"""
The TensorParallel module wrapper for Hugging Face PreTrainedModel
"""
import logging
from typing import Any, Optional, Sequence, Union, Dict

import torch

import transformers
from transformers import PreTrainedModel

from tensor_parallel.slicer_wrapper import Config
from tensor_parallel.tensor_parallel import TensorParallel

logger = logging.getLogger(__file__)


class TensorParallelPreTrainedModel(PreTrainedModel):
    def __init__(
        self,
        module: PreTrainedModel,
        device_ids: Optional[Sequence[torch.device]] = None,
        output_device: Optional[torch.device] = None,
        output_device_index: Optional[int] = None,
        config: Optional[Config] = None,
    ):
        super().__init__(module.config)  # Temporary empty config. Gets replaced in from_pretrained
        self.tensor_parallel = TensorParallel(module, device_ids, output_device, output_device_index, config)

    def forward(self, *args, **kwargs):
        return self.tensor_parallel(*args, **kwargs)

    def _validate_model_class(self):
        return self.tensor_parallel.module_shards[0]._validate_model_class()

    def _validate_model_kwargs(self, model_kwargs: Dict[str, Any]):
        return self.tensor_parallel.module_shards[0]._validate_model_kwargs(model_kwargs)

    def prepare_inputs_for_generation(self, *args, **kwargs):
        return self.tensor_parallel.module_shards[0].prepare_inputs_for_generation(*args, **kwargs)

    def _reorder_cache(self, past, beam_idx):
        for shard in self.tensor_parallel.module_shards:
            shard._reorder_cache(past, beam_idx)
