import argparse
import os
import json
import imageio
import numpy as np

def load_aerial(args):
    AERIAL_BLOCK_NAME = args.block_name
    SCALE = args.scale
    xmax,xmin,ymax,ymin = args.xmax,args.xmin,args.ymax,args.ymin

    os.makedirs(os.path.join('aerial/pose', AERIAL_BLOCK_NAME), exist_ok=True)

    base_path=os.path.join('aerial', args.set_type)
    all_frames=[]

    if AERIAL_BLOCK_NAME=='block_A':
        if args.set_type=='train':
            block_names=['block_1', 'block_2']
        else:
            block_names=['block_1_test', 'block_2_test']
        
        for block_name in block_names:
            with open(os.path.join(base_path, block_name, "transforms.json"), "r") as f:
                tj = json.load(f)

            for frame in tj['frames']:
                file_path = os.path.join("../..", args.set_type, block_name, str(frame['frame_index']).zfill(4)+'.png')
                c2w = np.array(frame['rot_mat'])
                c2w[:3,:3] *= 100
                c2w[:3,3] /= SCALE
                all_frames.append({'file_path':file_path,'transform_matrix':c2w.tolist()})

    elif AERIAL_BLOCK_NAME=='block_B' or AERIAL_BLOCK_NAME=='block_C':
        if args.set_type=='train':
            block_names=['block_3','block_4','block_5','block_6','block_7','block_8']
        else:
            block_names=['block_3_test','block_4_test','block_5_test','block_6_test','block_7_test','block_8_test']
        for block_name in block_names:
            with open(os.path.join(base_path, block_name, "transforms.json"), "r") as f:
                tj = json.load(f)
            for frame in tj['frames']:
                file_path = os.path.join("../..", args.set_type, block_name, str(frame['frame_index']).zfill(4)+'.png')
                # file_path = os.path.join("../..", block_name, args.set_type, str(frame['frame_index']).zfill(4)+'.png')
                c2w = np.array(frame['rot_mat'])
                c2w[:3,:3] *= 100
                c2w[:3,3] /= SCALE
                if c2w[0,3] > xmin and c2w[0,3] < xmax and c2w[1,3] > ymin and c2w[1,3] < ymax:
                    all_frames.append({'file_path':file_path,'transform_matrix':c2w.tolist()})

    elif AERIAL_BLOCK_NAME=='block_D':
        if args.set_type=='train':
            block_name='block_9'
        else:
            block_name='block_9_test'
     
        with open(os.path.join(base_path, block_name, "transforms.json"), "r") as f:
            tj = json.load(f)

        for frame in tj['frames']:
            file_path = os.path.join("../..", args.set_type, block_name, str(frame['frame_index']).zfill(4)+'.png')
            c2w = np.array(frame['rot_mat'])
            c2w[:3,:3] *= 100
            c2w[:3,3] /= SCALE
            all_frames.append({'file_path':file_path,'transform_matrix':c2w.tolist()})
    
    elif AERIAL_BLOCK_NAME=='block_E':
        if args.set_type=='train':
            block_name='block_10'
        else:
            block_name='block_10_test'
     
        with open(os.path.join(base_path, block_name, "transforms.json"), "r") as f:
            tj = json.load(f)

        for frame in tj['frames']:
            file_path = os.path.join("../..", args.set_type, block_name, str(frame['frame_index']).zfill(4)+'.png')
            c2w = np.array(frame['rot_mat'])
            c2w[:3,:3] *= 100
            c2w[:3,3] /= SCALE
            all_frames.append({'file_path':file_path,'transform_matrix':c2w.tolist()})
    
    elif AERIAL_BLOCK_NAME=='block_all':
        if args.set_type=='train':
            block_names=['block_1', 'block_2', 'block_3', 'block_4', 'block_5', 'block_6', 'block_7', 'block_8', 'block_9', 'block_10']
        else:
            block_names=['block_1_test', 'block_2_test', 'block_3_test', 'block_4_test', 'block_5_test', 'block_6_test', 'block_7_test', 'block_8_test', 'block_9_test', 'block_10_test']
        
        for block_name in block_names:
            with open(os.path.join(base_path, block_name, "transforms.json"), "r") as f:
                tj = json.load(f)

            for frame in tj['frames']:
                file_path = os.path.join("../..", args.set_type, block_name, str(frame['frame_index']).zfill(4)+'.png')
                c2w = np.array(frame['rot_mat'])
                c2w[:3,:3] *= 100
                c2w[:3,3] /= SCALE
                all_frames.append({'file_path':file_path,'transform_matrix':c2w.tolist()})
    
    angle_x = tj['camera_angle_x']
    w = float(1920)
    h = float(1080)
    fl_x = float(.5 * w / np.tan(.5 * angle_x))
    fl_y = fl_x
    k1 = 0
    k2 = 0
    k3 = 0
    k4 = 0
    p1 = 0
    p2 = 0
    cx = w / 2
    cy = h / 2
    
    pose = {
            "camera_angle_x": angle_x,
            "fl_x": fl_x,
            "fl_y": fl_y,
            "k1": k1,
            "k2": k2,
            "k3": k3,
            "k4": k4,
            "p1": p1,
            "p2": p2,
            "cx": cx,
            "cy": cy,
            "w": w,
            "h": h,
            "frames": all_frames
        }
    
    save_dir = os.path.join('aerial/pose', AERIAL_BLOCK_NAME)
    with open(os.path.join(save_dir, 'transforms_{}.json'.format(args.set_type)),"w") as outfile:
        json.dump(pose, outfile, indent=2)
