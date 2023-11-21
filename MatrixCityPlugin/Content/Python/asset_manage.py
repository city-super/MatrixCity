import os
import unreal

from utils import get_world


# filename: str : Windows file fullname of the asset you want to import
# destination_path: str : Asset path
# option: obj : Import option object. Can be None for assets that does not usually have a pop-up when importing. (e.g. Sound, Texture, etc.)
# return: obj : The import task object
def buildImportTask(filename='', destination_path='', options=None):
    task = unreal.AssetImportTask()
    task.set_editor_property('automated', True)
    task.set_editor_property('destination_name', '')
    task.set_editor_property('destination_path', destination_path)
    task.set_editor_property('filename', filename)
    task.set_editor_property('replace_existing', True)
    task.set_editor_property('save', True)
    task.set_editor_property('options', options)
    return task


# tasks: obj List : The import tasks object. You can get them from buildImportTask()
# return: str List : The paths of successfully imported assets
def executeImportTasks(tasks=[], return_path=False):
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)

    if not return_path:
        return

    imported_asset_paths = []
    for task in tasks:
        for path in task.get_editor_property('imported_object_paths'):
            imported_asset_paths.append(path)
    return imported_asset_paths


# return: obj : Import option object. The basic import options for importing a static mesh
def buildStaticMeshImportOptions():
    options = unreal.FbxImportUI()
    # unreal.FbxImportUI
    options.set_editor_property('import_mesh', True)
    options.set_editor_property('import_textures', False)
    options.set_editor_property('import_materials', False)
    options.set_editor_property('import_as_skeletal', False)  # Static Mesh
    # unreal.FbxMeshImportData
    options.static_mesh_import_data.set_editor_property('import_translation', unreal.Vector(0.0, 0.0, 0.0))
    options.static_mesh_import_data.set_editor_property('import_rotation', unreal.Rotator(0.0, 0.0, 0.0))
    options.static_mesh_import_data.set_editor_property('import_uniform_scale', 1.0)
    # unreal.FbxStaticMeshImportData
    options.static_mesh_import_data.set_editor_property('combine_meshes', True)
    options.static_mesh_import_data.set_editor_property('generate_lightmap_u_vs', True)
    options.static_mesh_import_data.set_editor_property('auto_generate_collision', True)
    return options


# return: obj : Import option object. The basic import options for importing a skeletal mesh
def buildSkeletalMeshImportOptions():
    options = unreal.FbxImportUI()
    # unreal.FbxImportUI
    options.set_editor_property('import_mesh', True)
    options.set_editor_property('import_textures', True)
    options.set_editor_property('import_materials', True)
    options.set_editor_property('import_as_skeletal', True)  # Skeletal Mesh
    # unreal.FbxMeshImportData
    options.skeletal_mesh_import_data.set_editor_property('import_translation', unreal.Vector(0.0, 0.0, 0.0))
    options.skeletal_mesh_import_data.set_editor_property('import_rotation', unreal.Rotator(0.0, 0.0, 0.0))
    options.skeletal_mesh_import_data.set_editor_property('import_uniform_scale', 1.0)
    # unreal.FbxSkeletalMeshImportData
    options.skeletal_mesh_import_data.set_editor_property('import_morph_targets', True)
    options.skeletal_mesh_import_data.set_editor_property('update_skeleton_reference_pose', False)
    return options


