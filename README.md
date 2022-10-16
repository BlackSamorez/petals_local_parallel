# petals_local_parallel
YSDA project


## Benchmarking tutorial

You may either use manual benchmark (```benchmark_manual.py```) or auto (```markbench.py```) 

#### Manual benchmark

consider command line arguments:

```-d | do_backward``` -- wether you need backward passes or not
```-n | num_iter ```   -- number of iterations
```-s | seq_length```  -- sequence length
```-b | batch_size```  -- okay
```-c | bloomconfig``` -- str used in BloomConfig().from_pretrained to specify the model you need

```CUDA_VISIBLE_DEVICES``` -- gpus, you are using
```nproc_per_node```       -- # of gpus/ processes

Don't forget to set correct gpu ids: ```export CUDA_DEVICE_ORDER=PCI_BUS_ID```

So the following command
``` CUDA_VISIBLE_DEVICES=4,5 torchrun --nproc_per_node 2 benchmark.py -d 0 -n 100 -s 17 -b 16 -c bloom ```
will run the manual benchmark with no backward pass, 100 iterations, sequence length of 17, batch size of 16 and "bloom" 176B model.


#### Auto benchmark

no command line arguments this time, just run ```markbench.py```

The script will run several experiments in cycle. To see the parameters, check the experiment setting section in the ```markbench.py```.
Models are tested both with and without backward passes. The results will be printed for all of the ranks. (MESS)

#### TODO:

- Implement smth to store the results into csv/ feather dataframe
- Decide which model are too big for backward passes and don't check them
- Decide what to do if one of the experiments failed
- test it



