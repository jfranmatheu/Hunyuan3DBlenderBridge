from bpy.types import WindowManager, PropertyGroup, Image
from bpy.props import StringProperty, BoolProperty, PointerProperty, EnumProperty, IntProperty


class H3D_WM_Properties(PropertyGroup):
    h3d_login_type: EnumProperty(name="Login Type", default="GUEST", items=[
        ("GUEST", "Guest", "Login as guest"),
        ("COOKIES", "Cookies", "Login with cookies")])

    h3d_generation_type: EnumProperty(name="Generation Type", default="TEXT_TO_3D", items=[
        ("TEXT_TO_3D", "Text to 3D", "Generate 3D model from text"),
        ("IMAGE_TO_3D", "Image to 3D", "Generate 3D model from image")])
    h3d_generation_count: IntProperty(name="Generation Count", default=4, min=1, max=12)
    h3d_generation_style: EnumProperty(name="Generation Style", default="DEFAULT", items=[
        ("DEFAULT", "Default", "Generate realistic 3D model"),
        ("china_style", "China Style", "Generate china-style 3D model")])
    h3d_generation_prompt: StringProperty(name="Generation Prompt", default="")
    h3d_generation_image: PointerProperty(type=Image, name="Image")
    h3d_generation_use_pbr: BoolProperty(name="PBR", default=True)
    
    ui_image_preview_scale: EnumProperty(name="Image Preview Scale", default="AUTO", items=[
        ('AUTO', "Auto", "Auto"),
        ("2", "Small", "Small"),
        ("4", "Medium", "Medium"),
        ("6", "Large", "Large"),
        ("8", "Extra Large", "Extra Large"),
        ("10", "Huge", "Huge"),
    ])
    ui_image_preview_shading_type: EnumProperty(name="Shading Type", default='RENDER', items=(
        ('SOLID', "Solid", "Solid (white mesh) shading", 'SHADING_SOLID', 0),
        # SHADING_TEXTURE
        ('RENDER', "Render", "Display rendered shading", 'SHADING_RENDERED', 1),
    ))

    ui_filter_generation_status: EnumProperty(name="UI Filter Generation Status", default="ALL", items=[
        ("ALL", "All", "All", 'STRIP_COLOR_09', 0),
        ("wait", "Wait", "Wait", 'STRIP_COLOR_03', 1),
        ("fail", "Failed", "Failed", 'STRIP_COLOR_01', 2),
        ("processing", "Processing", "Processing", 'STRIP_COLOR_05', 3),
        ("success", "Success", "Success", 'STRIP_COLOR_04', 4),
    ])
    ui_filter_generation_page_order_invert: BoolProperty(name="Page Order Invert", default=False)

    def update_ui_filter_generation_page_index(self, context):
        if self.ui_filter_generation_page_index == 0:
            return
        scn_h3d = context.scene.h3d
        generation_count = len(scn_h3d.generation_details) - 1
        max_pages = generation_count // self.ui_filter_generation_page_size
        if self.ui_filter_generation_page_index > max_pages:
            self.ui_filter_generation_page_index = max_pages
        
    def update_ui_filter_generation_page_size(self, context):
        if self.ui_filter_generation_page_index != 0:
            self.ui_filter_generation_page_index = 0

    ui_filter_generation_page_index: IntProperty(name="UI Filter Generation Page Index", default=0, min=0, update=update_ui_filter_generation_page_index)
    ui_filter_generation_page_size: IntProperty(name="UI Filter Generation Page Size", default=10, min=1, max=30, update=update_ui_filter_generation_page_size)



# --- Type Hints ---

class WM_Properties:
    h3d_login_type: str
    h3d_generation_type: str
    h3d_generation_count: int
    h3d_generation_style: str
    h3d_generation_prompt: str
    h3d_generation_image: Image
    h3d_generation_use_pbr: bool
    
    ui_image_preview_scale: str
    ui_image_preview_shading_type: str
    ui_filter_generation_status: str
    ui_filter_generation_page_order_invert: bool
    ui_filter_generation_page_index: int
    ui_filter_generation_page_size: int


# --- Register and unregister ---

def register():
    WindowManager.h3d = PointerProperty(type=H3D_WM_Properties)

def unregister():
    if hasattr(WindowManager, "h3d"):
        del WindowManager.h3d
