import os
import tempfile

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, IntProperty, BoolProperty
from collections import deque
from ..api.h3d import generate_3d_model, generate_3d_model_from_image, get_creation_details
from ..utils import TimerManager
from ..data import H3D_Data
from ..data.scn import GenerationDetails
from ..utils.ui import ui_tag_redraw


currently_processing_count = 0
generation_queue = deque()
timer_id = "generation_timer"
running_generations: dict[str, GenerationDetails] = {}


def get_all_running_generations() -> dict[str, GenerationDetails]:
    global running_generations
    return running_generations

def get_queue_count() -> int:
    global generation_queue
    return len(generation_queue)

def get_currently_processing_count() -> int:
    global currently_processing_count
    return currently_processing_count


def generation_timer():
    global currently_processing_count, generation_queue, running_generations
    if currently_processing_count < 3:
        if len(generation_queue) > 0:
            data = generation_queue.popleft()
            generation_type = data.pop("generation_type", "TEXT_TO_3D")
            temp_filepath = data.pop("temp_filepath", "")
            creation_id = None
            try:
                if generation_type == "IMAGE_TO_3D":
                    creation_id = generate_3d_model_from_image(**data)
                else:
                    creation_id = generate_3d_model(**data)
            finally:
                if temp_filepath:
                    try:
                        os.remove(temp_filepath)
                    except OSError:
                        pass

            if creation_id:
                currently_processing_count += 1
                h3d_scn = H3D_Data.SCN()
                running_generations[creation_id] = h3d_scn.new_generation(creation_id)
            else:
                print("Failed to generate 3D model")
                return 4.0

    if currently_processing_count == 0:
        return None

    # get all generation details
    completed_generations = []
    invalid_generations = []
    for creation_id, generation in running_generations.items():
        creation_details = get_creation_details(creation_id)
        if creation_details is None:
            continue
        generation.load_from_response(creation_details)
        if generation.status == "success":
            completed_generations.append(creation_id)
            currently_processing_count -= 1
        if generation.status == 'fail':
            invalid_generations.append(creation_id)
            currently_processing_count -= 1

    for creation_id in completed_generations:
        running_generations.pop(creation_id)

    for creation_id in invalid_generations:
        running_generations.pop(creation_id)
        h3d_scn = H3D_Data.SCN()
        h3d_scn.remove_generation(creation_id)

    # update UI
    ui_tag_redraw("VIEW_3D", "UI")

    return 4.0


class H3D_OT_TextTo3D(Operator):
    bl_idname = "h3d.text_to_3d"
    bl_label = "Text to 3D"

    prompt: StringProperty(name="Prompt", default="")
    style: StringProperty(name="Style", default="")
    count: IntProperty(name="Count", default=4, min=1)
    use_pbr: BoolProperty(name="PBR", default=True)

    def execute(self, context):
        wm_h3d = H3D_Data.WM(context)
        if wm_h3d.h3d_generation_type == 'IMAGE_TO_3D':
            image = wm_h3d.h3d_generation_image
            image_filepath, temp_filepath, cache_keys = self.get_image_filepath(image)
            if not image_filepath:
                self.report({'ERROR'}, "Select an image with a valid file path")
                return {'CANCELLED'}
            self.add_to_queue({
                "generation_type": "IMAGE_TO_3D",
                "image_path": image_filepath,
                "temp_filepath": temp_filepath,
                "cache_keys": cache_keys,
                "title": image.name if image else "",
                "style": "",
                "count": 1,
                "enable_pbr": self.use_pbr,
                "enable_low_poly": False
            })
        else:
            if self.count == 0:
                return {'CANCELLED'}
            prompt: str = self.prompt
            prompt = prompt.strip()
            if prompt == "":
                return {'CANCELLED'}
            self.add_to_queue({
                "generation_type": "TEXT_TO_3D",
                "prompt": prompt,
                "title": prompt,
                "style": "" if self.style == 'DEFAULT' else self.style,
                "count": self.count,
                "enable_pbr": self.use_pbr,
                "enable_low_poly": False
            })
        return {'FINISHED'}

    def get_image_filepath(self, image: bpy.types.Image | None) -> tuple[str, str, list[str]]:
        if image is None:
            return "", "", []

        cache_keys = [f"image-name:{image.name}"]
        if image.filepath:
            cache_keys.append(f"image-path:{bpy.path.abspath(image.filepath)}")

        image_is_dirty = getattr(image, "is_dirty", False)
        image_is_packed = getattr(image, "packed_file", None) is not None

        if image.filepath and not image_is_dirty and not image_is_packed:
            filepath = bpy.path.abspath(image.filepath)
            if os.path.isfile(filepath):
                return filepath, "", cache_keys

        temp_file = tempfile.NamedTemporaryFile(
            prefix="hunyuan3d_image_",
            suffix=".png",
            delete=False,
        )
        temp_filepath = temp_file.name
        temp_file.close()

        original_filepath_raw = image.filepath_raw
        original_file_format = image.file_format
        try:
            image.filepath_raw = temp_filepath
            image.file_format = 'PNG'
            image.save()
            return temp_filepath, temp_filepath, cache_keys
        except Exception as e:
            print(f"Failed to save Blender image for upload: {e}")
            try:
                os.remove(temp_filepath)
            except OSError:
                pass
            return "", "", []
        finally:
            image.filepath_raw = original_filepath_raw
            image.file_format = original_file_format

    def add_to_queue(self, data: dict):
        generation_queue.append(data)
        global timer_id
        if TimerManager.exists(timer_id):
            return
        TimerManager.add(timer_id, generation_timer)
