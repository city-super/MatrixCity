from typing import Callable, Optional

import unreal
import utils
from data.config import CfgNode

from GLOBAL_VARS import MATERIAL_PATHS, PLUGIN_ROOT

# define the post process material to the render_pass
material_paths = MATERIAL_PATHS
material_path_keys = [key.lower() for key in material_paths.keys()]


class CustomMoviePipeline():
    """This class contains several class methods, which are used to control the
    movie pipeline (Movie Render Queue), including:

    - clearQueue: Clear the movie render queue.
    - addJobToQueueWithYAMLConfig: Add a job to the movie render queue with yaml config.
    - renderQueue: Render the jobs in movie render queue.
    - ...
    """

    render_config = CfgNode.load_yaml_with_base(
        PLUGIN_ROOT / 'misc/render_config.yaml')
    subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    pipeline_queue = subsystem.get_queue()

    host = '127.0.0.1'
    port = 9999
    jobs = []
    new_executor = None

    @classmethod
    def clear_queue(cls):
        for job in cls.pipeline_queue.get_jobs():
            unreal.log("Deleting job " + job.job_name)
            cls.pipeline_queue.delete_job(job)
        unreal.log("Queue cleared.")

    @classmethod
    def add_render_passes(
        cls,
        movie_preset: unreal.MoviePipelineMasterConfig,
        render_passes: list
    ) -> None:
        """Add render passes to a movie preset.

        Args:
            movie_preset (unreal.MoviePipelineMasterConfig): The movie preset to add render passes to.
            render_passes (list): definition of render passes. 
                The available render passes are same as `material_paths` which is defined in the beginning of this file:

                - rgb
                - depth
                - mask
                - optical_flow
                - diffuse
                - normal
                - metallic
                - roughness
                - specular
                - tangent
                - basecolor
        """

        # find or add setting
        render_pass = movie_preset.find_or_add_setting_by_class(
            unreal.CustomMoviePipelineDeferredPass)
        render_pass_config = movie_preset.find_or_add_setting_by_class(
            unreal.CustomMoviePipelineOutput)

        # add render passes
        additional_render_passes = []
        for render_pass in render_passes:
            pass_name = render_pass['pass_name']
            enable = render_pass['enable']
            ext = getattr(unreal.CustomImageFormat,
                          render_pass['ext'].upper())  # convert to enum

            if pass_name.lower() == 'rgb':
                render_pass_config.enable_render_pass_rgb = enable
                render_pass_config.render_pass_name_rgb = pass_name
                render_pass_config.extension_rgb = ext
            elif pass_name.lower() in material_path_keys:
                # material = unreal.SoftObjectPath(material_map[pass_name])
                material = unreal.load_asset(material_paths[pass_name.lower()])
                _pass = unreal.CustomMoviePipelineRenderPass(
                    enabled=enable,
                    material=material,
                    render_pass_name=pass_name,
                    extension=ext
                )
                additional_render_passes.append(_pass)

        render_pass_config.additional_render_passes = additional_render_passes

    @classmethod
    def add_output_config(
        cls,
        movie_preset: unreal.MoviePipelineMasterConfig,
        resolution: list = [1920, 1080],
        file_name_format: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> None:
        """Add output config to a movie preset.

        Args:
            movie_preset (unreal.MoviePipelineMasterConfig): The movie preset to add output config to.
            resolution (list): Resolution of the output, e.g. [1920, 1080].
            file_name_format (str): Format of the output file name, e.g. '{sequence_name}/{render_pass}/{frame_number}'
            output_path (str): Path of the output, e.g. 'E:/output'
        """
        # find or add setting
        output_config = movie_preset.find_or_add_setting_by_class(
            unreal.MoviePipelineOutputSetting)

        # add resolution settings
        output_config.output_resolution = unreal.IntPoint(
            resolution[0], resolution[1])

        # add file name format settings
        if file_name_format:
            output_config.file_name_format = file_name_format

        # set output path
        if output_path is not None:
            output_config.output_directory = unreal.DirectoryPath(output_path)

    @classmethod
    def add_console_command(
        cls,
        movie_preset: unreal.MoviePipelineMasterConfig,
        motion_blur: bool = False,
    ) -> None:
        """Add console command to a movie preset. Now only support motion blur.

        Args:
            movie_preset (unreal.MoviePipelineMasterConfig): The movie preset to add console command to.
            motion_blur (bool): Whether to enable motion blur.
        """
        # find or add setting
        console_config = movie_preset.find_or_add_setting_by_class(
            unreal.MoviePipelineConsoleVariableSetting)

        # add motion blur settings
        if not motion_blur:
            console_config.console_variables['r.MotionBlurQuality'] = 0

    @classmethod
    def add_anti_alias(
        cls,
        movie_preset: unreal.MoviePipelineMasterConfig,
        anti_alias: dict = {'enable': False,
                            'spatial_samples': 8, 'temporal_samples': 1},
    ) -> None:
        """Add anti-alias settings to a movie preset.

        Args:
            movie_preset (unreal.MoviePipelineMasterConfig): The movie preset to add anti-alias settings to.
            anti_alias (dict): Anti-alias settings.
        """

        # add anti_alias settings
        if anti_alias['enable']:
            anti_alias_config = movie_preset.find_or_add_setting_by_class(
                unreal.MoviePipelineAntiAliasingSetting)
            anti_alias_config.override_anti_aliasing = True
            anti_alias_config.spatial_sample_count = anti_alias['spatial_samples']
            anti_alias_config.temporal_sample_count = anti_alias['temporal_samples']

    @classmethod
    def add_settings_to_movie_preset(
        cls,
        movie_preset: unreal.MoviePipelineMasterConfig,
        render_passes: list = [
            {'pass_name': 'rgb', 'enable': True, 'ext': 'png'}],
        resolution: list = [1920, 1080],
        file_name_format: Optional[str] = None,
        output_path: Optional[str] = None,
        anti_alias: dict = {'enable': False,
                            'spatial_samples': 8, 'temporal_samples': 1},
        motion_blur: bool = False,
    ) -> unreal.MoviePipelineMasterConfig:
        """Add settings to a movie preset.

        Args:
            movie_preset (unreal.MoviePipelineMasterConfig): The movie preset to add settings to.
            render_passes (list): definition of render passes.
            resolution (list): Resolution of the output, e.g. [1920, 1080].
            file_name_format (str): Format of the output file name, e.g. '{sequence_name}/{render_pass}/{frame_number}'
            output_path (str): Path of the output, e.g. 'E:/output'
            anti_alias (dict): Anti-alias settings.
            motion_blur (bool): Whether to enable motion blur.

        Returns:
            unreal.MoviePipelineMasterConfig: The created movie preset.
        """

        cls.add_render_passes(movie_preset, render_passes)
        cls.add_output_config(movie_preset, resolution,
                              file_name_format, output_path)
        cls.add_anti_alias(movie_preset, anti_alias)
        cls.add_console_command(movie_preset, motion_blur)

        unreal.EditorAssetLibrary.save_loaded_asset(movie_preset)
        return movie_preset

    @classmethod
    def create_movie_preset(
        cls,
        render_passes: list = [
            {'pass_name': 'rgb', 'enable': True, 'ext': 'png'}],
        resolution: list = [1920, 1080],
        file_name_format: Optional[str] = None,
        output_path: Optional[str] = None,
        anti_alias: dict = {'enable': False,
                            'spatial_samples': 8, 'temporal_samples': 1},
        motion_blur: bool = False,
    ) -> unreal.MoviePipelineMasterConfig:
        """Create a movie preset from args.

        Args:
            render_passes (list): definition of render passes.
            resolution (list): Resolution of the output, e.g. [1920, 1080].
            file_name_format (str): Format of the output file name, e.g. '{sequence_name}/{render_pass}/{frame_number}'
            output_path (str): Path of the output, e.g. 'E:/output'
            anti_alias (dict): Anti-alias settings.
            motion_blur (bool): Whether to enable motion blur.

        Returns:
            unreal.MoviePipelineMasterConfig: The created movie preset.
        """

        movie_preset = unreal.MoviePipelineMasterConfig()

        cls.add_render_passes(movie_preset, render_passes)
        cls.add_output_config(movie_preset, resolution,
                              file_name_format, output_path)
        cls.add_anti_alias(movie_preset, anti_alias)
        cls.add_console_command(movie_preset, motion_blur)

        return movie_preset

    @classmethod
    def create_job(
        cls,
        level: str,
        level_sequence: str,
    ) -> unreal.MoviePipelineExecutorJob:
        # check if assets exist
        if not (unreal.EditorAssetLibrary.does_asset_exist(level) and unreal.EditorAssetLibrary.does_asset_exist(level_sequence)):
            return False

        # Create a new job and add it to the queue.
        new_job = cls.pipeline_queue.allocate_new_job(
            unreal.MoviePipelineExecutorJob)
        new_job.job_name = str(level_sequence.rsplit('/', 1)[-1])
        new_job.map = utils.get_soft_object_path(level)
        new_job.sequence = utils.get_soft_object_path(level_sequence)

        return new_job

    @classmethod
    def add_job_to_queue_with_preset(
        cls,
        level: str,
        level_sequence: str,
        config: str,
    ) -> bool:
        """Add a job to the queue with a pre-defined preset.

        Args:
            level (str): level path in unreal engine.
            level_sequence (str): level sequence path in unreal engine.
            config (str): pre-defined preset path in unreal engine.

        Returns:
            bool: success or not.
        """
        new_job = cls.create_job(level, level_sequence)
        movie_preset = unreal.load_asset(config)
        new_job.set_configuration(movie_preset)
        unreal.log(f"Added new job ({new_job.job_name}) to queue.")
        return True

    @classmethod
    def add_job_to_queue_with_render_config(
        cls,
        level: str,
        level_sequence: str,
        render_config: Optional[dict] = None,
    ) -> bool:
        """Add a job to the queue with a YAML config loaded from a file.

        Args:
            level (str): level path in unreal engine.
            level_sequence (str): level sequence path in unreal engine.
            render_config (dict): YAML config loaded from a file. You can
                find a template in `data/render_config.yaml`.

        Returns:
            bool: success or not.

        Examples:
            >>> render_config = {
                    'Resolution': [1920, 1080],
                    'Output_Path': 'E:/Datasets/tmp',
                    'File_Name_Format': '{sequence_name}/{render_pass}/{frame_number}',
                    'Motion_Blur': False,
                    'Anti_Alias': {'enable': False, 'spatial_samples': 8, 'temporal_samples': 8},
                    'Render_Passes': [
                        {'pass_name': 'rgb', 'enable': True, 'ext': 'jpeg'},
                        {'pass_name': 'depth', 'enable': True, 'ext': 'exr'},
                        {'pass_name': 'mask', 'enable': True, 'ext': 'exr'},
                        {'pass_name': 'optical_flow', 'enable': True, 'ext': 'exr'},
                        {'pass_name': 'normal', 'enable': True, 'ext': 'png'}
                    ]
                }
            >>> # or you can use the following code to load the config from a file
            >>> from data.config import CfgNode
            >>> render_config = CfgNode.load_yaml_with_base(PLUGIN_ROOT / 'misc/render_config_common.yaml')
            >>> #
            >>> CustomMoviePipeline.add_job_to_queue_with_render_config(
                    level='/Game/ThirdPerson/Maps/ThirdPersonMap',
                    level_sequence='/Game/NewLevelSequence',
                    render_config=render_config
                )
        """
        newJob = cls.create_job(level, level_sequence)
        if render_config is None:
            render_config = cls.render_config
        movie_preset = cls.create_movie_preset(
            render_passes=render_config['Render_Passes'],
            resolution=render_config['Resolution'],
            file_name_format=render_config['File_Name_Format'],
            output_path=render_config['Output_Path'],
            anti_alias=render_config['Anti_Alias'],
            motion_blur=render_config['Motion_Blur'],
        )
        newJob.set_configuration(movie_preset)
        unreal.log(f"Added new job ({newJob.job_name}) to queue.")
        return True

    def onQueueFinishedCallback(executor: unreal.MoviePipelineLinearExecutorBase, success: bool):
        """On queue finished callback.
        This is called when the queue finishes.
        The args are the executor and the success of the queue, and it cannot be modified.

        Args:
            executor (unreal.MoviePipelineLinearExecutorBase): The executor of the queue.
            success (bool): Whether the queue finished successfully.
        """
        mss = f"Render completed. Success: {success}"
        utils.log_msg_with_socket(executor, mss)

    def onIndividualJobFinishedCallback(inJob: unreal.MoviePipelineExecutorJob, success: bool):
        """On individual job finished callback.
        This is called when an individual job finishes.
        The args are the job and the success of the job, and it cannot be modified.

        Args:
            inJob (unreal.MoviePipelineExecutorJob): The job that finished.
            success (bool): Whether the job finished successfully.
        """

        # get class variable `Jobs` to get the index of the finished job
        jobs = CustomMoviePipeline.jobs

        job_name = inJob.job_name
        job_index = jobs.index(job_name) + 1
        mss = f"Individual job completed: {job_name}, {job_index}/{len(jobs)}"
        utils.log_msg_with_socket(CustomMoviePipeline.new_executor, mss)

    @classmethod
    def render_queue(
        cls,
        queue_finished_callback: Callable = onQueueFinishedCallback,
        individual_job_finished_callback: Callable = onIndividualJobFinishedCallback,
        executor: Optional[unreal.MoviePipelineLinearExecutorBase] = None,
    ) -> None:
        """Render the queue.
        This will render the queue.
        You can pass a callback function to be called when a job or the queue finishes.
        You can also pass a custom executor to use, or the default one will be used.

        Args:
            queue_finished_callback (Callable): The callback function to be called when the queue finishes.
            individual_job_finished_callback (Callable): The callback function to be called when an individual job finishes.
            executor (unreal.MoviePipelineLinearExecutorBase): The custom executor to use, or the default one will be used.
        """
        # check if there's jobs added to the queue
        if (len(cls.pipeline_queue.get_jobs()) == 0):
            unreal.log_error(
                "Open the Window > Movie Render Queue and add at least one job to use this example.")
            return

        # add job_name to class variable `Jobs` for monitoring progress in the individual job finished callback
        for job in cls.pipeline_queue.get_jobs():
            cls.jobs.append(job.job_name)

        # set Executor
        if executor:
            cls.new_executor = executor
        else:
            cls.new_executor = unreal.MoviePipelinePIEExecutor()

        # connect socket
        cls.new_executor.connect_socket(cls.host, cls.port)

        # set callbacks
        cls.new_executor.on_executor_finished_delegate.add_callable_unique(
            queue_finished_callback)
        cls.new_executor.on_individual_job_finished_delegate.add_callable_unique(
            individual_job_finished_callback)

        # render the queue
        cls.new_executor.execute(cls.pipeline_queue)
        cls.new_executor.send_socket_message("Start Render:")


def main():
    render_config_path = PLUGIN_ROOT / 'misc/render_config_common.yaml'
    render_config = CfgNode.load_yaml_with_base(render_config_path)
    CustomMoviePipeline.clear_queue()
    CustomMoviePipeline.add_job_to_queue_with_render_config(
        level='/Game/Maps/DefaultMap',
        level_sequence='/Game/Sequences/NewSequence',
        render_config=render_config
    )
    CustomMoviePipeline.render_queue()


if __name__ == "__main__":
    # from utils import loadRegistry
    # registry = loadRegistry(RenderQueue)
    # registry.register()

    main()
