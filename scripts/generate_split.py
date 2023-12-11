import argparse
import os
import json
import imageio
import numpy as np
from load_aerial import load_aerial
from load_street import load_street


def parse_args():
    parser = argparse.ArgumentParser(
        description="generate train/test json.")
    
    parser.add_argument("--scale", type=float, default=100)

    parser.add_argument("--dataset_type",type=str, default='aerial', 
                        help='options: aerial / street')
    
    parser.add_argument("--block_name", type=str, default='block_A')
    parser.add_argument("--set_type",type=str, default='train', 
                        help='options: train / train_dense / test')
    parser.add_argument("--xmax", type=float, default=-1.2)
    parser.add_argument("--xmin", type=float, default=-10.)
    parser.add_argument("--ymax", type=float, default=0)
    parser.add_argument("--ymin", type=float, default=-6.3)

    args = parser.parse_args()
    return args



if __name__ == "__main__":
    args = parse_args()
    
    DATASET_TYPE=args.dataset_type
    
    if DATASET_TYPE == 'aerial':
        load_aerial(args)
    elif DATASET_TYPE == 'street':
        load_street(args)
    
    
