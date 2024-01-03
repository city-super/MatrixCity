# Code Details
Python modules are defined in [MatrixCityPlugin/Content/Python](MatrixCityPlugin/Content/Python/) folder.

C++ modules are defined in [MatrixCityPlugin/Source/MatrixCityPlugin](MatrixCityPlugin/Source/MatrixCityPlugin/) folder.

[misc/run_cmd_async.py](../misc/run_cmd_async.py) is a **complicated** script including:

- call `UE` process in `UnrealEditor-Cmd.exe` with `-ExecCmds=py {python_script}` 
(defined in [run_cmd_async.py#L213](../misc/run_cmd_async.py)), where `python_script` is
defined in [misc/user.json#L5](../misc/user.json).
- communicate with `UE` process by socket asynchronously.
    - receive generation status from `UE` process
    - error catching and resuming

The core of `run_cmd_async.py` is running `{python_script}` inside `UE` process, 
`{python_script}` is 
[Content/Python/pipeline.py](../Content/Python/pipeline.py) 
in this tutorial. So let's get rid of the fancy code in `run_cmd_async.py` and
just focus on `{python_script}`.

## [pipeline.py](../Content/Python/pipeline.py)

This pipeline is divided into three parts:

### 1. create a PIE Executor, and connect to the socket server 
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

### 2. create a sequence

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
    - `main()`: a demonstration of using these functions with demonstration project
    - ...

    **CAUTION**: Please use `SequenceKey` defined in [pydantic_model.py](../Content/Python/pydantic_model.py) 
    when adding keys to the sequence to avoid errors.


### 3. render the sequence

    Initiating the `City Sample Project` from a python script is is notably inefficient, and it cannot flexibly control the lighting, human and car crowds. Thus, in the paper, our plugin is used to generate camera trajectories, which are then manually rendered within the `City Sample Project`. 
    
    For your custom project, you can uncomment this part of code, allowing the use of Python scripts for both trajectory generation and image rendering.

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
    there are several class method defined inside the class, including:
    - `CustomMoviePipeline.clear_queue()`: clear the queue of rendering.
    - `CustomMoviePipeline.add_job_to_queue_with_render_config()`: add a job to the queue of rendering.
        > there is a queue of rendering, and each job is a rendering job.
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