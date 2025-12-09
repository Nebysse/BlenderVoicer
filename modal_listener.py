import bpy
from . import sfx_manager

_keymap_items = []

def on_keymap_update():
    wm = bpy.context.window_manager
    if not wm:
        return
    kc = wm.keyconfigs.addon
    if not kc:
        return
    
    km = kc.keymaps.new(name='Window', space_type='EMPTY')
    kmi = km.keymap_items.new("blendvoice.sidebar_sfx", 'N', 'PRESS')
    _keymap_items.append((km, kmi))

def start_modal():
    if bpy.context.window_manager:
        on_keymap_update()
    else:
        bpy.app.timers.register(lambda: on_keymap_update(), first_interval=0.1)

def stop_modal():
    for km, kmi in _keymap_items:
        km.keymap_items.remove(kmi)
    _keymap_items.clear()

class BLENDVOICE_OT_sidebar_sfx(bpy.types.Operator):
    bl_idname = "blendvoice.sidebar_sfx"
    bl_label = "Sidebar SFX"
    
    def execute(self, context):
        sfx_manager.SFXManager.play(sfx_manager.SFXManager.SIDEBAR_OPEN)
        return {'PASS_THROUGH'}

def register():
    bpy.utils.register_class(BLENDVOICE_OT_sidebar_sfx)

def unregister():
    stop_modal()
    try:
        bpy.utils.unregister_class(BLENDVOICE_OT_sidebar_sfx)
    except:
        pass

