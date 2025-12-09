import bpy
from bpy.types import Operator
from bpy.props import IntProperty, BoolProperty, EnumProperty
from . import sfx_manager

_prev_node_counts = {}

class BLENDVOICE_OT_bake_animation(Operator):
    bl_idname = "blendvoice.bake_animation"
    bl_label = "Bake Animation"
    bl_description = "Bake animation with SFX feedback"
    bl_options = {'REGISTER', 'UNDO'}
    
    frame_start: IntProperty(
        name="起始帧",
        description="Bake 起始帧",
        default=1,
        min=1
    )
    
    frame_end: IntProperty(
        name="结束帧",
        description="Bake 结束帧",
        default=250,
        min=1
    )
    
    only_selected: BoolProperty(
        name="仅选中对象",
        description="仅对选中的对象进行 Bake",
        default=False
    )
    
    visual_keying: BoolProperty(
        name="视觉关键帧",
        description="使用视觉关键帧模式",
        default=False
    )
    
    clear_constraints: BoolProperty(
        name="清除约束",
        description="Bake 后清除约束",
        default=False
    )
    
    clear_parents: BoolProperty(
        name="清除父级",
        description="Bake 后清除父级关系",
        default=False
    )
    
    use_current_action: BoolProperty(
        name="使用当前动作",
        description="使用当前动作而非创建新动作",
        default=False
    )
    
    bake_types: EnumProperty(
        name="Bake 类型",
        description="要 Bake 的数据类型",
        items=[
            ('OBJECT', "Object", "Bake object transforms"),
            ('POSE', "Pose", "Bake pose bones"),
        ],
        default={'OBJECT'},
        options={'ENUM_FLAG'}
    )
    
    def invoke(self, context, event):
        self.frame_start = context.scene.frame_start
        self.frame_end = context.scene.frame_end
        self.only_selected = len(context.selected_objects) > 0
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "frame_start")
        layout.prop(self, "frame_end")
        layout.prop(self, "only_selected")
        layout.prop(self, "visual_keying")
        layout.prop(self, "clear_constraints")
        layout.prop(self, "clear_parents")
        layout.prop(self, "use_current_action")
        layout.prop(self, "bake_types")
    
    def execute(self, context):
        result = bpy.ops.nla.bake(
            frame_start=self.frame_start,
            frame_end=self.frame_end,
            only_selected=self.only_selected,
            visual_keying=self.visual_keying,
            clear_constraints=self.clear_constraints,
            clear_parents=self.clear_parents,
            use_current_action=self.use_current_action,
            bake_types=self.bake_types
        )
        
        if 'FINISHED' in result:
            sfx_manager.SFXManager.play(sfx_manager.SFXManager.BAKE_DONE)
            return {'FINISHED'}
        else:
            return result

def menu_func(self, context):
    self.layout.separator()
    self.layout.operator(BLENDVOICE_OT_bake_animation.bl_idname, text="Bake Animation (SFX)")

def on_render_complete(scene):
    sfx_manager.SFXManager.play(sfx_manager.SFXManager.RENDER_DONE)

def on_depsgraph_update(scene, depsgraph):
    for update in depsgraph.updates:
        if isinstance(update.id, bpy.types.NodeTree):
            node_tree = update.id
            current_count = len(node_tree.nodes)
            tree_id = id(node_tree)
            prev_count = _prev_node_counts.get(tree_id, 0)
            
            if current_count > prev_count:
                sfx_manager.SFXManager.play(sfx_manager.SFXManager.NODE_ADD)
            
            _prev_node_counts[tree_id] = current_count

def setup_handlers():
    bpy.app.handlers.render_complete.append(on_render_complete)
    bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update)

def remove_handlers():
    if on_render_complete in bpy.app.handlers.render_complete:
        bpy.app.handlers.render_complete.remove(on_render_complete)
    if on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)
    _prev_node_counts.clear()

def register():
    bpy.utils.register_class(BLENDVOICE_OT_bake_animation)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    remove_handlers()
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    try:
        bpy.utils.unregister_class(BLENDVOICE_OT_bake_animation)
    except:
        pass

