# Get Started

## Device Requirement for `City Sample Project`

- Windows 10 with support for DirectX 12

- 12-core CPU at 3.4 GHz

- 64 GB of System RAM

- GeForce RTX-2080 / AMD Radeon 6000 or higher

- At least 8 GB of VRAM

## Install `Unreal Engine 5.0.3`

- Download and Install [Epic Games Launcher](https://store.epicgames.com/en-US/download).

- Choose `Unreal Engine 5.0.3` and click `Install` in your own setting (normally default setting is good).

![teaser](figures/ue5_install.png)

## Install `City Sample Project` in Epic Games Launcher


## Install `MatrixCityPlugin`

Download MatrixCityPlugin from our github repo.

### 0. Create a new UE project.

### 1. set config

Modify config in [misc/user.json](../misc/user.json):

- `ue_command`: refers to the path of `UnrealEditor-Cmd.exe`.
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

**For details of this demonstration, please refer to [Tutorial](./Tutorial.md).**

---

> This plugin will automatically set some project settings for ue project (see [Source/MatrixCityPlugin/Private/MatrixCityPlugin.cpp](../Source/MatrixCityPlugin/Private/MatrixCityPlugin.cpp) for details):
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