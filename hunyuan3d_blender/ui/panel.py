import bpy
from bpy.types import Panel

from ..data import H3D_Data
from ..api.session import get_session
from ..ops.text_to_3d import get_currently_processing_count, get_queue_count
from ..utils.image import get_image_from_url
from ..prefs import get_prefs


class H3D_PT_Panel(Panel):
    bl_label = "Hunyuan 3D"
    bl_idname = "H3D_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AI'

    def draw(self, context):
        layout = self.layout
        header, login_subpanel = layout.panel('H3D_PT_login', default_closed=True)
        header.label(text="Login")
        if login_subpanel:
            self.draw_login(context, login_subpanel)

        session = get_session(create=False)
        if not session:
            return

        header, generation_subpanel = layout.panel('H3D_PT_generation', default_closed=True)
        header.label(text="Generation")
        if generation_subpanel:
            self.draw_generation(context, generation_subpanel)
        header, generation_details_subpanel = layout.panel('H3D_PT_generation_details', default_closed=True)
        header.label(text="Generation Details")
        if generation_details_subpanel:
            self.draw_generation_details(context, generation_details_subpanel)

    def draw_login(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        wm_h3d = H3D_Data.WM(context)
        prefs = get_prefs()

        # Choose between login as guest or with cookies.
        row = layout.row()
        row.prop(wm_h3d, "h3d_login_type", expand=True)

        if wm_h3d.h3d_login_type == 'COOKIES':
            layout.prop(prefs, "h3d_cookie_token")
            layout.prop(prefs, "h3d_cookie_user_id")
            row = layout.row()
            row.operator("h3d.login_with_cookies")
        else:
            layout.operator("h3d.login_as_guest")

        row = layout.row()
        if get_session(create=False):
            row.operator("h3d.delete_session")

    def draw_generation(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        wm_h3d = H3D_Data.WM()

        # 3D model generation.
        generation_box = layout.box().column()
        generation_box.row().prop(wm_h3d, "h3d_generation_type", expand=True)
        if wm_h3d.h3d_generation_type == 'TEXT_TO_3D':
            col = generation_box.column(align=True)
            char_count = len(wm_h3d.h3d_generation_prompt)
            if char_count > 150:
                col.alert = True
            col.label(text=f'Prompt - {char_count}/150 characters')
            col.prop(wm_h3d, "h3d_generation_prompt", text='')
            row = generation_box.row(heading='Style')
            row.prop(wm_h3d, "h3d_generation_style", text='')
            row.prop(wm_h3d, 'h3d_generation_use_pbr', text='PBR', toggle=True)
            generation_box.prop(wm_h3d, "h3d_generation_count", slider=True)
        elif wm_h3d.h3d_generation_type == 'IMAGE_TO_3D':
            generation_box.prop(wm_h3d, "h3d_generation_image")
            generation_box.prop(wm_h3d, 'h3d_generation_use_pbr')

        op = generation_box.operator("h3d.text_to_3d")
        op.prompt = wm_h3d.h3d_generation_prompt
        op.style = wm_h3d.h3d_generation_style
        op.count = wm_h3d.h3d_generation_count
        op.use_pbr = wm_h3d.h3d_generation_use_pbr

    def draw_generation_details(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        scn_h3d = H3D_Data.SCN(context)
        wm_h3d = H3D_Data.WM(context)
        
        reg_width = context.region.width
        
        box = layout.box()
        split = box.split(factor=0.5)
        process_count = get_currently_processing_count()
        queue_count = get_queue_count()
        split.label(text=f"Processing {process_count}")
        split.label(text=f"Queue {queue_count}")

        # --- Filter. ---
        filter_box = layout.box().row()
        filter_box.scale_y = 1.4
        filter_box.row().prop(wm_h3d, "ui_filter_generation_status", expand=False, text="")
        sub = filter_box.row()
        sub.scale_x = 1.2
        sub.prop(wm_h3d, "ui_filter_generation_page_order_invert", text="", toggle=True, icon='SORT_DESC' if wm_h3d.ui_filter_generation_page_order_invert else 'SORT_ASC')
        sub.prop(wm_h3d, 'ui_image_preview_shading_type', text='', expand=True, icon_only=True)
        sub.prop(wm_h3d, "ui_image_preview_scale", text="", expand=False, icon='IMAGE_DATA', icon_only=True)


        filter_status: str = wm_h3d.ui_filter_generation_status
        use_filter_status = filter_status != "ALL"
        
        current_page_index = wm_h3d.ui_filter_generation_page_index
        max_pages = len(scn_h3d.generation_details) // wm_h3d.ui_filter_generation_page_size

        generations = list(scn_h3d.generation_details)
        start_index = current_page_index * wm_h3d.ui_filter_generation_page_size
        end_index = min(start_index + wm_h3d.ui_filter_generation_page_size, len(generations))

        if not wm_h3d.ui_filter_generation_page_order_invert:
            generations = list(reversed(generations))
            
        generations = generations[start_index:end_index]
        
        # --- List of generations. ---
        if wm_h3d.ui_image_preview_scale == "AUTO":
            image_preview_scale = min(max(reg_width // 88, 2), 12)
        else:
            image_preview_scale = int(wm_h3d.ui_image_preview_scale)
            
        image_shading_type = wm_h3d.ui_image_preview_shading_type
        show_render_image = image_shading_type == 'RENDER'

        generation_col = layout.column(align=True)
        for gen_index, generation in enumerate(generations):
            if not generation.show_in_gen_ui:
                continue
            if use_filter_status and generation.status != filter_status:
                continue

            if gen_index > 0:
                generation_col.separator(factor=0.5)

            col = generation_col.column(align=True)

            title_box = col.row(align=True)
            sub = title_box.box()
            status_icon = bpy.types.UILayout.enum_item_icon(generation, "status", generation.status)
            sub.label(text="", icon_value=status_icon)
            sub.ui_units_x = 1.5
            row_left = title_box.box().row(align=False)
            row_left.alignment = 'EXPAND'
            row_left.prop(generation, 'expand_in_gen_ui', text=generation.title, icon='TRIA_DOWN' if generation.expand_in_gen_ui else 'TRIA_RIGHT', emboss=False)
            # row_right = title_box.row(align=False)
            # row_right.alignment = 'RIGHT'
            # TODO: add options/ops/menu here... applied to the generation/batch.

            if not generation.expand_in_gen_ui:
                continue

            gen_grid = generation_col.grid_flow(columns=2, align=True, even_columns=True, even_rows=True, row_major=True)

            # Results.
            for result in generation.result:
                if result.name == "":
                    continue
                
                result_box = gen_grid.box().column(align=True)
                # LEFT: (input image/generated image).
                # RIGHT: (preview render).
                row = result_box.row(align=False)
                # Left
                # Skip this condition since both images are the same...
                # if result.url_result.image.url and result.url_result.image.image:
                #     result.url_result.image.draw_preview(row, image_preview_scale)
                if result.intermediate_output.image.url and result.intermediate_output.image.image:
                    result.intermediate_output.image.draw_preview(row, image_preview_scale)
                else:
                    row.box().label(text="", icon='IMAGE_DATA')
                # Right
                if result.url_result.gif.url and result.url_result.gif.image and show_render_image:
                    result.url_result.gif.draw_preview(row, image_preview_scale)
                elif result.intermediate_output.gif.url and result.intermediate_output.gif.image:
                    result.intermediate_output.gif.draw_preview(row, image_preview_scale)
                else:
                    row.box().label(text="", icon='IMAGE_DATA')

                # Progress.
                if result.status in {"processing", "wait"}:
                    col = result_box.column(align=True)
                    col.prop(result, "progress", text="", slider=True)
                    row = col.row(align=False)
                    row.prop(result, "progress_geometry", text="", slider=True, icon='MESH_MONKEY')
                    row.prop(result, "progress_texture", text="", slider=True, icon='TPAINT_HLT')
                elif result.status == "fail":
                    col = result_box.column(align=True)
                    col.alert = True
                    col.label(text="Failed due to geometry issues", icon='ERROR')
                    op = col.operator("h3d.discard_result", text="Discard", icon='TRASH')
                    op.generation_id = generation.name
                    op.result_id = result.name
                elif result.status == "success":
                    actions_row = result_box.row(align=True)
                    if result.saved:
                        op = actions_row.operator("h3d.import_result_model", text="Import Model", icon='IMPORT')
                        op.generation_id = generation.name
                        op.result_id = result.name
                    else:
                        op = actions_row.operator("h3d.import_result_model", text="", icon='IMPORT')
                        op.generation_id = generation.name
                        op.result_id = result.name
                        actions_row.separator()
                        op = actions_row.operator("h3d.save_result", text="Save", icon='CURRENT_FILE')
                        op.generation_id = generation.name
                        op.result_id = result.name
                        op = actions_row.operator("h3d.discard_result", text="Discard", icon='TRASH')
                        op.generation_id = generation.name
                        op.result_id = result.name
                    actions_row.separator()
                    actions_row.prop(result, "fav", text="", icon='SOLO_ON' if result.fav else 'SOLO_OFF')

        # Filter.
        footer_col = layout.column(align=True)
        page_index_row = footer_col.row(align=True)
        page_index_row.emboss = 'PULLDOWN_MENU'
        left_row = page_index_row.box().row(align=True)
        left_row.alignment = 'LEFT'
        left_row.operator("h3d.filter_generation_page_index_first", text="", icon='TRIA_LEFT_BAR')
        left_row.operator("h3d.filter_generation_page_index_prev", text="", icon='TRIA_LEFT')
        left_row.separator(factor=0.5)
        middle_row = page_index_row.box().row(align=True)
        middle_row.alignment = 'EXPAND'

        # Calculate the number of page numbers to display
        # Assuming roughly 25px per page button + 25px for ellipses/spacing
        # Ensure at least 3 page numbers are shown (prev, current, next)
        # max_visible_pages = max(3, context.region.width // 50)
        # For now, let's stick to a simpler logic, will refine if needed.
        # Let's define a sensible default number of pages to show around current.
        pages_around_current = 2 # Shows X pages before and X pages after current

        # Determine the actual range of pages to display
        start_page_display = max(0, current_page_index - pages_around_current)
        end_page_display = min(max_pages, current_page_index + pages_around_current)

        # Adjust start and end if we are near the beginning or end
        if current_page_index < pages_around_current:
            end_page_display = min(max_pages, (pages_around_current * 2))
        if current_page_index > max_pages - pages_around_current:
            start_page_display = max(0, max_pages - (pages_around_current * 2))
        
        # Ensure we have at least 3 if possible (current, prev, next)
        if max_pages == 0: # single page
            op = middle_row.operator("h3d.set_filter_generation_page_index", text="0", depress=True)
            op.page_index = 0
        elif max_pages == 1: # two pages
            op = middle_row.operator("h3d.set_filter_generation_page_index", text="0", depress=(current_page_index == 0))
            op.page_index = 0
            op = middle_row.operator("h3d.set_filter_generation_page_index", text="1", depress=(current_page_index == 1))
            op.page_index = 1
        else: # 3 or more pages
            # Always show page 0
            if start_page_display > 0:
                op = middle_row.operator("h3d.set_filter_generation_page_index", text="0")
                op.page_index = 0
                if start_page_display > 1: # Add ellipsis if there's a gap
                    middle_row.label(text="...")

            # Display pages around current
            for i in range(start_page_display, end_page_display + 1):
                if i == 0 and start_page_display == 0: # Already handled by "Always show page 0"
                    # but ensure it's drawn if it's the current or only page in this loop
                    if i == current_page_index or (start_page_display == end_page_display):
                        op = middle_row.operator("h3d.set_filter_generation_page_index", text=f"{i}", depress=(i == current_page_index))
                        op.page_index = i
                    continue
                if i == max_pages and end_page_display == max_pages: # Will be handled by "Always show last page"
                     # but ensure it's drawn if it's the current
                    if i == current_page_index:
                        op = middle_row.operator("h3d.set_filter_generation_page_index", text=f"{i}", depress=(i == current_page_index))
                        op.page_index = i
                    continue

                op = middle_row.operator("h3d.set_filter_generation_page_index", text=f"{i}", depress=(i == current_page_index))
                op.page_index = i
            
            # Always show last page (max_pages)
            if end_page_display < max_pages:
                if end_page_display < max_pages - 1: # Add ellipsis if there's a gap
                    middle_row.label(text="...")
                op = middle_row.operator("h3d.set_filter_generation_page_index", text=f"{max_pages}", depress=(max_pages == current_page_index))
                op.page_index = max_pages

        right_row = page_index_row.box().row(align=True)
        right_row.alignment = 'RIGHT'
        right_row.separator(factor=0.5)
        right_row.operator("h3d.filter_generation_page_index_next", text="", icon='TRIA_RIGHT')
        right_row.operator("h3d.filter_generation_page_index_last", text="", icon='TRIA_RIGHT_BAR')

        _row = footer_col.row(align=False)
        _row.scale_y = .3
        _row.prop(wm_h3d, "ui_filter_generation_page_size", slider=True, text="")
