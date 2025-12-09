import bpy
import os
from bpy.props import StringProperty, BoolProperty, FloatProperty
from bpy.types import AddonPreferences, Operator
from . import sfx_manager

class BLENDVOICE_OT_select_sfx_file(Operator):
    bl_idname = "blendvoice.select_sfx_file"
    bl_label = "选择 WAV 文件"
    bl_description = "选择音效文件"
    
    filepath: StringProperty(
        name="文件路径",
        description="选择 WAV 音效文件",
        maxlen=1024,
        subtype='FILE_PATH'
    )
    
    event_type: StringProperty()
    
    filter_glob: StringProperty(
        default='*.wav',
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        if not self.filepath:
            return {'CANCELLED'}
        
        if not self.filepath.lower().endswith('.wav'):
            self.report({'ERROR'}, "仅支持 WAV 格式")
            return {'CANCELLED'}
        
        prefs = context.preferences.addons[__name__.split('.')[0]].preferences
        
        if self.event_type == sfx_manager.SFXManager.RENDER_DONE:
            prefs.sfx_render_path = self.filepath
        elif self.event_type == sfx_manager.SFXManager.BAKE_DONE:
            prefs.sfx_bake_path = self.filepath
        elif self.event_type == sfx_manager.SFXManager.NODE_ADD:
            prefs.sfx_node_path = self.filepath
        elif self.event_type == sfx_manager.SFXManager.SIDEBAR_OPEN:
            prefs.sfx_sidebar_path = self.filepath
        
        sfx_manager.SFXManager.reload_one(prefs, self.event_type)
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class BLENDVOICE_OT_reset_defaults(Operator):
    bl_idname = "blendvoice.reset_defaults"
    bl_label = "重置为默认音效"
    bl_description = "将所有音效路径重置为默认值"
    
    def execute(self, context):
        prefs = context.preferences.addons[__name__.split('.')[0]].preferences
        
        prefs.sfx_render_path = ""
        prefs.sfx_bake_path = ""
        prefs.sfx_node_path = ""
        prefs.sfx_sidebar_path = ""
        
        sfx_manager.SFXManager.load_all_from_preferences(prefs)
        
        self.report({'INFO'}, "已重置为默认音效")
        return {'FINISHED'}

class BLENDVOICE_AddonPreferences(AddonPreferences):
    bl_idname = __name__.split('.')[0]
    
    sfx_render_path: StringProperty(
        name="Render 完成音效",
        description="渲染完成时播放的音效文件路径",
        default="",
        subtype='FILE_PATH'
    )
    
    sfx_bake_path: StringProperty(
        name="Bake 完成音效",
        description="烘焙完成时播放的音效文件路径",
        default="",
        subtype='FILE_PATH'
    )
    
    sfx_node_path: StringProperty(
        name="Node 添加音效",
        description="添加节点时播放的音效文件路径",
        default="",
        subtype='FILE_PATH'
    )
    
    sfx_sidebar_path: StringProperty(
        name="Sidebar 音效",
        description="侧边栏打开时播放的音效文件路径",
        default="",
        subtype='FILE_PATH'
    )
    
    sfx_enabled: BoolProperty(
        name="启用音效",
        description="全局音效开关",
        default=True
    )
    
    sfx_volume: FloatProperty(
        name="音量",
        description="音效音量 (0.0 - 1.0)",
        default=0.5,
        min=0.0,
        max=1.0,
        subtype='FACTOR'
    )
    
    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "sfx_enabled")
        layout.prop(self, "sfx_volume")
        layout.separator()
        
        box = layout.box()
        box.label(text="事件音效设置:")
        
        row = box.row()
        row.label(text="Render 完成:")
        row.prop(self, "sfx_render_path", text="")
        op = row.operator("blendvoice.select_sfx_file", text="选择")
        op.event_type = sfx_manager.SFXManager.RENDER_DONE
        
        row = box.row()
        row.label(text="Bake 完成:")
        row.prop(self, "sfx_bake_path", text="")
        op = row.operator("blendvoice.select_sfx_file", text="选择")
        op.event_type = sfx_manager.SFXManager.BAKE_DONE
        
        row = box.row()
        row.label(text="Node 添加:")
        row.prop(self, "sfx_node_path", text="")
        op = row.operator("blendvoice.select_sfx_file", text="选择")
        op.event_type = sfx_manager.SFXManager.NODE_ADD
        
        row = box.row()
        row.label(text="Sidebar 打开:")
        row.prop(self, "sfx_sidebar_path", text="")
        op = row.operator("blendvoice.select_sfx_file", text="选择")
        op.event_type = sfx_manager.SFXManager.SIDEBAR_OPEN
        
        layout.separator()
        layout.operator("blendvoice.reset_defaults")

def register():
    bpy.utils.register_class(BLENDVOICE_OT_select_sfx_file)
    bpy.utils.register_class(BLENDVOICE_OT_reset_defaults)
    bpy.utils.register_class(BLENDVOICE_AddonPreferences)

def unregister():
    bpy.utils.unregister_class(BLENDVOICE_AddonPreferences)
    bpy.utils.unregister_class(BLENDVOICE_OT_reset_defaults)
    bpy.utils.unregister_class(BLENDVOICE_OT_select_sfx_file)

