import bpy
from bpy.types import Scene, PropertyGroup, Image, ImageTexture
from bpy.props import PointerProperty, StringProperty, IntProperty, FloatProperty, BoolProperty, EnumProperty, CollectionProperty
from typing import List, Dict, Any

from ..utils.image import request_image_load


class H3D_PG_generation_image(PropertyGroup):
    def update_url(self, context):
        self.load_image()

    @property
    def texture(self) -> ImageTexture | None:
        tex = bpy.data.textures.get(f".{self.name}", None)
        if tex is None:
            tex = bpy.data.textures.new(name=f".{self.name}", type='IMAGE')
            tex.image = self.image
            tex.extension = 'CLIP'
        return tex

    def draw_preview(self, layout: bpy.types.UILayout, scale: int):
        if image := self.image:
            if image.preview:
                layout.template_icon(image.preview.icon_id, scale=scale)
            else:
                # layout.prop(self, "image", text="")
                layout.template_ID_preview(self, "image_ptr", hide_buttons=True)

    def load_image(self):
        def on_load_complete(image: Image):
            print(f"H3D UI: Image '{self.name}' load completed.")
            self.image = image
            self.filepath = image.filepath_raw
            image['url'] = self.url

        def on_load_error():
            print(f"H3D UI: Image '{self.name}' load failed.")

        if self.image_ptr is not None:
            return

        if self.filepath and os.path.exist(self.filepath) and os.path.isfile(self.filepath):
            self.image = bpy.data.images.load(self.filepath, check_existing=True)
            return

        if not self.url:
            return

        request_image_load(
            self.name,
            self.url,
            on_complete_callback=on_load_complete,
            on_error_callback=on_load_error
        )

    @property
    def image(self) -> Image | None:
        if self.image_ptr is not None:
            return self.image_ptr
        else:
            self.load_image()
        return None
    
    @image.setter
    def image(self, image: Image) -> None:
        if isinstance(image, Image) or image is None:
            self.image_ptr = image

    name: StringProperty(name="Name", default="")
    image_ptr: PointerProperty(type=Image, name="Image")
    url: StringProperty(name="URL", default="") # , update=update_url)
    filepath: StringProperty(name="Filepath", subtype='FILE_PATH', default="")


'''class H3D_PG_generation_model(PropertyGroup):
    name: StringProperty(name="Name", default="")
    local: StringProperty(name="URL", default="", subtype='FILE_PATH')
    remote: StringProperty(name="URL", default="")'''


class H3D_PG_intermediate_output(PropertyGroup):
    gif: PointerProperty(type=H3D_PG_generation_image, name="GIF")
    glb_url: StringProperty(name="GLB URL", default="")
    image: PointerProperty(type=H3D_PG_generation_image, name="Image")
    created: IntProperty(name="Created", default=0)

    def load_from_response(self, asset_id: str, response: Dict[str, Any]) -> None:
        self.gif.name = f"{asset_id}_result_intermediate"
        self.gif.url = response.get("gif_url", "")
        self.glb_url = response.get("glb_url", "")
        self.image.name = f"{asset_id}_input_intermediate"
        self.image.url = response.get("image_url", "")
        self.created = response.get("created", 0)


class H3D_PG_generation_url_result(PropertyGroup):
    glb: StringProperty(name="GLB URL", default="")
    gif: PointerProperty(type=H3D_PG_generation_image, name="GIF Image")
    obj: StringProperty(name="OBJ URL", default="")
    mtl: StringProperty(name="MTL URL", default="")
    image: PointerProperty(type=H3D_PG_generation_image, name="Image")
    geometryGif: StringProperty(name="Geometry GIF URL", default="")
    geometryGlb: StringProperty(name="Geometry GLB URL", default="")
    textureGif: StringProperty(name="Texture GIF URL", default="")
    textureObj: StringProperty(name="Texture OBJ URL", default="")
    textureGlb: StringProperty(name="Texture GLB URL", default="")
    obj_url: StringProperty(name="OBJ URL", default="")
    fbx: StringProperty(name="FBX URL", default="")

    def load_from_response(self, asset_id: str, response: Dict[str, Any]) -> None:
        if not response:
            return
        self.glb = response.get("glb", "")
        self.gif.name = f"{asset_id}_result"
        self.gif.url = response.get("gif", "")
        self.obj = response.get("obj", "")
        self.mtl = response.get("mtl", "")
        self.image.name = f"{asset_id}_input"
        self.image.url = response.get("image_url", "")
        self.geometryGif = response.get("geometryGif", "")
        self.geometryGlb = response.get("geometryGlb", "")
        self.textureGif = response.get("textureGif", "")
        self.textureObj = response.get("textureObj", "")
        self.textureGlb = response.get("textureGlb", "")
        self.obj_url = response.get("obj_url", "")
        self.fbx = response.get("fbx", "")

