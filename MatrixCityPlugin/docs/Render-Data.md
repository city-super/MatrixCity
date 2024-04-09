# Render Data

## Preparation
- **Camera trajectory**: You can use the provided trajectories in folder [MatrixCitySequence](../../MatrixCitySequence) or you own generated trajectory. Please put this folder under the folder `CitySample\Content`.
![Sequence](figures/Sequence.png)

- **Rendering config**: You can use the provided config in folder [MatrixCityRenderConfig](../../MatrixCityRenderConfig). Please copy these uassets into folder `CitySample\Content\Cinematics`. Ortherwise the engine cannot find these uassets.  
![RenderConfig](figures/RenderConfig.png)

## Proejct Setting
The primary aim of the MatrixCity v0.1.0 dataset is to study the core challenges of city-scale neural rendering. To facilitate this, we disabled the directional light, sun dome, fog, and human and car crowds, resulting in a static scene. The environmental settings in our paper are as follows. You can also modify these settings to generate data that meets your requirements.

- Light: 
    - Search `light` in `Outliner`, including sky light and directional light.
    ![Search_light](figures/Search_light.png)

    - In our paper, we set the directional light invisible, ie. `Visible` as False.
    ![Invisible_directional_light](figures/Invisible_directional_light.png)

    - In your work, you can set the directional light visible. After selecting the asset, you can adjust the light intensity, angle, color and so on for both sky light and directional light in the `Details` panel.
    ![Adjust_light](figures/Adjust_light.png)

- Sun dome: 
    - Search `sun` in `Outliner`
    ![Search_sun](figures/Search_sun.png)

    - In our paper, we set the sun invisible to to avoid some overexposure situations, ie. `Visible` as False. Note that never set the dome to invisible.
    ![Invisible_sun](figures/Invisible_sun.png)
    - In your work, you can set the sun visible.

- Fog: 
    - Search `fog` in `Outliner`
    ![Search_fog](figures/Search_fog.png)

    - In our paper, we set the fog invisible, ie. `Visible` as False.
    ![Invisible_fog](figures/Invisible_fog.png)

    - In your work, you can set the fog visible. After selecting the asset, you can adjust the fog's density, height and so on in the `Details` panel.
    ![Adjust_fog](figures/Adjust_fog.png)

- Human and Car crowds: 
    - Search `spawn` in `Outliner`, including `BP_MassCrowdSpawner` (number of moving pedestrians), `BP_MassTrafficParkedVehichleSpawner`(number of static parked cars), and `BP_MassTrafficVehicleSpwaner`(number of moving cars).
    ![Search_spawn](figures/Search_spawn.png)

    - In our paper, we set the `count` of `BP_MassCrowdSpawner`, `BP_MassTrafficVehicleSpwaner` and `BP_MassTrafficParkedVehichleSpawner` to 0 in the `Details` panel, resulting a static scene.
    ![Crowd_0](figures/Crowd_0.png)
    ![Car_0](figures/Car_0.png)
    ![Car_1](figures/Car_1.png)

    - In your work, after selecting the asset, you can adjut the count of moving pedestrians, static parked cars and moving cars in the `Details` panel to simulate the real-world dynamic scenes.

- PostProcessVolume: 
    - Search `post` in `Outliner`, including `PostProcessVolume_Sandbox_only`, `PostProcessVolumePostToggle_Sandbox_only` and `PostProcessVolume_WP`.
    ![Search_post](figures/Search_post.png)

    - In our work, we set the `Vignette Intensity` of `PostProcessVolume_Sandbox_only`, `PostProcessVolumePostToggle_Sandbox_only` and `PostProcessVolume_WP` to 0.0 in the `Details` panel for appearance consistency. `Vignette` is an effect that simulates the darkening in real-world camera lenses. High quality lens try to compensate for this effect. The effect is mostly noticeable near the edges of the image. Please refer to [vignette](https://docs.unrealengine.com/4.27/en-US/RenderingAndGraphics/PostProcessEffects/Vignette/) for more details.
    ![Sandbox_only](figures/Sandbox_only.png)
    ![PostToggle_Sandbox_only](figures/PostToggle_Sandbox_only.png)
    ![WP](figures/WP.png)

    - In your work, if you want to simulate this camera imperfection, you can adjust this value for the relevant camera in the `Details` panel.
    ![Camera_vignette](figures/Camera_vignette.png)

## Render
### 1. Double click the camera trajectory uasset to enter the sequence.
![Into_sequence](figures/Into_sequence.png)
![In_sequence](figures/In_sequence.png)

### 2. Select the newest Movie Render Queue version and click this icon to render images.
![Select_MVQ_version](figures/Select_MVQ_version.png)

### 3. Click the icons below to select the render config you want.
![Select_config](figures/Select_config.png)

### 4. You can control the rendering pass in the section `Exports`. Our default rendering config only enable `rgb`, `depth` and `normal` pass. You can enable other passes you want. You can also control the output format by changing `Extension` of each path. **Note that output of exr format is in the linear space and output of png format is in the sRGB space, which needs gamma correction for mutual conversion.**
![Select_render_pass](figures/Select_render_pass.png)

### 5. You can control the output directory, output name format, and output resolution in the section `Output`. **After finishing setting the render config, remember to click the `Accept` icon.**
![Select_output_setting](figures/Select_output_setting.png) 

### 6. (Optional) If you change the config file provided, you can click this icon to create your own config file, which is saved in folder `CitySample/Content/Cinematics`.
![Save_config](figures/Save_config.png)

### 7. Click the `Render(local)` icon to render the images. **Note that the first running requires compiling the shaders, which will take a long time. Just wait patiently.** Output will be saved in the folder you specify in the render config. 
![render](figures/render.png)

## Extra

### Camera aspect ratio:
The default camera aspect ratio is 16:9. If your output resolution is not this ratio, you should set `Constrain Aspect Ratio` as False in the `Details` panel after selecting the cine camera actor. We have changed this setting in our provided camera trajectories of street view. Please note that you need to change this setting for your own generated trajectories, whose output resolution ratio is not 16:9.
![Set_constrain](figures/Set_constrain.png)

### Depth:
#### 1. To achieve the highest possible image quality, we use anti-aliasing during the rendering process. This will make the edges of the depth smooth and brings noises when converting depth into poing cloud. Please refer to [Noise in depth gt](https://github.com/city-super/MatrixCity/issues/4#issuecomment-1774054407) for more details. We only provide the depth map rendered with anti-alias. 

>If you want to use the depth map to guide reconstruction, depth map rendered with anti-alias is more suitable because rgb is also rendered with anti-alias. You can download our provided depth map.

>If you want to extract geometry from depth map, you should rendered without anti-alias. You just change the `Spatial Sample Count` from `8` to `1` in rendering config file to disable the anti-alias.
![Set_anti_alias](figures/Set_anti_alias.png)

#### 2. The default data type for the EXR file is float16, which can represent a maximum value of 65504, and the precision decreases as it approaches this maximum value. float16 is reasonable for depth maps of street views, but many depth maps of aerial views exceed this range, necessitating the use of float32 precision. You can set the `Use 32Bit Post Process Materials` as True in rendering config file to save depth map in float32 format.
![Set_float32](figures/Set_float32.png)