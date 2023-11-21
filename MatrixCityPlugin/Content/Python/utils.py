import json
import time
from typing import List, Optional, Tuple, Dict

import unreal
from GLOBAL_VARS import LEVEL_INFO_JSON, EditorLevelSub, EditorSub

################################################################################
# define decorators


def loader_func(func):

    def wrap_func(*args, **kwargs):
        unreal.log_warning("ticking.")
        asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
        if asset_registry.is_loading_assets():
            unreal.log_warning("still loading...")
        else:
            unreal.log_warning("ready!")
            unreal.unregister_slate_pre_tick_callback(tickhandle)

        result = func(*args, **kwargs)
        return result

    # This function shows the execution time of
    # the function object passed
    tickhandle = unreal.register_slate_pre_tick_callback(wrap_func)

    return wrap_func


def timer_func(func):
    # This function shows the execution time of
    # the function object passed
    def wrap_func(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()
        print(
            f"[TimerLogger] Function {repr(func.__name__)} executed in {(t2-t1):.4f}s"
        )
        return result

    return wrap_func


def ue_task(function):
    def wrapper(*args, **kwargs):
        slow_task = args[0]  # args[0] is the first argument of the function
        # slow_task = args[0].slow_task  # args[0] is the instance of the class
        # slow_task = kwargs['slow_task']
        # print(slow_task)

        # True if the user has pressed Cancel in the UI
        if slow_task.should_cancel():
            exit()

        # log the start of the task
        log_info = f"[PythonLogger] Running Function: {repr(function.__name__)}"
        slow_task.enter_progress_frame(1, log_info)
        # print(log_info)

        # run the function
        result = function(*args, **kwargs)

        # log the end of the task
        # print(f"[PythonLogger] Function {repr(function.__name__)} finished")

        return result

    return wrapper

################################################################################


class loadRegistry():
    """
        example_usage:

        registry = loadRegistry(RenderQueue)
        registry.register()
    """

    def __init__(self, func) -> None:
        self.tickhandle = None
        self.func = func

    def testing(self, deltaTime):
        unreal.log_warning("ticking.")
        asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
        if asset_registry.is_loading_assets():
            unreal.log_warning("still loading...")
        else:
            unreal.log_warning("ready!")
            unreal.unregister_slate_pre_tick_callback(self.tickhandle)

            self.func()

    def register(self):
        self.tickhandle = unreal.register_slate_pre_tick_callback(self.testing)

        unreal.log_warning("registered!")
        return self.tickhandle


def check_abort(slow_task):
    slow_task.enter_progress_frame(1)
    if slow_task.should_cancel():
        exit()


def log_msg_with_socket(PIEExecutor: unreal.MoviePipelinePIEExecutor, msg: str):
    PIEExecutor.send_socket_message(msg)
    print(msg)


################################################################################
# misc

def get_world() -> unreal.World:
    if EditorSub:
        world = EditorSub.get_editor_world()
    else:
        world = unreal.EditorLevelLibrary.get_editor_world()
    return world


def new_world(new_level_path: str) -> bool:
    if EditorLevelSub:
        success = EditorLevelSub.new_level(new_level_path)
    else:
        success = unreal.EditorLevelLibrary().new_level(new_level_path)
    return success


def get_levels(world: Optional[unreal.World]=None) -> List[unreal.Level]:
    if not world:
        world = get_world()
    levels = unreal.EditorLevelUtils.get_levels(world)
    return levels


def save_current_level() -> None:
    if EditorLevelSub:
        EditorLevelSub.save_current_level()
    else:
        unreal.EditorLevelLibrary.save_current_level()


def get_soft_object_path(path: str) -> unreal.SoftObjectPath:
    path = f'{path}.{path.split("/")[-1]}'
    return unreal.SoftObjectPath(path)


def get_sublevels(persistent_level_path: str) -> List[Dict]:
    """get sublevels of persistent level, this step would load the persistent level.

    Args:
        persistent_level_path (str): a path to the persistent level, e.g. "/Game/Maps/PersistentLevel"

    Returns:
        level_configs (List(Dict)): a list of level_configs (dict) containing keys of 
            `level_name`, `is_visible`, and `streaming_class`.
    """
    asset_registry: unreal.AssetRegistry = unreal.AssetRegistryHelpers.get_asset_registry()

    # load persistent level
    world = unreal.EditorLoadingAndSavingUtils.load_map(persistent_level_path)
    # unreal.GameplayStatics.open_level(self.get_last_loaded_world(), mapPackagePath, True, gameOverrideClassPath)

    # get all sub-levels of persistent level and their config
    level_configs = []
    persistent_level_asset_data = asset_registry.get_asset_by_object_path(persistent_level_path)
    persistent_level_name = str(persistent_level_asset_data.package_name)
    level_configs.append(
        {
            "level_name": persistent_level_name,
            "is_visible": True,
            "streaming_class": "LevelStreamingAlwaysLoaded",
        }
    )

    levels: List[unreal.Level] = unreal.EditorLevelUtils.get_levels(world)
    for level in levels:
        asset_data = asset_registry.get_asset_by_object_path(level.get_path_name())
        sub_level_name = str(asset_data.package_name)
        streaming_level = unreal.GameplayStatics.get_streaming_level(world, sub_level_name)
        if streaming_level is not None:
            level_configs.append(
                {
                    "level_name": sub_level_name,
                    "is_visible": streaming_level.is_level_visible(),
                    "streaming_class": type(streaming_level).__name__,
                }
            )

    unreal.log(level_configs)
    return level_configs

def add_levels(persistent_level_path: str, new_level_path: str) -> Tuple[List, List]:
    """add levels from persistent level to the current world

    Args:
        persistent_level_path (str): a path to the persistent level, e.g. "/Game/Maps/PersistentLevel"

    Returns:
        level_visible_names (list): a list of visible level names
        level_hidden_names (list): a list of hidden level names
    """

    # check if persistent level exists
    is_level_exist = unreal.EditorAssetLibrary.does_asset_exist(persistent_level_path)
    assert is_level_exist, RuntimeError(f"Persistent level does not exist", persistent_level_path)

    # get/save sub-levels as json
    sublevel_json = LEVEL_INFO_JSON
    level_configs = []
    level_infos = {}

    if sublevel_json.exists():
        with open(sublevel_json) as f:
            level_infos: dict = json.load(f)
        if persistent_level_path in level_infos.keys():
            level_configs = level_infos[persistent_level_path]
    
    if not level_configs:
        # get sublevels of persistent level, this step would load the persistent level
        level_configs = get_sublevels(persistent_level_path)
        # reload new levels
        world = unreal.EditorLoadingAndSavingUtils.load_map(new_level_path)
        level_infos[persistent_level_path] = level_configs
        with open(sublevel_json, "w") as f:
            json.dump(level_infos, f, indent=4)

    # add persistent level and its sub levels, set visibility
    level_visible_names, level_hidden_names = [], []
    world = get_world()

    for level_config in level_configs:
        level_name: str = level_config["level_name"]
        is_visible: bool = level_config["is_visible"]
        streaming_class: str = level_config["streaming_class"]
        streaming_class_cls = getattr(unreal, streaming_class)
        streaming_level: unreal.LevelStreaming = unreal.EditorLevelUtils.add_level_to_world(world, level_name, streaming_class_cls)

        assert (streaming_class_cls is not None), f"Unknown unreal class: {streaming_class}"
        assert (streaming_level is not None), f"Unable to add level to the world: {level_name}"

        unreal.EditorLevelUtils.set_level_visibility(streaming_level.get_loaded_level(), is_visible, False)

        level_basename = level_name.rpartition("/")[-1]
        if is_visible:
            level_visible_names.append(level_basename)
        else:
            level_hidden_names.append(level_basename)
    
    return level_visible_names, level_hidden_names


@ue_task
@timer_func
def tmp(slow_task):
    time.sleep(0.01)


def task_bar():

    with unreal.ScopedSlowTask(100, 'Running') as slow_task:
        slow_task.make_dialog(True)

        for i in range(100):
            time.sleep(0.01)
            check_abort(slow_task)

    with unreal.ScopedSlowTask(100, 'Running') as slow_task:
        slow_task.make_dialog(True)
        for i in range(100):
            tmp(slow_task)
