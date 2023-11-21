from typing import List, Tuple, Union

import unreal
from utils import get_world
from GLOBAL_VARS import EditorActorSub


def set_stencil_value(
    actor: unreal.Actor, 
    stencil_value: int, 
    receives_decals: bool = False
) -> None:
    # skeletal mesh component
    for skeletal_mesh_component in actor.get_components_by_class(unreal.SkeletalMeshComponent):
        skeletal_mesh_component.set_render_custom_depth(True)
        skeletal_mesh_component.set_custom_depth_stencil_value(stencil_value)
        skeletal_mesh_component.set_editor_property('receives_decals', receives_decals)
    # static mesh component
    for static_mesh_component in actor.get_components_by_class(unreal.StaticMeshComponent):
        static_mesh_component.set_render_custom_depth(True)
        static_mesh_component.set_custom_depth_stencil_value(stencil_value)
        static_mesh_component.set_editor_property('receives_decals', receives_decals)


def get_actor_mesh_component(
    actor: Union[unreal.SkeletalMeshActor, unreal.StaticMeshActor]
) -> Union[unreal.SkeletalMeshComponent, unreal.StaticMeshComponent]:
    if isinstance(actor, unreal.SkeletalMeshActor):
        mesh_component = actor.skeletal_mesh_component
    elif isinstance(actor, unreal.StaticMeshActor):
        mesh_component = actor.static_mesh_component
    else:
        raise TypeError(f'{actor.get_name()} is not a SkeletalMeshActor or StaticMeshActor')
    return mesh_component


def get_z_by_raycast(x: float, y: float, debug: bool=False):
    z_infinity_positive = 100000
    z_infinity_negative = -100000
    start = unreal.Vector(x, y, z_infinity_positive)
    end = unreal.Vector(x, y, z_infinity_negative)
    trace_channel = unreal.TraceTypeQuery.TRACE_TYPE_QUERY2
    actors_to_ignore = unreal.Array(unreal.Actor)

    object_types = unreal.Array(unreal.ObjectTypeQuery)

    # only OBJECT_TYPE_QUERY1 works
    object_types.append(unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1)

    if debug:
        DrawDebugTrace = unreal.DrawDebugTrace.FOR_DURATION
    else:
        DrawDebugTrace = unreal.DrawDebugTrace.NONE

    hits = unreal.SystemLibrary.line_trace_multi_for_objects(
        get_world(),
        start,
        end,
        object_types=object_types,
        trace_complex=True,
        actors_to_ignore=actors_to_ignore,
        draw_debug_type=DrawDebugTrace,
        ignore_self=False,
        trace_color=unreal.LinearColor(r=1, g=0, b=0, a=1),
        trace_hit_color=unreal.LinearColor(r=0, g=0, b=1, a=1),
        draw_time=60,
    )

    return hits


def hit_to_z(hit) -> float:
    z = hit.to_tuple()[4].z
    return z


def rp_rotation(rot: list) -> Tuple[float, float, float]:
    # rotate 90 degrees around yaw axis (z)
    rot_x, rot_y, rot_z = rot
    quat, quat_offset = unreal.Quat(), unreal.Quat()
    quat.set_from_euler(unreal.Vector(rot_x, rot_y, rot_z))
    quat_offset.set_from_euler(unreal.Vector(0, 0, 90))
    rot = (quat * quat_offset).euler()
    return (rot.x, rot.y, rot.z)



def draw_actor_bbox(
    actor: unreal.Actor, 
    color: unreal.LinearColor = unreal.LinearColor(1, 0, 0, 1), 
    duration: int = 10, 
    thickness: int = 1
) -> None:

    bbox: Tuple[unreal.Vector, unreal.Vector] = actor.get_actor_bounds(
        False, include_from_child_actors=True)
    world = get_world()

    actor_name = actor.get_fname()
    print(f'{actor_name} center: {bbox[0].to_tuple()}')
    print(f'{actor_name} extend: {bbox[1].to_tuple()}')

    unreal.SystemLibrary.draw_debug_box(
        world,
        bbox[0],
        bbox[1],
        color,
        duration=duration,
        thickness=thickness
    )


def draw_selected_actors_bbox(
    color: unreal.LinearColor = unreal.LinearColor(1, 0, 0, 1), 
    duration: int = 10, 
    thickness: int = 1
) -> None:

    actors = get_selected_actors()
    for actor in actors:
        draw_actor_bbox(actor, color, duration, thickness)


def spawn_actor_from_object(
    actor_object: unreal.StreamableRenderAsset,
    location: Tuple[float, float, float] = (0, 0, 0),
    rotation: Tuple[float, float, float] = (0, 0, 0),
) -> unreal.Actor:
    
    location = unreal.Vector(location[0], location[1], location[2])
    rotation = unreal.Rotator(rotation[0], rotation[1], rotation[2])

    if EditorActorSub:
        actor = EditorActorSub.spawn_actor_from_object(
            object_to_use=actor_object,
            location=location,
            rotation=rotation
        )
    else:
        actor = unreal.EditorLevelLibrary().spawn_actor_from_object(
            actor_class=actor_object,
            location=location,
            rotation=rotation
        )
    return actor


def spawn_actor_from_class(
    actor_class: unreal.Actor,
    location: Tuple[float, float, float] = (0, 0, 0),
    rotation: Tuple[float, float, float] = (0, 0, 0),
) -> unreal.Actor:
    
    location = unreal.Vector(location[0], location[1], location[2])
    rotation = unreal.Rotator(rotation[0], rotation[1], rotation[2])

    if EditorActorSub:
        actor = EditorActorSub.spawn_actor_from_class(
            actor_class=actor_class,
            location=location,
            rotation=rotation
        )
    else:
        actor = unreal.EditorLevelLibrary().spawn_actor_from_class(
            actor_class=actor_class,
            location=location,
            rotation=rotation
        )
    return actor


def get_selected_actors():
    # ! Selected
    if EditorActorSub:
        selected_actors = EditorActorSub.get_selected_level_actors()
    else:
        selected_actors = unreal.EditorLevelLibrary.get_selected_level_actors()
    return selected_actors


def get_class_actor(actor_class) -> unreal.Actor:
    # ! Class
    world = get_world()
    class_actor = unreal.GameplayStatics.get_actor_of_class(world, actor_class)
    return class_actor


def get_class_actors(actor_class) -> List[unreal.Actor]:
    # ! Class
    world = get_world()
    class_actors = unreal.GameplayStatics.get_all_actors_of_class(world, actor_class)
    return class_actors


def get_tag_actors(actor_tag) -> List[unreal.Actor]:
    # ! Tag
    world = get_world()
    tag_actors = unreal.GameplayStatics.get_all_actors_with_tag(world, actor_tag)
    return tag_actors


def get_all_actors() -> List[unreal.Actor]:
    # ! All
    world = get_world()
    all_actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
    return all_actors


def get_components_of_class(actor, component_class) -> List:
    # ! Component
    components = actor.get_components_by_class(component_class)
    return components

