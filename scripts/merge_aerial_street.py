import argparse
import os
import json
import imageio
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser(description="merge aerial and road json.")
    parser.add_argument("--high_name", type=str, default='aerial')
    parser.add_argument("--road_name", type=str, default='street')
    parser.add_argument("--out_name", type=str, default='aerial_street')
    args = parser.parse_args()
    return args


# TODO: fuse the train and test
if __name__ == "__main__":
    args = parse_args()
    HIGH_NAME = args.high_name
    ROAD_NAME = args.road_name
    OUT_NAME = args.out_name

    metas = {}
    # road_metas={}
    # assume all situations share the same intri
    with open(os.path.join(HIGH_NAME,f"transforms_train.json"), "r") as f:
        meta_high_train = json.load(f)
    high_angle_x = meta_high_train['camera_angle_x']
    high_fl_x = meta_high_train['fl_x']
    high_fl_y = meta_high_train['fl_y']
    high_cx = meta_high_train['cx']
    high_cy = meta_high_train['cy']
    high_w = meta_high_train['w']
    high_h = meta_high_train['h']
    
    with open(os.path.join(ROAD_NAME,f"transforms_train.json"), "r") as f:
        meta_road_train = json.load(f)
    road_angle_x = meta_road_train['camera_angle_x']
    road_fl_x = meta_road_train['fl_x']
    road_fl_y = meta_road_train['fl_y']
    road_cx = meta_road_train['cx']
    road_cy = meta_road_train['cy']
    road_w = meta_road_train['w']
    road_h = meta_road_train['h']
    
    train_json = {
        "camera_model": "SIMPLE_PINHOLE",
        "frames": []
        }

    test_json = {
        "camera_model": "SIMPLE_PINHOLE",
        "frames": []
    }
        
    
    split = ['train', 'test']
        
    data_type = ['high', 'road']

    for data in data_type:
        metas[data]={}
        for s in split:
            name = HIGH_NAME if data == 'high' else ROAD_NAME
            with open(
                    os.path.join(name,
                                 f"transforms_{s}.json"), "r") as f:
                metas[data][s] = json.load(f)

    for data in data_type:

        basedir = os.path.join("../", HIGH_NAME) if data == 'high' else os.path.join(
                                   "../", ROAD_NAME)
        camera_angle_x = high_angle_x if data=='high' else road_angle_x
        fl_x = high_fl_x if data=='high' else road_fl_x
        fl_y = high_fl_y if data=='high' else road_fl_y
        cx = high_cx if data=='high' else road_cx
        cy = high_cy if data=='high' else road_cy
        w = high_w if data=='high' else road_w
        h = high_h if data=='high' else road_h

        for s in split:
            meta = metas[data][s]
            for i, frame in enumerate(meta['frames']):
                fname = os.path.join(basedir, frame['file_path'])
                if s == "train":
                    train_json['frames'].append({
                        'camera_angle_x': camera_angle_x, 
                        'fl_x': fl_x,
                        'fl_y': fl_y,
                        'cx': cx,
                        'cy': cy,
                        'w': w,
                        'h': h,
                        'file_path':fname,
                        'transform_matrix':frame['transform_matrix']
                    })
                elif s == "test":
                    test_json['frames'].append({
                        'camera_angle_x': camera_angle_x, 
                        'fl_x': fl_x,
                        'fl_y': fl_y,
                        'cx': cx,
                        'cy': cy,
                        'w': w,
                        'h': h,
                        'file_path':fname,
                        'transform_matrix':frame['transform_matrix']
                    })
            
    # save
    save_dir = os.path.join(OUT_NAME)
    os.makedirs(save_dir,exist_ok=True)
    with open(os.path.join(save_dir, 'transforms_train.json'),"w") as outfile:
        json.dump(train_json, outfile, indent=2)
    with open(os.path.join(save_dir, 'transforms_test.json'),"w") as outfile:
        json.dump(test_json, outfile, indent=2)
  