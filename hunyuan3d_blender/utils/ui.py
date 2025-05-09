import bpy
from typing import Optional


def ui_tag_redraw(space_type: str, region_type: Optional[str] = None, context: Optional[bpy.types.Context] = None):
    if context is None:
        context = bpy.context
    for area in context.screen.areas:
        if area.type == space_type:
            if region_type is None:
                area.tag_redraw()
            else:
                for region in area.regions:
                    if region.type == region_type:
                        region.tag_redraw()

def ui_tag_refresh(space_type: str, region_type: str, context: Optional[bpy.types.Context] = None):
    if context is None:
        context = bpy.context
    for area in context.screen.areas:
        if area.type == space_type:
            for region in area.regions:
                if region.type == region_type:
                    region.tag_refresh_ui()
