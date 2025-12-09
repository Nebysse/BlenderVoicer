import bpy
import os
import shutil
from bpy.props import StringProperty, BoolProperty, FloatProperty
from bpy.types import AddonPreferences, Operator
from . import sfx_manager

def _get_assets_user_sfx_path():
    addon_path = os.path.dirname(__file__)
    user_sfx_path = os.path.join(addon_path, "assets", "user_sfx")
    os.makedirs(user_sfx_path, exist_ok=True)
    return user_sfx_path

class BLENDVOICE_OT_select_sfx_file(Operator):
    bl_idname = "blendvoice.select_sfx_file"
    bl_label = "选择音效文件"
    bl_description = "选择音效文件 (WAV/OGG)"
    
    filepath: StringProperty(
        name="文件路径",
        description="选择音效文件 (支持 WAV 或 OGG 格式)",
        maxlen=1024,
        subtype='FILE_PATH'
    )
    
    event_type: StringProperty()
    
    filter_glob: StringProperty(
        default='*.wav;*.ogg',
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        if not self.filepath:
            return {'CANCELLED'}
        
        filepath_lower = self.filepath.lower()
        if not (filepath_lower.endswith('.wav') or filepath_lower.endswith('.ogg')):
            self.report({'ERROR'}, "仅支持 WAV 或 OGG 格式")
            return {'CANCELLED'}
        
        if not os.path.exists(self.filepath):
            self.report({'ERROR'}, "文件不存在")
            return {'CANCELLED'}
        
        event_file_map = {
            sfx_manager.SFXManager.RENDER_DONE: "render_done",
            sfx_manager.SFXManager.BAKE_DONE: "bake_done",
            sfx_manager.SFXManager.NODE_ADD: "node_add",
            sfx_manager.SFXManager.SIDEBAR_OPEN: "sidebar",
        }
        
        event_name = event_file_map.get(self.event_type)
        if not event_name:
            return {'CANCELLED'}
        
        _, ext = os.path.splitext(self.filepath)
        user_sfx_path = _get_assets_user_sfx_path()
        target_filename = f"{event_name}{ext}"
        target_path = os.path.join(user_sfx_path, target_filename)
        
        try:
            shutil.copy2(self.filepath, target_path)
        except Exception as e:
            self.report({'ERROR'}, f"复制文件失败: {str(e)}")
            return {'CANCELLED'}
        
        prefs = context.preferences.addons[__name__.split('.')[0]].preferences
        
        if self.event_type == sfx_manager.SFXManager.RENDER_DONE:
            prefs.sfx_render_path = target_filename
        elif self.event_type == sfx_manager.SFXManager.BAKE_DONE:
            prefs.sfx_bake_path = target_filename
        elif self.event_type == sfx_manager.SFXManager.NODE_ADD:
            prefs.sfx_node_path = target_filename
        elif self.event_type == sfx_manager.SFXManager.SIDEBAR_OPEN:
            prefs.sfx_sidebar_path = target_filename
        
        sfx_manager.SFXManager.reload_one(prefs, self.event_type)
        
        self.report({'INFO'}, f"音效已保存到插件目录")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class BLENDVOICE_OT_reset_defaults(Operator):
    bl_idname = "blendvoice.reset_defaults"
    bl_label = "重置为默认音效"
    bl_description = "将所有音效重置为默认值并删除自定义文件"
    
    def execute(self, context):
        prefs = context.preferences.addons[__name__.split('.')[0]].preferences
        
        user_sfx_path = _get_assets_user_sfx_path()
        filenames = [
            prefs.sfx_render_path,
            prefs.sfx_bake_path,
            prefs.sfx_node_path,
            prefs.sfx_sidebar_path,
        ]
        
        for filename in filenames:
            if filename:
                file_path = os.path.join(user_sfx_path, filename)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass
        
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
        description="渲染完成时播放的音效文件名",
        default="",
        maxlen=256
    )
    
    sfx_bake_path: StringProperty(
        name="Bake 完成音效",
        description="烘焙完成时播放的音效文件名",
        default="",
        maxlen=256
    )
    
    sfx_node_path: StringProperty(
        name="Node 添加音效",
        description="添加节点时播放的音效文件名",
        default="",
        maxlen=256
    )
    
    sfx_sidebar_path: StringProperty(
        name="Sidebar 音效",
        description="侧边栏打开时播放的音效文件名",
        default="",
        maxlen=256
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
        if self.sfx_render_path:
            row.label(text=self.sfx_render_path, icon='SOUND')
        else:
            row.label(text="(使用默认)", icon='INFO')
        op = row.operator("blendvoice.select_sfx_file", text="选择")
        op.event_type = sfx_manager.SFXManager.RENDER_DONE
        
        row = box.row()
        row.label(text="Bake 完成:")
        if self.sfx_bake_path:
            row.label(text=self.sfx_bake_path, icon='SOUND')
        else:
            row.label(text="(使用默认)", icon='INFO')
        op = row.operator("blendvoice.select_sfx_file", text="选择")
        op.event_type = sfx_manager.SFXManager.BAKE_DONE
        
        row = box.row()
        row.label(text="Node 添加:")
        if self.sfx_node_path:
            row.label(text=self.sfx_node_path, icon='SOUND')
        else:
            row.label(text="(使用默认)", icon='INFO')
        op = row.operator("blendvoice.select_sfx_file", text="选择")
        op.event_type = sfx_manager.SFXManager.NODE_ADD
        
        row = box.row()
        row.label(text="Sidebar 打开:")
        if self.sfx_sidebar_path:
            row.label(text=self.sfx_sidebar_path, icon='SOUND')
        else:
            row.label(text="(使用默认)", icon='INFO')
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