class H3D_PG_generation_result(PropertyGroup):
    name: StringProperty(name="Name", default="")  # match task_id!!! used for dict like search.
    task_id: StringProperty(name="Task ID", default="")
    asset_id: StringProperty(name="Asset ID", default="")
    status: EnumProperty(name="Status", default="wait", items=[
        ("wait", "Wait", "Wait", 'STRIP_COLOR_03', 0),
        ("fail", "Failed", "Failed", 'STRIP_COLOR_01', 1),
        ("processing", "Processing", "Processing", 'STRIP_COLOR_05', 2),
        ("success", "Success", "Success", 'STRIP_COLOR_04', 3),
    ])
    progress: FloatProperty(name="Progress", default=0.0, min=0.0, max=100.0, subtype="PERCENTAGE")
    progress_geometry: FloatProperty(name="Progress Geometry", default=0.0, min=0.0, max=100.0, subtype="PERCENTAGE")
    progress_texture: FloatProperty(name="Progress Texture", default=0.0, min=0.0, max=100.0, subtype="PERCENTAGE")
    created_at: IntProperty(name="Created At", default=0)
    updated_at: IntProperty(name="Updated At", default=0)
    url_result: PointerProperty(type=H3D_PG_generation_url_result, name="Result")
    intermediate_output: PointerProperty(type=H3D_PG_intermediate_output, name="Intermediate Result")

    # User data.
    fav: BoolProperty(name="Fav", default=False)
    saved: BoolProperty(name="Saved", default=False)

    def load_from_response(self, response: Dict[str, Any]) -> None:
        self.task_id = response.get("taskId", "")
        self.asset_id = response.get("assetId", "")
        self.status = response.get("status", "wait")
        self.created_at = response.get("createdAt", 0)
        self.updated_at = response.get("updatedAt", 0)
        self.progress = response.get("progress", 0.0)
        self.progress_geometry = response.get("progressGeometry", 0.0)
        self.progress_texture = response.get("progressTexture", 0.0)

        url_data = response.get("urlResult", {})
        self.url_result.load_from_response(self.asset_id, url_data)

        intermediate_data = response.get("intermediate_outputs", {})
        if intermediate_data and "geometry" in intermediate_data:
            self.intermediate_output.load_from_response(self.asset_id, intermediate_data["geometry"])

    def save(self, context: bpy.types.Context) -> None:
        pass


class H3D_PG_generation_details(PropertyGroup):
    name: StringProperty(name="Name", default="") # match creation_id!!! used for dict like search.
    user_id: StringProperty(name="User ID", default="")
    creation_id: StringProperty(name="Creation ID", default="", update=lambda self, context: setattr(self, "name", self.creation_id))
    scene_type: StringProperty(name="Scene Type", default="playGround3D-2.0")
    model_type: StringProperty(name="Model Type", default="modelCreationV2.5")
    prompt: StringProperty(name="Prompt", default="")
    prompt_image: PointerProperty(type=Image, name="Prompt Image")
    title: StringProperty(name="Title", default="")
    style: StringProperty(name="Style", default="")
    count: IntProperty(name="Count", default=4)
    status: EnumProperty(name="Status", default="wait", items=[
        ("wait", "Wait", "Wait", 'STRIP_COLOR_03', 0),
        ("fail", "Failed", "Failed", 'STRIP_COLOR_01', 1),
        ("processing", "Processing", "Processing", 'STRIP_COLOR_05', 2),
        ("success", "Success", "Success", 'STRIP_COLOR_04', 3),
    ])
    wait_time: IntProperty(name="Wait Time", default=0)
    trace_id: StringProperty(name="Trace ID", default="")
    task_id: StringProperty(name="Task ID", default="")
    created_at: IntProperty(name="Created At", default=0)
    updated_at: IntProperty(name="Updated At", default=0)
    deleted_at: IntProperty(name="Deleted At", default=0)
    enable_pbr: BoolProperty(name="Enable PBR", default=True)
    motion_type: IntProperty(name="Motion Type", default=0)

    result: CollectionProperty(type=H3D_PG_generation_result)

    show_in_gen_ui: BoolProperty(name="Show in UI", default=False)
    expand_in_gen_ui: BoolProperty(name="Expanded in UI", default=False)

    def get_result(self, task_id: str, create: bool = True) -> H3D_PG_generation_result:
        generation_result = self.result.get(task_id)
        if generation_result:
            return generation_result

        for result in self.result:
            if result.task_id == task_id or result.name == task_id:
                return result

        if create:
            new_result = self.result.add()
            new_result.name = task_id
            return new_result

        return None

    def remove_result(self, id: str | int) -> None:
        if isinstance(id, str):
            res = self.get_result(id, create=False)
            if res is None:
                print(f"Error 'remove_result': Can't find result with id '{id}' in generation with id '{self.name}'")
            for i, result in enumerate(self.result):
                if result.name == id:
                    self.remove_result(i)
                    return
        elif isinstance(id, int):
            if id < 0 or id >= len(self.result):
                return
            self.result.remove(id)

    def load_from_response(self, response: Dict[str, Any]) -> None:
        def _load_result_data() -> None:
            nonlocal response
            for result_data in response.get("result", []):
                result_status = result_data.get('status', None)
                if result_status is not None and result_status == 'fail':
                    # Remove invalid results from generation.
                    gen_detail = self.get_result(result_data.get("taskId", ""), create=False)
                    if gen_detail is not None:
                        self.remove_result(gen_detail.name)
                        print("Removing result due to geometry issues")
                    return
                gen_detail = self.get_result(result_data.get("taskId", ""), create=True)
                if gen_detail is None:
                    continue
                gen_detail.load_from_response(result_data)

        if len(self.result) > 0 and self.creation_id == response.get("id", ""):
            self.status = response.get("status", self.status)
            _load_result_data()
            self.updated_at = response.get("updatedAt", self.updated_at)
            self.wait_time = response.get("waitTime", self.wait_time)
            return

        self.creation_id = response.get("id", "")
        self.user_id = response.get("userId", "")
        self.scene_type = response.get("sceneType", "playGround3D-2.0")
        self.model_type = response.get("modelType", "modelCreationV2.5")
        self.prompt = response.get("prompt", "")
        self.title = response.get("title", "")
        self.style = response.get("style", "")
        self.count = response.get("n", 4)
        self.status = response.get("status", "wait")
        self.wait_time = response.get("waitTime", 0)
        self.trace_id = response.get("traceId", "")
        self.created_at = response.get("createdAt", 0)
        self.updated_at = response.get("updatedAt", 0)
        self.deleted_at = response.get("deletedAt", 0)
        self.enable_pbr = response.get("enable_pbr", True)
        self.motion_type = response.get("motionType", 0)

        _load_result_data()


