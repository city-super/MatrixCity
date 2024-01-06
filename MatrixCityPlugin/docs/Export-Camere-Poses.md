# Export Camera Poses

## 1. Install `Blender`
## 2. Export camera poses from UE project
- Right click on the cine camera actor of the sequence and select `Export...`.
![UE_camera_pose_1](figures/UE_camera_pose_1.png)

- There is no need to modify the settings, just select `Export`.
![UE_camera_pose_2](figures/UE_camera_pose_2.png)

- Read the index `N` of the last frame from the sequence or from the rendered image. For the following example, `N` is 329
![UE_camera_pose_3](figures/UE_camera_pose_3.png)

## 3. Transform camera poses in Blender
- Double-click [pose.blend](../../scripts/pose.blend) to open it in Blender.
![UE_camera_pose_1](figures/Blender_camera_pose_1.png)

- Import the fbx file exported from UE.
![UE_camera_pose_2](figures/Blender_camera_pose_2.png)

- If you import successfully, you will see `Cine_Camera_Actor`.
![UE_camera_pose_3](figures/Blender_camera_pose_3.png)

- Select `Layout` to change the `End` with `N+1` (`N` is the index of the last frame of the sequence).
![UE_camera_pose_4](figures/Blender_camera_pose_4.png)
![UE_camera_pose_5](figures/Blender_camera_pose_5.png)

- Select `Script` and change the `fp` to your local directory.
![UE_camera_pose_6](figures/Blender_camera_pose_6.png)

- Select `Cine_Camera_Actor` and then click the `Run` icon. `transforms.json` will be saved in `fp`. The unit of position is m. And the rotaton matrix needs to be multiplied by 100 to normalize it. You can use [generate_split.py](../../scripts/generate_split.py) to generate files for training. 
![UE_camera_pose_7](figures/Blender_camera_pose_7.png)