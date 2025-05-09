from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty

import bpy
import webbrowser
import requests
import os
import time
import re
from typing import Optional
import pathlib
from urllib.parse import urlparse
from collections import deque
from threading import Thread
from shutil import move

from ..data import H3D_Data
from ..data.scn import GenerationDetails
from ..prefs import get_prefs
from ..utils import TimerManager


download_request_queue = deque()
thread = None
import_request_queue = deque()


saved_in_tempfiles: dict[str, str] = {}


def _thread_download_request():
    global download_request_queue
    while len(download_request_queue) > 0:
        asset_id, url, filepath, do_import = download_request_queue.popleft()
        success, filepath = download_model(url, filepath)
        if success and do_import:
            import_request_queue.append((asset_id, filepath))
        time.sleep(0.5)


def _timer_import_request():
    global thread, import_request_queue
    if thread is None or not thread.is_alive():
        return None
    
    while len(import_request_queue) > 0:
        asset_id, filepath = import_request_queue.popleft()
        import_model(asset_id, filepath)
    
    return 0.5


def import_model(name: str, filepath: str) -> bool:
    if os.path.exists(filepath):
        print(f"Attempting to import GLB: {filepath}")
        bpy.ops.import_scene.gltf(filepath=filepath)
        bpy.context.active_object.name = name
        return True
    else:
        print(f"ERROR: GLB file not found at {filepath}")
        return False


