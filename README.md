# MatrixCity
**MatrixCity: A Large-scale City Dataset for City-scale Neural Rendering and Beyond.**

[Yixuan Li](https://yixuanli98.github.io/), [Lihan Jiang](https://jianglh-whu.github.io/), [Linning Xu](https://eveneveno.github.io/lnxu/), [Yuanbo Xiangli](https://kam1107.github.io/), [Zhenzhi Wang](https://zhenzhiwang.github.io/), [Dahua Lin](http://dahua.site/), [Bo Dai](https://daibo.info/)

The Chinese University of Hong Kong, Shanghai AI Laboratory

[[`Paper`](https://arxiv.org/abs/2309.16553)] 
[[`Project Page`](https://city-super.github.io/matrixcity/)]

![teaser](figures/teaser.png)

# Release

**Jan. 2024 - Release depth maps of Big City**

**Dec. 2023 - V1.0.1 MatrixCityPlugin Released**
- Documentation on using our plugins to collect custom data. 
- Render configs and sequences used in our paper.
- Related useful scripts.

**Oct. 2023 - Attend ICCV 2023 Conference.**

**Sep. 2023 - MatrixCity Dataset Released.**

# Data Download

We provide three ways to download our MatrixCity dataset. We use the same pose coordinate system as original [NeRF repo](https://github.com/bmild/nerf): the local camera coordinate system of an image is defined in a way that the X axis points to the right, the Y axis upwards, and the Z axis backwards as seen from the image.

**Hugging face**: https://huggingface.co/datasets/BoDai/MatrixCity/tree/main

**Openxlab**: https://openxlab.org.cn/datasets/bdaibdai/MatrixCity

**Baidu Wangpan**: https://pan.baidu.com/s/187P0e5p1hz9t5mgdJXjL1g#list/path=%2F (password: hqnn)

# Data Structure

- **small_city**: Small City Map ($2.7km^2$) data.
  - **aerial**: Aerial-view data.
    - **train**: Training set data.
      - **\<block\>**: The unit of position is m. And the rotaton matrix needs to be multiplied by 100 to normalize it. 
        - **transforms_origin.json:** Poses of all original collected images.
        - **transforms.json:** Poses of images after removing the images that look outside the map boundary, which are used for training and testing.
      - **\<block\>.tar:** Contain PNG images. Please unzip this file into corresponding directory **\<block\>**.
    - **test**:  Test set data.
    - **pose/<block_name>**: Data splits and pose used in our paper. The unit of position is 100m and the rotaton matrix has already been normalized. Please refer to **scripts/generate\_split.py** to generate train/test splits for custom block.
  - **street**: Street-view data.
    - **train**: Training set data. The collection interval is 5m.
      - **\<block\>**: The unit of position is m. And the rotaton matrix needs to be multiplied by 100 to normalize it.
        - **transforms_origin.json:** Poses of all original collected images.
        - **transforms.json:** Poses of images after removing the images that look straight down following, which are used for training and testing.
      - **\<block\>.tar:** Contain PNG images. Please unzip this file into corresponding directory **\<block\>**.
    - **train_dense**: Training dense set data. The collection interval is 1m.
    - **test**:  Test set data.
    - **pose/\<block_name\>**: Data splits and pose used in our paper. The unit of position is 100m and the rotaton matrix has already been normalized. Please refer to **scripts/generate\_split.py** to generate train/test splits for custom block.
- **big_city**: Big City Map ($25.3km^2$) data, which has a similar file structure to the **small_city** directory.
- **aerial_street_fusion**: The aerial and street data of the same area, used in our paper's Section 4.5. Please refer to **scripts/merge\_aerial\_street.py** to merge custom data of aerial and street modality with different resolutions and focals.
- **small_city_depth**: Depth data for the Small City Map which shares the same camera poses as the **small_city** directory. The unit is cm. Please load it with **scripts/load_data.py**.
- **small_city_normal**: Normal data for the Small City Map which shares the same camera poses as the **small_city** directory. Please load it with **scripts/load_data.py**.

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

##  Generate custom trajectories

Please see [Generate-Trajectory](MatrixCityPlugin/docs/Generate-Trajectory.md) to generate custom trajectories.

 We have provided the trajectories of Small City and Big City used in our dataset in folder [MatrixCitySequence](MatrixCitySequence). If you only want to render your own data under different environmental settings based on the provided trajectories, you can skip this part. 

## Render custom data

Please see [Render-Data](MatrixCityPlugin/docs/Render-Data.md) to render custom data after getting camera trajectories (Provided / Custom).

## Exports camera poses

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
