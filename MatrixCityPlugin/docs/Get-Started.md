# Get Started

## Install `Unreal Engine`

### Download and Install Epic Games Launcher

[https://store.epicgames.com/en-US/download](https://store.epicgames.com/en-US/download)

### Install `Unreal Engine 5.0.3` in Epic Games Launcher

![EpicGameLauncher](./pics/EpicGameLauncher.png "EpicGameLauncher")

Choose `Unreal Engine 5.0.3` and click `Install` in your own setting 
(normally default setting is good).

## Install `XRFeitoria-Gear`

Download xrfeitoria-gear-master.zip from [**releases page**](../../releases)
and unzip it.

### 0. Download our demonstration project (or Create a new project)

[OneDrive Download (UE5.0.3)](https://sensetime-my.sharepoint.cn/:u:/g/personal/meihaiyi_sensetime_com/EZFFJl3HAu9LimUoSRy0hDsBV6crj71b5Og1uxwuIFw6FA)

[OneDrive Download (UE4.27.3)](https://sensetime-my.sharepoint.cn/:u:/g/personal/meihaiyi_sensetime_com/Eb8qdrUUl3VHs9V8vN1EZRYBKXK4654oniyU3VQkfMtlEQ?e=eAJb7p)

### 1. set config

Modify config in [misc/user.json](../misc/user.json):

- `ue_command`: refers to the path of `UnrealEditor-Cmd.exe` (`UE4Editor-Cmd.exe` for ue4).
- `ue_project`: refers to the path of your project with suffix of `.uprojcet`.
- `render_config`: refers to the path of render config you defined in `.yaml` 
(an example definition is in [misc/render_config_common.yaml](../misc/render_config_common.yaml)).
- `python_script`: refers to the path of python script you want to execute.

### 2. init the plugin

```bash
# (optional) change pip source to speed up
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# python 3.7 or above
python misc/run_init.py -f misc/user.json
```

This script would execute the following steps:

- `pip install -r misc/requirements_ue.txt` for ue python.

- `pip install -r misc/requirements.txt` for system python.

- create a soft link to the plugin folder in the project root folder.

## Run demonstration

```bash
python misc/run_cmd_async.py -f misc/user.json
```

You can simply run the command above to run a demonstration which contains:
- generating a sequence containing a `render people` model with animations and a `cube`
- rendering to RGB, mask, depth, normal map, and optical flow.

**The rendering results are saved in `Output_Path` defined in `render_config.yaml`.**
- visualize the results in `Output_Path`
- use [visualize.py](../misc/visualize.py) or 
[exr_reader.py](https://github.com/openxrlab/xrprimer/blob/main/python/xrprimer/io/exr_reader.py)
to convert `.exr` results to `.png`, for example:

```bash
$Output_Path="E:\Datasets\tmp"
python misc/visualize.py -i $Output_Path -o $Output_Path/vis_mask --img_pattern "*/mask/*" -t mask 
python misc/visualize.py -i $Output_Path -o $Output_Path/vis_depth --img_pattern "*/depth/*" -t depth 
python misc/visualize.py -i $Output_Path -o $Output_Path/vis_flow --img_pattern "*/flow/*" -t flow 
```

You would get a result like:

![demo](./pics/demo.gif)

**For details of this demonstration, please refer to [Tutorial](./Tutorial.md).**

---

> This plugin will automatically set some project settings for ue project (see [Source/XRFeitoriaGear/Private/XRFeitoriaGear.cpp](../Source/XRFeitoriaGear/Private/XRFeitoriaGear.cpp) for details):
> 
> - `URendererSettings->CustomDepthStencil = ECustomDepthStencil::EnabledWithStencil`
> (same as `r.CustomDepth=3` in `Config/DefaultEngine.ini` under `[/Script/Engine.RendererSettings]`
> 
> - `URendererSettings->VelocityPass = EVelocityOutputPass::BasePass`
> (same as `r.VelocityOutputPass=1` in `Config/DefaultEngine.ini` under `[/Script/Engine.RendererSettings]`)
> 
>     - in UE 4.27: `Settings->bBasePassOutputsVelocity = True` 
>    (same as `r.BasePassOutputsVelocity=True` in `Config/DefaultEngine.ini` under `[/Script/Engine.RendererSettings]`)
> 
> - `UMovieRenderPipelineProjectSettings->DefaultClasses.Add(UCustomMoviePipelineOutput::StaticClass());`
> `UMovieRenderPipelineProjectSettings->DefaultClasses.Add(UCustomMoviePipelineDeferredPass::StaticClass());`
> ![movie render pipeline setting](./pics/MovieRenderPipelineProjectSettings.png "Movie Render Pipeline Setting")