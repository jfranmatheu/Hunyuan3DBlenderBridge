from bpy.types import Operator
from bpy.props import IntProperty


class H3D_OT_FilterGenerationPageIndexFirst(Operator):
    bl_idname = "h3d.filter_generation_page_index_first"
    bl_label = "Filter Generation Page Index First"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm_h3d = context.window_manager.h3d
        wm_h3d.ui_filter_generation_page_index = 0
        return {'FINISHED'}


class H3D_OT_FilterGenerationPageIndexLast(Operator):
    bl_idname = "h3d.filter_generation_page_index_last"
    bl_label = "Filter Generation Page Index Last"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn_h3d = context.scene.h3d
        wm_h3d = context.window_manager.h3d
        wm_h3d.ui_filter_generation_page_index = len(scn_h3d.generation_details) // wm_h3d.ui_filter_generation_page_size
        return {'FINISHED'}


class H3D_OT_FilterGenerationPageIndexPrev(Operator):
    bl_idname = "h3d.filter_generation_page_index_prev"
    bl_label = "Filter Generation Page Index Prev"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm_h3d = context.window_manager.h3d
        wm_h3d.ui_filter_generation_page_index -= 1
        return {'FINISHED'}


class H3D_OT_FilterGenerationPageIndexNext(Operator):
    bl_idname = "h3d.filter_generation_page_index_next"
    bl_label = "Filter Generation Page Index Next"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm_h3d = context.window_manager.h3d
        wm_h3d.ui_filter_generation_page_index += 1
        return {'FINISHED'}


class H3D_OT_SetFilterGenerationPageIndex(Operator):
    bl_idname = "h3d.set_filter_generation_page_index"
    bl_label = "Set Filter Generation Page Index"
    bl_options = {'REGISTER', 'UNDO'}

    page_index: IntProperty(name="Page Index", default=0)

    def execute(self, context):
        wm_h3d = context.window_manager.h3d
        wm_h3d.ui_filter_generation_page_index = self.page_index
        return {'FINISHED'}
