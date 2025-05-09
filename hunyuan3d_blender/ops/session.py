import requests

from bpy.types import Operator

from ..api.session import new_session, get_session, delete_session
from ..prefs import get_prefs


class H3D_OT_NewSession(Operator):
    bl_idname = "h3d.new_session"
    bl_label = "New Session"

    def execute(self, context):
        # Create a new session
        if global_session := get_session():
            self.report({'INFO'}, "Session already exists")
            print(f"Session already exists: {global_session}")
        else:
            global_session = new_session()
            self.report({'INFO'}, "New session created")
            print(f"New session created: {global_session}")
        return {'FINISHED'}


class H3D_OT_DeleteSession(Operator):
    bl_idname = "h3d.delete_session"
    bl_label = "Delete Session"

    def execute(self, context):
        delete_session()
        self.report({'INFO'}, "Session deleted")
        print("Session deleted")
        return {'FINISHED'}


class H3D_OT_LoginAsGuest(Operator):
    bl_idname = "h3d.login_as_guest"
    bl_label = "Login as Guest"

    @classmethod
    def poll(cls, context):
        return not get_session(create=False)

    def execute(self, context):
        raise NotImplementedError("Login as guest not implemented")
        if new_account():
            self.report({'INFO'}, "New guest account created")
            print("New guest account created")
        else:
            self.report({'ERROR'}, "Failed to create new guest account")
            print("Failed to create new guest account")
        return {'FINISHED'}


class H3D_OT_LoginWithCookies(Operator):
    bl_idname = "h3d.login_with_cookies"
    bl_label = "Login with Cookies"

    @classmethod
    def poll(cls, context):
        return not get_session(create=False)

    def execute(self, context):
        prefs = get_prefs()
        token = prefs.h3d_cookie_token
        userid = prefs.h3d_cookie_user_id
        source = 'web'
        if not token or not userid:
            self.report({'ERROR'}, "No cookies provided")
            return {'CANCELLED'}

        session = new_session()
        session.cookies.update({
            "hy_token": token,
            "hy_user": userid,
            "hy_source": source
        })
        self.report({'INFO'}, "Session created with cookies")
        print("Session created with cookies")
        return {'FINISHED'}
