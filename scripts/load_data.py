import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"
import cv2
import numpy as np

def load_depth(depth_path, is_float16=True):
    image = cv2.imread(depth_path, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)[...,0] #(H, W)
    if is_float16==True:
        invalid_mask=(image==65504)
    else:
        invalid_mask=None
    image = image / 10000 # cm -> 100m
    return image, invalid_mask

def load_normal(normal_path):
    image = cv2.imread(normal_path, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)[..., :3] * 2. - 1. #(H, W, 1)
    invalid_mask=np.all(image==[-1, -1, -1], axis=-1)
    image /= np.linalg.norm(image,axis=-1,keepdims=True)
    image[...,1]*=-1
    return image, invalid_mask
