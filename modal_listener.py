import bpy
from . import sfx_manager

_modal_handler = None
_sidebar_shortcut = None
_toolbar_shortcut = None

def parse_keymap_shortcuts():
    global _sidebar_shortcut, _toolbar_shortcut
    
    wm = bpy.context.window_manager
    if not wm:
        return
    
    kc = wm.keyconfigs.default
    
    for km_name in ['3D View', 'Window']:
        km = kc.keymaps.find(name=km_name)
        if not km:
            continue
        
        for kmi in km.keymap_items:
            if kmi.idname == 'SCREEN_OT_region_toggle':
                if kmi.properties.region_type == 'UI':
                    _sidebar_shortcut = {
                        'type': kmi.type,
                        'value': kmi.value,
                        'ctrl': kmi.ctrl,
                        'alt': kmi.alt,
                        'shift': kmi.shift,
                        'oskey': kmi.oskey
                    }
                elif kmi.properties.region_type == 'TOOLS':
                    _toolbar_shortcut = {
                        'type': kmi.type,
                        'value': kmi.value,
                        'ctrl': kmi.ctrl,
                        'alt': kmi.alt,
                        'shift': kmi.shift,
                        'oskey': kmi.oskey
                    }

def matches_shortcut(event, shortcut):
    if not shortcut:
        return False
    return (event.type == shortcut['type'] and
            event.value == shortcut['value'] and
            event.ctrl == shortcut['ctrl'] and
            event.alt == shortcut['alt'] and
            event.shift == shortcut['shift'] and
            event.oskey == shortcut['oskey'])


class BLENDVOICE_OT_ui_listener(bpy.types.Operator):
    bl_idname = "blendvoice.ui_listener"
    bl_label = "UI Listener"
    
    def modal(self, context, event):
        if not context.area or context.area.type != 'VIEW_3D':
            return {'PASS_THROUGH'}
        
        if event.value != 'PRESS':
            return {'PASS_THROUGH'}
        
        sidebar_match = matches_shortcut(event, _sidebar_shortcut)
        toolbar_match = matches_shortcut(event, _toolbar_shortcut)
        
        if sidebar_match:
            sfx_manager.SFXManager.play(sfx_manager.SFXManager.SIDEBAR_OPEN)
        
        if toolbar_match:
            sfx_manager.SFXManager.play(sfx_manager.SFXManager.TOOLBAR_OPEN)
        
        return {'PASS_THROUGH'}
    
    
    def execute(self, context):
        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

def start_modal():
    global _modal_handler
    if _modal_handler is None:
        parse_keymap_shortcuts()
        if bpy.context.window_manager:
            try:
                bpy.ops.blendvoice.ui_listener('INVOKE_DEFAULT')
                _modal_handler = True
            except:
                bpy.app.timers.register(lambda: start_modal(), first_interval=0.1)
        else:
            bpy.app.timers.register(lambda: start_modal(), first_interval=0.1)

def stop_modal():
    global _modal_handler
    _modal_handler = None

def register():
    bpy.utils.register_class(BLENDVOICE_OT_ui_listener)

def unregister():
    stop_modal()
    try:
        bpy.utils.unregister_class(BLENDVOICE_OT_ui_listener)
    except:
        pass
