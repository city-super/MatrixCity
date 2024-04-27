import numpy as np
import argparse
import os
import json
import imageio
import cv2
import torch
import open3d as o3d
import pdb
os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"

def parse_args():
    parser = argparse.ArgumentParser(
        description="warp rgbd images to pc")

    parser.add_argument("--rgb_path",
                        type=str,
                        default='data/toy_utopia/rgb')
    
    parser.add_argument("--depth_path",
                        type=str,
                        default='data/toy_utopia/depth')

    parser.add_argument("--json_path",
                        type=str,
                        default='data/toy_utopia/transforms_1.json')
    
    parser.add_argument("--save_path",
                        type=str,
                        default='data/toy_utopia/merge/point_cloud')

    parser.add_argument("--ds", type=int, default=5)
    parser.add_argument("--ratio", type=int, default=1)
    parser.add_argument("--per_frame", action='store_true')
    parser.add_argument("--all_frames", action='store_true')
    parser.add_argument("--depth_cut", type=float, default=-1)

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    os.makedirs(args.save_path,exist_ok=True)
    os.makedirs(os.path.join(args.save_path,"per_frame"),exist_ok=True)
    # load c2ws and intrics
    with open(args.json_path, "r") as f:
        meta = json.load(f)
    cam_x = meta['camera_angle_x']
    frames = meta["frames"]
    cx = meta["cx"]/args.ds
    cy = meta["cy"]/args.ds
    w = int(meta["w"]/args.ds)
    h = int(meta["h"]/args.ds)
    fx = meta["fl_x"]/args.ds
    fy = meta["fl_y"]/args.ds
    c2ws = []
    for frame in frames:
        c2w=np.array(frame["transform_matrix"])
        c2w[3,3]=1
        c2ws.append(c2w.tolist()) 
    c2ws=np.stack(c2ws) #[B,4,4]

    # assume all images share the same intrinsic
    intrinsic = np.array([[fx,0,cx],[0,fy,cy],[0,0,1]])
    
    depths=[]
    rgbs=[]
    for i, frame in enumerate(frames):
        file_path = frame['file_path']
        rgb = cv2.imread(os.path.join(args.rgb_path,file_path))
        rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)
        rgb = cv2.resize(rgb, (w,h))
        depth = cv2.imread(os.path.join(args.depth_path,file_path.replace("png","exr")), cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)[...,0] / 10000. # cm -> 100m
        depth = cv2.resize(depth, (w,h))
        rgbs.append(rgb)
        depths.append(depth)
        
    rgbs = np.stack(rgbs) # [B,H,W,3]
    depths = np.stack(depths) # [B,H,W,1]
    # import pdb;pdb.set_trace()
    
    # convert to torch
    rgbs = torch.from_numpy(rgbs).float()
    depths = torch.from_numpy(depths).float()
    intrinsic = torch.from_numpy(intrinsic).float()
    c2ws = torch.from_numpy(c2ws).float()
    
    # project to world
    all_points = []
    all_colors = []
    # Compute the pixel coordinates of each point in the depth image
    for i in range(depths.shape[0]):
        y, x = torch.meshgrid([torch.arange(0, h, dtype=torch.float32, device=depths.device),
                            torch.arange(0, w, dtype=torch.float32, device=depths.device)])
        y, x = y.contiguous(), x.contiguous()
        y, x = y.view(h * w), x.view(h * w)
        xyz = torch.stack((x, y, torch.ones_like(x)))
        
        # if depth > thre, mask
        if args.depth_cut != -1:
            depth_mask = depths[i] < args.depth_cut
        else:
            depth_mask = torch.ones(depths[i].shape,dtype=torch.bool)
        
        # Convert pixel coordinates to camera coordinates
        inv_K = torch.inverse(intrinsic)
        cam_coords1 = inv_K.clone() @ (xyz.clone() * depths[i].reshape(-1))
        cam_coords1[1,:] = -cam_coords1[1,:]
        cam_coords1[2,:] = -cam_coords1[2,:]
        world_coords = (c2ws[i] @ torch.cat([cam_coords1, torch.ones((1, cam_coords1.shape[1]))], dim=0)).T
        world_coords = world_coords[:,:3]
        
        world_coords = world_coords[depth_mask.reshape(-1)]
        color = rgbs[i].reshape(-1,3)/255.
        color = color[depth_mask.reshape(-1)]
        
        all_points.append(world_coords)
        all_colors.append(color)
        
        if args.per_frame:
            final_pcd = o3d.geometry.PointCloud()
            final_pcd.points = o3d.utility.Vector3dVector(np.vstack(all_points[i]))
            final_pcd.colors = o3d.utility.Vector3dVector(np.vstack(all_colors[i]))
            o3d.io.write_point_cloud(os.path.join(args.save_path,"per_frame",f"{i}.ply"), final_pcd)
    
    if args.all_frames:
        merged_points = np.vstack(all_points)[::args.ratio,:]
        merged_colors = np.vstack(all_colors)[::args.ratio,:]

        # save the final point cloud
        final_pcd = o3d.geometry.PointCloud()
        final_pcd.points = o3d.utility.Vector3dVector(merged_points)
        final_pcd.colors = o3d.utility.Vector3dVector(merged_colors)
        o3d.io.write_point_cloud(os.path.join(args.save_path,"all.ply"), final_pcd)
