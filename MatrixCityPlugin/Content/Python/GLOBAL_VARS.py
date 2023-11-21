from typing import *
from pathlib import Path
import unreal


def get_subsystem(
    engine_major_version: int
):
    EditorActorSub = EditorLevelSub = EditorSub = None
    if engine_major_version == 5:
        EditorActorSub = unreal.EditorActorSubsystem()
        EditorLevelSub = unreal.LevelEditorSubsystem()
        EditorSub = unreal.UnrealEditorSubsystem()
        # level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

    return EditorActorSub, EditorLevelSub, EditorSub


def get_plugin_path() -> List[Path]:
    PROJECT_FILE = Path(unreal.Paths.get_project_file_path())
    PROJECT_ROOT = PROJECT_FILE.parent
    PLUGIN_ROOT = PROJECT_ROOT / 'Plugins' / PLUGIN_NAME
    PLUGIN_PYTHON_ROOT = PLUGIN_ROOT / 'Content/Python'
    LEVEL_INFO_JSON = PLUGIN_ROOT / 'Resources' / 'level_info.json'

    return PROJECT_ROOT, PLUGIN_ROOT, PLUGIN_PYTHON_ROOT, LEVEL_INFO_JSON


PLUGIN_NAME = 'XRFeitoriaGear'

MATERIAL_PATHS = {
    'depth': f'/{PLUGIN_NAME}/Materials/MRQ/PPM_depth_EXR',
    'mask': f'/{PLUGIN_NAME}/Materials/MRQ/PPM_mask_MRQ',
    'optical_flow': f'/{PLUGIN_NAME}/Materials/PPM_velocity',
    'diffuse': f'/{PLUGIN_NAME}/Materials/PPM_diffusecolor',
    'normal': f'/{PLUGIN_NAME}/Materials/PPM_normal_map',
    'metallic': f'/{PLUGIN_NAME}/Materials/PPM_metallic',
    'roughness': f'/{PLUGIN_NAME}/Materials/PPM_roughness',
    'specular': f'/{PLUGIN_NAME}/Materials/PPM_specular',
    'tangent': f'/{PLUGIN_NAME}/Materials/PPM_tangent',
    'basecolor': f'/{PLUGIN_NAME}/Materials/PPM_basecolor',
}

PROJECT_ROOT, PLUGIN_ROOT, PLUGIN_PYTHON_ROOT, LEVEL_INFO_JSON = get_plugin_path()

ENGINE_MAJOR_VERSION = int(unreal.SystemLibrary.get_engine_version()[0])
EditorActorSub, EditorLevelSub, EditorSub = get_subsystem(ENGINE_MAJOR_VERSION)
