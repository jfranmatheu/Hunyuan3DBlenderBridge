from bpy.types import Context
import bpy
from .scn import SCN_Properties
from .wm import WM_Properties


class H3D_Data:
    
    @staticmethod
    def SCN(context: Context | None = None) -> SCN_Properties:
        if context is None:
            context = bpy.context
        return context.scene.h3d
    
    @staticmethod
    def WM(context: Context | None = None) -> WM_Properties:
        if context is None:
            context = bpy.context
        return context.window_manager.h3d
