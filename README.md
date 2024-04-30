# MatrixCity
**MatrixCity: A Large-scale City Dataset for City-scale Neural Rendering and Beyond.**

[Yixuan Li](https://yixuanli98.github.io/), [Lihan Jiang](https://jianglh-whu.github.io/), [Linning Xu](https://eveneveno.github.io/lnxu/), [Yuanbo Xiangli](https://kam1107.github.io/), [Zhenzhi Wang](https://zhenzhiwang.github.io/), [Dahua Lin](http://dahua.site/), [Bo Dai](https://daibo.info/)

The Chinese University of Hong Kong, Shanghai AI Laboratory

[[`Paper`](https://arxiv.org/abs/2309.16553)] 
[[`Project Page`](https://city-super.github.io/matrixcity/)]

![teaser](figures/teaser.png)

# Release

**Apr. 2024 - Update the script for extracting point clouds from several rgb-depth pairs at [rgbd2pc.py](scripts/rgbd2pc.py), which can be used as the initialization of [3DGS](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/).**

**Apr. 2024 - Release depth maps of aerial data in float32 format on Hugging Face and Baidu Netdisk. Update the scripts for loading depth and normal maps.**
- We recommand that using the depth maps in float32 format for aerial views because the default for EXR is float16, which can represent up to 65504cm and does not effectively represent the depth for aerial views.
- Add checks for invalid masks in the scripts including the sky and content exceeding the maximum depth range.

**Feb. 2024 - Release diffuse, metallic, roughness and specular of Small City on Hugging Face and Baidu Netdisk**

**Jan. 2024 - Release depth maps of Big City**

**Dec. 2023 - V1.0.1 MatrixCityPlugin Released**
- Documentation on using our plugins to collect custom data. 
- Render configs and sequences used in our paper.
- Related useful scripts.

**Oct. 2023 - Attend ICCV 2023 Conference.**

**Sep. 2023 - MatrixCity Dataset Released.**

# Data Download

We provide three ways to download our MatrixCity dataset.

**Hugging Face**: https://huggingface.co/datasets/BoDai/MatrixCity/tree/main

**Openxlab**: https://openxlab.org.cn/datasets/bdaibdai/MatrixCity

**Baidu Netdisk**: https://pan.baidu.com/s/187P0e5p1hz9t5mgdJXjL1g#list/path=%2F (password: hqnn)


# Data Color Space

We output depth and normal maps in EXR format, while RGB, diffuse, specular, roughness, and metallic are output in PNG format. All files in EXR format are in linear space, and all images in PNG format are in sRGB space. Please use [gamma correction](https://en.wikipedia.org/wiki/Gamma_correction) for conversion.

# Depth and Normal Map Note

- Our depth maps are **Z-depth**, which refers to the distance between a point in the 3D space and the camera along the Z-axis, which is aligned with the camera's direction of view. 

- Our depth maps are rendered with anti-aliasing settings to align with RGB images. However, this may result in artifacts when converting depth maps to point clouds, as discussed in the [issue#4](https://github.com/city-super/MatrixCity/issues/4). We provide the guidance to render depth maps without anti-alias in [Render Data/Depth-1](https://github.com/city-super/MatrixCity/blob/main/MatrixCityPlugin/docs/Render-Data.md#depth).
- The depth maps are in EXR format, which defaults to float16 data type with a maximum range of 65504. For depth maps, this means the farthest distance that can be expressed is 65504 cm, so we recommend using the depth maps in float32 format for aerial views. We provide the guidance to export EXR files in float32 format in [Render Data/Depth-2](https://github.com/city-super/MatrixCity/blob/main/MatrixCityPlugin/docs/Render-Data.md#depth). Also we provide code in [load_data.py](scripts/load_data.py) to identify the invalid part of depth maps in float16 precision.
- The normal maps of the sky portion are invalid, and we provide code in [load_data.py](scripts/load_data.py) to identify the invalid masks.


# Export Point Clouds

Please refer to [rgbd2pc.py](https://github.com/city-super/MatrixCity/blob/main/scripts/rgbd2pc.py) to extract point clouds from several rgb-depth pairs ‼️ The generated point clouds can be used as the initialization of [3DGS](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/).

# Pose File Structure

We use the same pose coordinate system as original [NeRF repo](https://github.com/bmild/nerf): the local camera coordinate system of an image is defined in a way that the X axis points to the right, the Y axis upwards, and the Z axis backwards as seen from the image.

- **camera_angle_x**: The fov (field of view) of horizontal direction. The unit is radian but not angle.
- **fl_x**: The focal length of the image. The unit is pixel.
- **fl_y**: This is a copy of fl_x.
- **w**: The width of the image. The unit is pixel.
- **h**: The height of the image. The unit is pixel.
- **frames**:
  - **file_path**: The relative path of the image in the MatrixCity directory structure.
  - **transform_matrix**: Poses are stored as $4 \times 4$ numpy arrays that represent camera-to-world transformation matrices. The last row of the matrix is ​​padding and has no other meaning.



# Data Structure

- **small_city**: Small City Map ($2.7km^2$) data.
  - **aerial**: Aerial-view data.
    - **train**: Training set data.
      - **\<block\>**: The unit of position is m. And the rotation matrix needs to be multiplied by 100 to normalize it. 
        - **transforms_origin.json:** Poses of all original collected images.
        - **transforms.json:** Poses of images after removing the images that look outside the map boundary, which are used for training and testing.
      - **\<block\>.tar:** Contain PNG images. Please unzip this file into corresponding directory **\<block\>**.
    - **test**:  Test set data.
    - **pose/<block_name>**: Data splits and pose used in our paper. The unit of position is 100m and the rotation matrix has already been normalized. Please refer to **scripts/generate\_split.py** to generate train/test splits for custom block.
  - **street**: Street-view data.
    - **train**: Training set data. The collection interval is 5m.
      - **\<block\>**: The unit of position is m. And the rotation matrix needs to be multiplied by 100 to normalize it.
        - **transforms_origin.json:** Poses of all original collected images.
        - **transforms.json:** Poses of images after removing the images that look straight down following, which are used for training and testing.
      - **\<block\>.tar:** Contain PNG images. Please unzip this file into corresponding directory **\<block\>**.
    - **train_dense**: Training dense set data. The collection interval is 1m.
    - **test**:  Test set data.
    - **pose/\<block_name\>**: Data splits and pose used in our paper. The unit of position is 100m and the rotation matrix has already been normalized. Please refer to **scripts/generate\_split.py** to generate train/test splits for custom block.
- **big_city**: Big City Map ($25.3km^2$) data, which has a similar file structure to the **small_city** directory.
- **big_city_depth**: Depth data in float16 format for the Big City Map which shares the same camera poses as the **big_city** directory. The unit is cm. Please load it with **scripts/load_data.py**. Note that our depth maps are **Z-depth**.
- **big_city_depth_flaot32**: Depth data in float32 format for the Big City Map which shares the same camera poses as the **big_city** directory. The unit is cm. Please load it with **scripts/load_data.py**. Note that our depth maps are **Z-depth**.
- **aerial_street_fusion**: The aerial and street data of the same area, used in our paper's Section 4.5. Please refer to **scripts/merge\_aerial\_street.py** to merge custom data of aerial and street modality with different resolutions and focals.
- **small_city_depth**: Depth data in float16 format for the Small City Map which shares the same camera poses as the **small_city** directory. The unit is cm. Please load it with **scripts/load_data.py**. Note that our depth maps are **Z-depth**.
- **small_city_depth_float32**: Depth data in float32 format for the Small City Map which shares the same camera poses as the **small_city** directory. The unit is cm. Please load it with **scripts/load_data.py**. Note that our depth maps are **Z-depth**.
- **small_city_normal**: Normal data for the Small City Map which shares the same camera poses as the **small_city** directory. Please load it with **scripts/load_data.py**.
- **small_city_diffuse**: Diffuse data for the Small City Map which shares the same camera poses as the **small_city** directory.
- **small_city_metallic**: Metallic data for the Small City Map which shares the same camera poses as the **small_city** directory.
- **small_city_roughness**: Roughness data for the Small City Map which shares the same camera poses as the **small_city** directory.
- **small_city_specular**: Specular data for the Small City Map which shares the same camera poses as the **small_city** directory.


# MatrixCityPlugin
Our plugin is developed based on the v0.1.0 version of [xrfeitoria](https://github.com/openxrlab/xrfeitoria/tree/v0.1.0). Thank [Haiyi Mei](https://haiyi-mei.com/) and [Lei Yang](https://scholar.google.com.hk/citations?user=jZH2IPYAAAAJ&hl=en) for
their invaluable help and discussions for the plug-in development.
> It leverages [Unreal Engine 5.0.3](https://www.unrealengine.com/) to automatically collect large-scale and high-quality city data from [City Sample project](https://www.unrealengine.com/marketplace/product/city-sample).
>
> Allowing researchers to flexibly control lighting, weather, and transient objects.
>
> Using this to generate synthetic data including rgb, depth, normal map, decomposed BRDF materials etc.
>
> General camera noises like motion blur and defocus blur can be simulated in UE5.
>
> This plugin is relied on the [Movie Render Queue](https://docs.unrealengine.com/5.0/en-US/render-cinematics-in-unreal-engine/) plugin, and is python-friendly.

## Installation

Please see [Get-Started](MatrixCityPlugin/docs/Get-Started.md) for plugin setup.

## Generate custom trajectories

Please see [Generate-Trajectory](MatrixCityPlugin/docs/Generate-Trajectory.md) to generate custom trajectories.

 We have provided the trajectories of Small City and Big City used in our dataset in folder [MatrixCitySequence](MatrixCitySequence). If you only want to render your own data under different environmental settings based on the provided trajectories, you can skip this part. 

## Render custom data

Please see [Render-Data](MatrixCityPlugin/docs/Render-Data.md) to render custom data after getting camera trajectories (Provided / Custom).

## Export camera poses

Please see [Export-Camere-Poses](MatrixCityPlugin/docs/Export-Camere-Poses.md) to export camera trajectories from UE to `transforms.json`.

## Code Details

We also provide some code details for your convenience in [Code-Details](MatrixCityPlugin/docs/Code-Details.md).

# Citation

```
@inproceedings{li2023matrixcity,
  title={MatrixCity: A Large-scale City Dataset for City-scale Neural Rendering and Beyond},
  author={Li, Yixuan and Jiang, Lihan and Xu, Linning and Xiangli, Yuanbo and Wang, Zhenzhi and Lin, Dahua and Dai, Bo},
  booktitle={Proceedings of the IEEE/CVF International Conference on Computer Vision},
  pages={3205--3215},
  year={2023}
}
```
