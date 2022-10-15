# petals_local_parallel
YSDA project


## Benchmarking tutorial

1. Open benchmark.py, put your model in the cycle. 
2. run from console with ```CUDA_VISIBLE_DEVICES=4,5 torchrun --nproc_per_node 2 benchmark.py```
3. There are command line arguments: --do_backward: bool, --num_iter: int, --batch_size: int, 
and their short versions: -d, -n, -b

CUDA_VISIBLE_DEVICES -- gpus, you are using
nproc_per_node       -- # of gpus/ processes

So, for example, to run a benchmark with no backward, 100 iterations and batch_size of 128 objects 
one can write: 

``` CUDA_VISIBLE_DEVICES=4,5 torchrun --nproc_per_node 2 benchmark.py -d 0 -n 100 -b 128```

or ``` CUDA_VISIBLE_DEVICES=4,5 torchrun --nproc_per_node 2 benchmark.py --do_backward 0 --num_iter 100 --batch_size 128```
