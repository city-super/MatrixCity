# Tutorial

> Generate your first synthetic dataset in 10 minutes.

## Initialize

You should first follow the instruction in 
[Get-Started](./Get-Started.md) for plugin setup, 
and notice to modify config in [misc/user.json](../misc/user.json):

- `ue_command`: refers to the path of `UnrealEditor-Cmd.exe` (`UE4Editor-Cmd.exe` for ue4).
- `ue_project`: refers to the path of your project with suffix of `.uprojcet`.
- `render_config`: refers to the path of render config you defined in `.yaml` 
(an example definition is in [misc/render_config_common.yaml](../misc/render_config_common.yaml)).
- `python_script`: refers to the path of python script you want to execute.

### Run from python

```bash
python misc/run_cmd_async.py
```

You can simply run the command above to run a demonstration which contains:
- generating a sequence containing a [render people](https://renderpeople.com/free-3d-people/)
model with an animation, a cube, and a camera.
- rendering to RGB, mask, depth, normal map, and optical flow.

[misc/run_cmd_async.py](../misc/run_cmd_async.py) is a **complicated** script including:

- call `UE` process in `UnrealEditor-Cmd.exe` with `-ExecCmds=py {python_script}` 
(defined in [run_cmd_async.py#L214](../misc/run_cmd_async.py)), where `python_script` is
defined in [misc/user.json#L5](../misc/user.json).
- communicate with `UE` process by socket asynchronously.
    - receive generation status from `UE` process
    - error catching and resuming

## Details

The core of `run_cmd_async.py` is running `{python_script}` inside `UE` process, 
`{python_script}` is 
[Content/Python/pipeline.py](../Content/Python/pipeline.py) 
in this tutorial. So let's get rid of the fancy code in `run_cmd_async.py` and
just focus on `{python_script}`.

### [pipeline.py](../Content/Python/pipeline.py)

This pipeline is divided into three parts:

1. create a PIE Executor, and connect to the socket server 
created in [run_cmd_async.py#L236](../misc/run_cmd_async.py).

    ```python
    import unreal
    from utils import log_msg_with_socket

    host = '127.0.0.1'
    port = 9999
    PIEExecutor = unreal.MoviePipelinePIEExecutor()
    PIEExecutor.connect_socket(host, port)
    log_msg_with_socket(PIEExecutor, '[*] Unreal Engine Loaded!')
    ```

    > Notice: this step is not necessary, it is just a demonstration of
    > monitor `UE` process when it's running.
    >
    > Plus, it may not be the best way to connect to the socket server using `PIEExecutor`,
    > but it is a simple way to do it, you can develop your own.

2. create a sequence

    Our plugin is relied on the [Movie Render Queue](https://docs.unrealengine.com/5.0/en-US/render-cinematics-in-unreal-engine/) plugin,
    which is relied on [Sequencer](https://docs.unrealengine.com/5.0/en-US/unreal-engine-sequencer-movie-tool-overview/).
    There are great tools developed by official Unreal Engine, and perfect for generating synthetic data.

    ```python
    import utils_sequencer

    level, sequence_name = utils_sequencer.main()
    ```

    In [utils_sequencer.py](../Content/Python/utils_sequencer.py), 
    we defined some useful functions for entirely creating a sequence with python code, including:

    - `generate_sequence()`: create a new sequence.
    - `add_spawnable_camera_to_sequence()`: add a new camera to the sequence, and it is spawned by this sequence.
    - `add_spawnable_actor_to_sequence()`: add a new actor to the sequence, and it is spawned by this sequence.
        > because it is spawned by this sequence, it would not change the original level.
    - `main()`: a demonstration of using these functions with demonstration project 
    ([OneDrive Download](https://sensetime-my.sharepoint.cn/:u:/g/personal/meihaiyi_sensetime_com/EZFFJl3HAu9LimUoSRy0hDsBV6crj71b5Og1uxwuIFw6FA))
    - ...

    **CAUTION**: Please use `SequenceKey` defined in [pydantic_model.py](../Content/Python/pydantic_model.py) 
    when adding keys to the sequence to avoid errors.

    ![sequencer](./pics/Sequencer.png "Sequencer")

3. render the sequence

    ```python
    from custom_movie_pipeline import CustomMoviePipeline
    from data.config import CfgNode

    render_config_path = 'misc/render_config_common.yaml'
    render_config = CfgNode.load_yaml_with_base(render_config_path)
    CustomMoviePipeline.clear_queue()
    CustomMoviePipeline.add_job_to_queue_with_render_config(
        level=level,
        level_sequence=sequence_name,
        render_config=render_config
    )
    CustomMoviePipeline.render_queue(executor=PIEExecutor)
    ```

    After creating a sequence, we should render it with `Movie Render Queue`.

    In [custom_movie_pipeline.py](../Content/Python/custom_movie_pipeline.py),
    we defined a class `CustomMoviePipeline` for rendering a sequence with movie render queue in python code, 
    there are several classmethod defined inside the class, including:
    - `CustomMoviePipeline.clear_queue()`: clear the queue of rendering.
    - `CustomMoviePipeline.add_job_to_queue_with_render_config()`: add a job to the queue of rendering.
        > there is a queue of rendering, and each job is a rendering job.
        > ![render queue](./pics/RenderQueue.png "render queue")
    - `CustomMoviePipeline.render_queue()`: render the queue of rendering.

    **CAUTION**: `render_config` is dict which contains information of rendering.
    You can found a template in [misc/render_config_common.yaml](../misc/render_config_common.yaml), 
    and load it with `render_config = CfgNode.load_yaml_with_base(render_config_path)`,
    which contains following setting:
    - Render_Passes: a list of render passes (rgb, mask, depth, normal map, optical flow, etc.).
    - Output_Path: the path of output.
    - File_Name_Format: the format of output file name.
    - Anti_Alias: anti-alias setting.
    - Motion_Blur: motion blur setting.
    - ...

Go to the `Output_Path`, you would get a result like:

![demo](./pics/demo.gif)

## Noticed

### `sys.path`

As described in [official documentation](https://docs.unrealengine.com/5.0/en-US/scripting-the-unreal-editor-using-python/#pythonenvironmentandpathsintheunrealeditor),
The Unreal Editor automatically adds several paths to this `sys.path` list:

- The **Content/Python** sub-folder in your Project's folder.
- The **Content/Python** sub-folder in the main Unreal Engine installation.
- The **Content/Python** sub-folder in each enabled Plugin's folder.
- ...

So, the main python modules of this plugin are defined in 
[`Content/Python`](../Content/Python) folder.


### Disable `Live Coding` in `Editor Preferences`:

This new feature of ue5 would cause some problems when you are using this plugin.

![](./pics/EditorPreferences.png)

![](./pics/LiveCoding.png)