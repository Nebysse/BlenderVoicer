bl_info = {
    "name": "Event SFX System",
    "author": "BlendVoice",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "Preferences > Add-ons",
    "description": "全局事件音效系统",
    "category": "System",
}

import bpy
from . import prefs
from . import sfx_manager
from . import handlers
from . import modal_listener

def register():
    prefs.register()
    sfx_manager.register()
    handlers.register()
    modal_listener.register()
    
    prefs_instance = bpy.context.preferences.addons[__name__].preferences
    sfx_manager.load_all_from_preferences(prefs_instance)
    handlers.setup_handlers()
    modal_listener.start_modal()

def unregister():
    handlers.remove_handlers()
    modal_listener.stop_modal()
    handlers.unregister()
    modal_listener.unregister()
    sfx_manager.unregister()
    prefs.unregister()

if __name__ == "__main__":
    register()

