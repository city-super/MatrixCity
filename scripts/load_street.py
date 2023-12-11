import argparse
import os
import json
import imageio
import numpy as np

def load_street(args):
    SCALE = args.scale
    STREET_BLOCK_NAME = args.block_name
    xmax,xmin,ymax,ymin = args.xmax,args.xmin,args.ymax,args.ymin
    
    os.makedirs(os.path.join('street/pose', STREET_BLOCK_NAME),exist_ok=True)
    street_dirs=[]
    base_path=os.path.join('street', args.set_type)
    street_files= os.listdir(base_path)
    for street_file in street_files:
        if not os.path.isfile(os.path.join(base_path,street_file)):
            street_dirs.append(street_file)
    
    all_frames=[]
    for street_dir in street_dirs:
        if 'outside' in street_dir:
            continue
        with open(os.path.join(base_path,street_dir,"transforms.json"), "r") as f:
            tj = json.load(f)
        
        for frame in tj['frames']:
            file_path = os.path.join("../..", args.set_type, street_dir, str(frame['frame_index']).zfill(4)+'.png')
            c2w = np.array(frame['rot_mat'])
            c2w[:3,:3] *= 100
            c2w[:3,3] /= SCALE
            if c2w[0,3] > xmin and c2w[0,3] < xmax and c2w[1,3] > ymin and c2w[1,3] < ymax:
                all_frames.append({'file_path':file_path,'transform_matrix':c2w.tolist()})
    
    angle_x = tj['camera_angle_x']
    w = float(1000)
    h = float(1000)
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
    
    save_dir = os.path.join('street/pose', STREET_BLOCK_NAME)
    with open(os.path.join(save_dir, 'transforms_{}.json'.format(args.set_type)),"w") as outfile:
        json.dump(pose, outfile, indent=2)
