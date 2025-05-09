from bpy.types import AddonPreferences, WindowManager, PropertyGroup
from bpy.props import StringProperty, PointerProperty
import bpy

from pathlib import Path
import json

from .utils import TimerManager


config_path = Path(bpy.utils.user_resource('CONFIG'))
package_name_sort = __package__.split('.')[-1]
config_file = config_path / f"{package_name_sort}.json"


class H3D_Preferences(AddonPreferences):
    bl_idname = __package__

    def backup_prop(self, prop_name: str):
        if hasattr(self, prop_name):
            if not config_file.exists():
                return
            config_data = None
            with config_file.open('r') as f:
                raw_data = f.read()
                if raw_data != "":
                    config_data = json.loads(raw_data)
                if not config_data:
                    config_data = {}
            value = getattr(self, prop_name)
            with config_file.open('w') as f:
                config_data[prop_name] = value
                json.dump(config_data, f)

    generations_save_dirpath: StringProperty(name="Generations Save Directory", default="", subtype="DIR_PATH", update=lambda prefs, ctx: prefs.backup_prop('generations_save_dirpath'))
    h3d_cookie_token: StringProperty(name="Token", default="", subtype="PASSWORD", update=lambda prefs, ctx: prefs.backup_prop('h3d_cookie_token'))
    h3d_cookie_user_id: StringProperty(name="User ID", default="", update=lambda prefs, ctx: prefs.backup_prop('h3d_cookie_user_id'))

    def draw(self, context):
        layout = self.layout
        
        login_box = layout.box()
        login_box.prop(self, "h3d_cookie_token")
        login_box.prop(self, "h3d_cookie_user_id")

        layout.prop(self, "generations_save_dirpath")


def get_prefs() -> H3D_Preferences:
    return bpy.context.preferences.addons[__package__].preferences


def load_prefs_from_config_file():
    if not config_file.exists():
        return
    prefs = get_prefs()
    with config_file.open('r') as f:
        raw_data = f.read()
        if raw_data == "":
            return
        config_data = json.loads(raw_data)
        if not config_data:
            return
        prefs.generations_save_dirpath = config_data.get('generations_save_dirpath', '')
        prefs.h3d_cookie_token = config_data.get('h3d_cookie_token', '')
        prefs.h3d_cookie_user_id = config_data.get('h3d_cookie_user_id', '')


def register():
    if not config_file.exists():
        config_file.touch()
        with config_file.open('w') as f:
            f.write('{\n}')
    else:
        TimerManager.add('load_prefs_from_config_file', load_prefs_from_config_file)
