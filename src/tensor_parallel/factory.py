import logging
from typing import Optional, Sequence, Union

import torch
import torch.distributed
from torch import nn
from transformers import PreTrainedModel

from tensor_parallel.pretrained_model import TensorParallelPreTrainedModel
from tensor_parallel.sharding import Sharded
from tensor_parallel.slicer_wrapper import Config
from tensor_parallel.tensor_parallel import TensorParallel

logger = logging.getLogger(__file__)


def tensor_parallel(
    module: nn.Module,
    device_ids: Optional[Sequence[Union[torch.device, str]]] = None,
    config: Optional[Config] = None,
    distributed: Optional[bool] = None,
    sharded: Optional[bool] = None,
    sharded_param_names: Optional[bool] = None,
    **kwargs
) -> nn.Module:
    """
    Wrap an existing PyTorch module with tensor parallelism. Return equivalent tensor-parallel module.

    :example:

    >>> import torch, transformers
    >>> import tensor_parallel as tp
    >>> model = transformers.AutoModel.from_pretrained("t5-11b")
    >>> model = tp.tensor_parallel(model, device_ids=['cuda:0', 'cuda:1'])
    >>> outputs_as_usual = model(**inputs_as_usual)  # backprop also works!

    :param module: original PyTorch module. We recommend storing input module on CPU to minimize GPU memory
    :param device_ids: model will be split among this list of devices (e.g. GPUs), default = all available CUDA devices
    :param config: custom tensor_parallel.Config to describe how the model is parallelized. defaults to auto config
    :param distributed: if True, use torch.distributed instead of threading. Assumes that we is running in torchrun
       defaults to True if torch.distributed.is_initialized, else False
    :param sharded: if True, any non-tensor-parallel parameters (e.g. layernorm weight) will still be sharded,
       and manually re-assembled for each forward. This is equivalent to pytorch FullyShardedDataParallel
    :param sharded_param_names: if sharded=True, this is a list of all parameter names (strings) that ZeRO-3 applies to;
       by default, ZeRO-3 applies to all parameters that are not split with tensor parallelism.
    :note: the default sharded_param_names are formed of parameters that are equal between shards after TP is applied
    :param kwargs: additional keyword arguments passed to TensorParallel init

    """
    distributed = distributed if distributed is not None else torch.distributed.is_initialized()
    if distributed:
        if device_ids is None:
            device_ids = [torch.device("cuda" if torch.cuda.is_available() else "cpu")]
        assert len(device_ids) == 1, "if distributed=True, please specify a single (current) device"
        assert not sharded, "distributed + sharded mode is not implemented, please keep one"
        if config is None:
            config = Config.get_default_config(module, device_ids=range(torch.distributed.get_world_size()))
            logger.info("Using automatic config: sharding individual linear/conv/emb layers")

        return config.make_distributed_shard(module, device=torch.device(device_ids[0]), **kwargs)
    else:
        if sharded is None:
            sharded = any(p.requires_grad for p in module.parameters())
            if sharded:
                logger.warning("Using ZeRO-3 sharding for remaining parameters")
        if isinstance(module, PreTrainedModel):
            module = TensorParallelPreTrainedModel(module, device_ids=device_ids, config=config, **kwargs)
            if sharded:
                module.tensor_parallel = Sharded(module.tensor_parallel, sharded_param_names=sharded_param_names)
        else:
            module = TensorParallel(module, device_ids=device_ids, config=config, **kwargs)
            if sharded:
                module = Sharded(module, sharded_param_names=sharded_param_names)
        return module