def download_model(url: str, download_path: Optional[str] = None) -> tuple[bool, str | None]:
    print(f"Attempting to download GLB from: {url}")
    
    global saved_in_tempfiles
    if url in saved_in_tempfiles:
        tempfilepath = saved_in_tempfiles[url]
        if os.path.exists(tempfilepath) and os.path.isfile(tempfilepath):
            if not download_path:
                # use cached, no need to re-download it lol.
                return True, download_path
            move(tempfilepath, download_path)
            # from tempfiles to actual user save directory path.
            return True, download_path

    attemps = 3
    while attemps > 0:
        try:
            response = requests.get(url, allow_redirects=True, timeout=30)
            response.raise_for_status()

            content_disposition = response.headers.get('content-disposition')
            filename = "downloaded_model.glb"
            if content_disposition:
                matches = re.findall(r'filename="?([^;"]+)"?', content_disposition)
                if matches:
                    filename = matches[0]
            else:
                parsed_url_obj = urlparse(url)
                if parsed_url_obj.path:
                    path_part = parsed_url_obj.path
                    if path_part.endswith('.glb'):
                        filename = os.path.basename(path_part)
            
            if not filename.lower().endswith('.glb'):
                filename += ".glb"

            if not download_path:
                default_save_dir = bpy.app.tempdir if bpy.app.tempdir else os.getcwd()
                download_path = os.path.join(default_save_dir, filename)
            
            os.makedirs(os.path.dirname(download_path), exist_ok=True)

            print(f"Downloading to: {download_path}")
            with open(download_path, 'wb') as f:
                f.write(response.content)

            print(f"GLB downloaded successfully to {download_path}")
            return True, download_path
        except requests.exceptions.RequestException as e:
            print(f"Error downloading GLB: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        attemps -= 1

    return False, download_path



def request_download_model(asset_id: str, url: str, filepath: str | None = None, do_import: bool = False) -> None:
    global thread, download_request_queue

    download_request_queue.append((asset_id, url, filepath, do_import))

    if thread is None or not thread.is_alive():
        thread = Thread(target=_thread_download_request)
        thread.start()
        
    if not TimerManager.exists('import_model_request_timer'):
        TimerManager.add('import_model_request_timer', _timer_import_request)


class H3D_OT_save_result(Operator):
    bl_label = "Save Result"
    bl_idname = "h3d.save_result"
    bl_description = "Save the result"

    generation_id: StringProperty(name="Generation ID", default="", options={'SKIP_SAVE'})
    result_id: StringProperty(name="Result ID", default="", options={'SKIP_SAVE'})
    do_import: BoolProperty(name="Do Import", default=True, options={'SKIP_SAVE'})

    def execute(self, context):
        scn_h3d = H3D_Data.SCN(context)
        generation = scn_h3d.get_generation(self.generation_id)
        if generation is None:
            self.report({'ERROR'}, "Generation not found")
            return {'CANCELLED'}
        result = generation.get_result(self.result_id)
        if result is None:
            self.report({'ERROR'}, "Result not found")
            return {'CANCELLED'}
        if result.url_result.glb == "":
            self.report({'ERROR'}, "Result has no GLB URL")
            return {'CANCELLED'}

        prefs = get_prefs()
        save_dirpath = prefs.generations_save_dirpath
        dirpath = pathlib.Path(save_dirpath) / generation.creation_id

        glb_url = result.url_result.glb
        filepath = str(dirpath / f"{result.asset_id}.glb")
        if not self.do_import:
            success, _output = download_model(
                glb_url,
                filepath,
            )
            if not success:
                return {'CANCELLED'}
        else:
            request_download_model(
                result.asset_id,
                glb_url,
                filepath,
                self.do_import
            )

        images = (
            # result.url_result.image.image,  # same as `intermediate_output.image.image`
            result.url_result.gif.image,
            result.intermediate_output.image.image,
            result.intermediate_output.gif.image,
        )
        for image in images:
            if image:
                image.save(filepath=str(dirpath / f"{image.name}.{image.file_format.lower()}"), save_copy=False)
        result.saved = True
        return {'FINISHED'}


class H3D_OT_discard_result(Operator):
    bl_label = "Discard Result"
    bl_idname = "h3d.discard_result"
    bl_description = "Discard the result"

    generation_id: StringProperty(name="Generation ID", default="", options={'SKIP_SAVE'})
    result_id: StringProperty(name="Result ID", default="", options={'SKIP_SAVE'})

    def execute(self, context):
        scn_h3d = H3D_Data.SCN(context)
        generation = scn_h3d.get_generation(self.generation_id)
        if generation is None:
            self.report({'ERROR'}, "Generation not found")
            return {'CANCELLED'}
        result = generation.get_result(self.result_id)
        if result is None:
            self.report({'ERROR'}, "Result not found")
            return {'CANCELLED'}
        images = (
            result.url_result.image.image_ptr,
            result.url_result.gif.image_ptr,
            result.intermediate_output.image.image_ptr,
            result.intermediate_output.gif.image_ptr,
        )
        for image in images:
            if image is None:
                continue
            bpy.data.images.remove(image, do_unlink=True, do_ui_user=True)
        generation.remove_result(self.result_id)
        return {'FINISHED'}


class H3D_OT_import_result_model(Operator):
    bl_label = "Import Result Model"
    bl_idname = "h3d.import_result_model"
    bl_description = "Import the result model"

    generation_id: StringProperty(name="Generation ID", default="", options={'SKIP_SAVE'})
    result_id: StringProperty(name="Result ID", default="", options={'SKIP_SAVE'})

    def execute(self, context):
        scn_h3d = H3D_Data.SCN(context)
        generation = scn_h3d.get_generation(self.generation_id)
        if generation is None:
            self.report({'ERROR'}, "Generation not found")
            return {'CANCELLED'}
        result = generation.get_result(self.result_id)
        if result is None:
            self.report({'ERROR'}, "Result not found")
            return {'CANCELLED'}

        if not result.saved:
            # Dont use preferences but temp dir by default.
            if result.url_result.glb:
                request_download_model(
                    result.asset_id,
                    result.url_result.glb,
                    None,
                    True
                )
        else:
            prefs = get_prefs()
            save_dirpath = prefs.generations_save_dirpath
            dirpath = pathlib.Path(save_dirpath) / generation.creation_id
            filepath = str(dirpath / f"{result.asset_id}.glb")
            if not os.path.exists(filepath):
                if result.url_result.glb:
                    request_download_model(
                        result.asset_id,
                        result.url_result.glb,
                        filepath,
                        True
                    )
                    return {'FINISHED'}
                else:
                    self.report({'ERROR'}, "Result not found")
                    return {'CANCELLED'}

            bpy.ops.import_scene.gltf(filepath=filepath)
        return {'FINISHED'}


def purge_invalid_generations():
    h3d_scn = H3D_Data.SCN()
    to_remove_generations: list[GenerationDetails] = []
    for generation in h3d_scn.generation_details:
        if generation.status in {'wait', 'processing'}:
            to_remove_generations.append(generation)

    if len(to_remove_generations) == 0:
        return

    print("Purging invalid AI generations...")

    for gen in to_remove_generations:
        for result in gen.result:
            bpy.ops.discard_result(generation_id=gen.name, result_id=result.name)
        h3d_scn.remove_generation(gen.name)


def register():
    TimerManager.add('purge_invalid_generations', purge_invalid_generations, first_interval=2.0)
