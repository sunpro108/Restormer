CONFIG=$1

python -m torch.distributed.launch --nproc_per_node=4 --master_port=4321 train.py -opt $CONFIG --launcher pytorch