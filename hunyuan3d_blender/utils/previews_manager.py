'''import bpy.utils.previews


previews = None


class PreviewsManager:
    @staticmethod
    def load_icon_from_image(image: bpy.types.Image) -> bpy.types.Image:
        global previews
        if image.name not in previews:
            previews.load(image.name, image.filepath, 'IMAGE')
        return previews.get(image.name).icon_id


def register(self):
    global previews
    previews = bpy.utils.previews.new()

def unregister():
    global previews
    bpy.utils.previews.remove(previews)
    previews = None
'''