class H3D_SCN_Properties(PropertyGroup):
    generation_details: CollectionProperty(type=H3D_PG_generation_details)
    
    def new_generation(self, creation_id: str) -> H3D_PG_generation_details:
        new_generation = self.generation_details.add()
        new_generation.creation_id = creation_id
        new_generation.show_in_gen_ui = True  # new generation should be shown in the generations UI.
        new_generation.expand_in_gen_ui = True  # new generation should be expanded in the generations UI.
        return new_generation

    def get_generation(self, creation_id: str) -> H3D_PG_generation_details:
        return self.generation_details.get(creation_id)
    
    def remove_generation(self, generation_id: str | int):
        if isinstance(generation_id, int):
            if generation_id < 0:
                return
            if generation_id >= len(self.generation_details):
                return
            self.generation_details.remove(generation_id)
        elif isinstance(generation_id, str):
            for index, gen in enumerate(self.generation_details):
                if gen.name == generation_id:
                    return self.remove_generation(index)


# --- Type Hints ---

class GenerationImage:
    image: Image
    url: str
    texture: ImageTexture | None

    def draw_preview(self, layout: bpy.types.UILayout, scale: int): pass

class IntermediateOutput:
    gif: GenerationImage
    glb_url: str
    image: GenerationImage
    created: int

    def load_from_response(self, response: Dict[str, Any]) -> None: pass

class GenerationUrlResult:
    glb: str
    gif: GenerationImage
    obj: str
    mtl: str
    image: GenerationImage
    geometryGif: str
    geometryGlb: str
    textureGif: str
    textureObj: str
    textureGlb: str
    obj_url: str
    fbx: str
    
    def load_from_response(self, response: Dict[str, Any]) -> None: pass

class GenerationResult:
    name: str
    task_id: str
    asset_id: str
    status: str
    createdAt: int
    updatedAt: int
    progress: float
    progress_geometry: float
    progress_texture: float
    url_result: GenerationUrlResult
    intermediate_output: IntermediateOutput
    
    fav: bool
    saved: bool
    
    def save(self, context: bpy.types.Context) -> None: pass
    
    def load_from_response(self, response: Dict[str, Any]) -> None: pass

class GenerationDetails:
    name: str
    creation_id: str
    scene_type: str
    model_type: str
    prompt: str
    prompt_image: Image
    title: str
    style: str
    count: int
    status: str
    wait_time: int
    trace_id: str
    task_id: str
    created_at: int
    updated_at: int
    deleted_at: int
    enable_pbr: bool
    motion_type: int
    result: List[GenerationResult] | Dict[str, GenerationResult]

    show_in_gen_ui: bool
    expand_in_gen_ui: bool

    def get_result(self, task_id: str, create: bool = True) -> GenerationResult: pass
    def remove_result(self, id: str | int) -> None: pass

    def load_from_response(self, response: Dict[str, Any]) -> None: pass

class SCN_Properties:
    generation_details: List[GenerationDetails] | Dict[str, GenerationDetails]
    
    def new_generation(self, creation_id: str) -> GenerationDetails: pass
    def get_generation(self, creation_id: str) -> GenerationDetails: pass
    def remove_generation(self, generation_id: str | int) -> None: pass


# --- Register and unregister ---

def register():
    Scene.h3d = PointerProperty(type=H3D_SCN_Properties)

def unregister():
    if hasattr(Scene, "h3d"):
        del Scene.h3d
