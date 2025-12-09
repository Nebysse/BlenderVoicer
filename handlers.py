import bpy
from . import sfx_manager

_prev_bake_state = {}
_prev_node_counts = {}

def on_render_complete(scene):
    sfx_manager.SFXManager.play(sfx_manager.SFXManager.RENDER_DONE)

def on_depsgraph_update(scene, depsgraph):
    for update in depsgraph.updates:
        if update.is_updated_geometry or update.is_updated_transform:
            obj = update.id
            if isinstance(obj, bpy.types.Object) and obj.type == 'MESH':
                if hasattr(obj.data, 'use_bake'):
                    current_bake = obj.data.use_bake
                    obj_id = id(obj)
                    prev_bake = _prev_bake_state.get(obj_id, False)
                    
                    if prev_bake and not current_bake:
                        sfx_manager.SFXManager.play(sfx_manager.SFXManager.BAKE_DONE)
                    
                    _prev_bake_state[obj_id] = current_bake
        
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
    _prev_bake_state.clear()
    _prev_node_counts.clear()

def register():
    pass

def unregister():
    remove_handlers()

