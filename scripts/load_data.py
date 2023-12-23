import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"
import cv2
import numpy as np

def load_depth(depth_path):
    image = cv2.imread(depth_path, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)[...,0] #(H, W)
    image = image / 10000 # cm -> 100m
    return image

def load_normal(normal_path):
    image = cv2.imread(normal_path, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)[..., :3] * 2. - 1. #(H, W, 1)
    image /= np.linalg.norm(image,axis=-1,keepdims=True)
    image[...,1]*=-1
    return image

if __name__ == '__main__':
    depth_path = os.path.join('depth_0000.exr')
    depth_image = load_depth(depth_path)[...,None]
    print(depth_image.shape)
    
    normal_path = os.path.join('normal_0000.exr')
    normal_image = load_normal(normal_path)
    print(normal_image.shape)