# skeleton_path: str : Skeleton asset path of the skeleton that will be used to bind the animation
# return: obj : Import option object. The basic import options for importing an animation
def buildAnimationImportOptions(skeleton_path=''):
    options = unreal.FbxImportUI()
    # unreal.FbxImportUI
    options.set_editor_property('import_animations', True)
    options.skeleton = unreal.load_asset(skeleton_path)
    # unreal.FbxMeshImportData
    options.anim_sequence_import_data.set_editor_property('import_translation', unreal.Vector(0.0, 0.0, 0.0))
    options.anim_sequence_import_data.set_editor_property('import_rotation', unreal.Rotator(0.0, 0.0, 0.0))
    options.anim_sequence_import_data.set_editor_property('import_uniform_scale', 1.0)
    # unreal.FbxAnimSequenceImportData
    options.anim_sequence_import_data.set_editor_property('animation_length', unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
    options.anim_sequence_import_data.set_editor_property('remove_redundant_keys', False)
    return options


def buildAlembicImportOptions():
    options = unreal.AbcImportSettings()

    options.import_type = unreal.AlembicImportType.GEOMETRY_CACHE
    options.geometry_cache_settings.flatten_tracks = False

    return options


def importAnimation(fbx_path: str, ingame_destination_path: str, ingame_skeleton_path: str):
    # texture_task = buildImportTask('C:/Path/To/Assets/Texture.TGA', '/Game/Textures')
    # sound_task = buildImportTask('C:/Path/To/Assets/Sound.WAV', '/Game/Sounds')
    # static_mesh_task = buildImportTask('C:/Path/To/Assets/StaticMesh.FBX', '/Game/StaticMeshes', buildStaticMeshImportOptions())
    # skeletal_mesh_task = buildImportTask('C:/Path/To/Assets/SkeletalMesh.FBX', '/Game/SkeletalMeshes', buildSkeletalMeshImportOptions())
    # print(executeImportTasks([texture_task, sound_task, static_mesh_task, skeletal_mesh_task]))

    asset_name = os.path.basename(fbx_path).split('.')[0]
    if not unreal.EditorAssetLibrary.does_asset_exist(f'{ingame_destination_path}/{asset_name}'):
        animation_task = buildImportTask(fbx_path, ingame_destination_path, buildAnimationImportOptions(ingame_skeleton_path))
        executeImportTasks([animation_task])


def getRenderPeoplePaths() -> list:
    project_file = unreal.Paths.get_project_file_path()
    project_dir = os.path.dirname(project_file)
    root = os.path.join(project_dir, 'Content', 'RP_Character')

    all_dir_names = os.listdir(root)

    rps = []
    for dir_name in all_dir_names:
        if dir_name[:3] == 'rp_' and dir_name[-4:] == '_ue4':
            rps.append(dir_name)
    return rps


def generatePhyscisAssets():
    rps = getRenderPeoplePaths()
    world = get_world()

    with unreal.ScopedSlowTask(len(rps), 'Generating Physics Asset') as slow_task:
        slow_task.make_dialog(True)               # Makes the dialog visible, if it isn't already
        for idx, rp in enumerate(rps):
            slow_task.enter_progress_frame(1, f'Generating Physics Asset for {rp}: {idx}/{len(rps)}')     # Advance progress by one frame.
            if slow_task.should_cancel():         # True if the user has pressed Cancel in the UI
                break
            path = '/Game/RP_Character/'+rp.lower()+'/'+rp.lower()
            if unreal.EditorAssetLibrary.does_asset_exist(path+'_PhysicsAsset'):
                continue
            skm = unreal.load_asset(path)
            physics_asset = unreal.SF_BlueprintFunctionLibrary.generate_physics_asset(skm, 5)

            unreal.SystemLibrary.delay(world, 90, unreal.LatentActionInfo())
            unreal.EditorAssetLibrary.save_loaded_asset(skm, False)
            unreal.EditorAssetLibrary.save_loaded_asset(physics_asset, False)


def generateLODSkeletalMeshes(LOD=5):
    # generate LOD for occlusion detection
    rps = getRenderPeoplePaths()
    with unreal.ScopedSlowTask(len(rps), 'Generating LODs') as slow_task:
        slow_task.make_dialog(True)               # Makes the dialog visible, if it isn't already
        for rp in rps:
            if slow_task.should_cancel():         # True if the user has pressed Cancel in the UI
                break
            #path = os.path.join('Game',rp,'RP_Character',rp.lower(),rp.lower()+'.'+rp.lower())
            path = '/Game/RP_Character/'+rp.lower()+'/'+rp.lower()
            print(f'path: {path}')
            skm = unreal.load_asset(path)
            if unreal.EditorSkeletalMeshLibrary.get_lod_count(skm) < LOD:
                unreal.EditorSkeletalMeshLibrary.regenerate_lod(
                    skm,
                    new_lod_count=LOD,
                    regenerate_even_if_imported=False, 
                    generate_base_lod=False
                )
                unreal.EditorAssetLibrary.save_loaded_asset(skm, False)
            slow_task.enter_progress_frame(1)     # Advance progress by one frame.
