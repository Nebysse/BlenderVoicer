import bpy
import os
import aud

def _get_addon_name():
    import sys
    addon_path = os.path.dirname(__file__)
    init_file = os.path.join(addon_path, '__init__.py')
    for name, module in sys.modules.items():
        if hasattr(module, '__file__') and module.__file__ == init_file:
            return name.split('.')[0] if '.' in name else name
    return os.path.basename(addon_path)

_SUPPORTED_FORMATS = ('.wav', '.ogg')

def _is_supported_format(filepath):
    return filepath.lower().endswith(_SUPPORTED_FORMATS)

class SFXManager:
    RENDER_DONE = "RENDER_DONE"
    BAKE_DONE = "BAKE_DONE"
    NODE_ADD = "NODE_ADD"
    SIDEBAR_OPEN = "SIDEBAR_OPEN"
    SIDEBAR_CLOSE = "SIDEBAR_CLOSE"
    TOOLBAR_OPEN = "TOOLBAR_OPEN"
    TOOLBAR_CLOSE = "TOOLBAR_CLOSE"
    
    _cache = {}
    _device = None
    
    @classmethod
    def register(cls):
        cls._device = aud.Device()
        user_sfx_path = cls._get_user_sfx_path()
        os.makedirs(user_sfx_path, exist_ok=True)
    
    @classmethod
    def unregister(cls):
        cls._cache.clear()
        if cls._device:
            cls._device = None
    
    @classmethod
    def _get_default_path(cls, event_type):
        addon_path = os.path.dirname(__file__)
        defaults = {
            cls.RENDER_DONE: os.path.join(addon_path, "assets", "default_sfx", "render_done.wav"),
            cls.BAKE_DONE: os.path.join(addon_path, "assets", "default_sfx", "bake_done.wav"),
            cls.NODE_ADD: os.path.join(addon_path, "assets", "default_sfx", "node_add.wav"),
            cls.SIDEBAR_OPEN: os.path.join(addon_path, "assets", "default_sfx", "sidebar.wav"),
            cls.SIDEBAR_CLOSE: os.path.join(addon_path, "assets", "default_sfx", "sidebar.wav"),
            cls.TOOLBAR_OPEN: os.path.join(addon_path, "assets", "default_sfx", "sidebar.wav"),
            cls.TOOLBAR_CLOSE: os.path.join(addon_path, "assets", "default_sfx", "sidebar.wav"),
        }
        return defaults.get(event_type, "")
    
    @classmethod
    def _get_user_filename(cls, prefs_instance, event_type):
        path_map = {
            cls.RENDER_DONE: prefs_instance.sfx_render_path,
            cls.BAKE_DONE: prefs_instance.sfx_bake_path,
            cls.NODE_ADD: prefs_instance.sfx_node_path,
            cls.SIDEBAR_OPEN: prefs_instance.sfx_sidebar_path,
            cls.SIDEBAR_CLOSE: prefs_instance.sfx_sidebar_path,
            cls.TOOLBAR_OPEN: prefs_instance.sfx_sidebar_path,
            cls.TOOLBAR_CLOSE: prefs_instance.sfx_sidebar_path,
        }
        return path_map.get(event_type, "")
    
    @classmethod
    def _get_user_sfx_path(cls):
        addon_path = os.path.dirname(__file__)
        return os.path.join(addon_path, "assets", "user_sfx")
    
    @classmethod
    def _get_effective_path(cls, prefs_instance, event_type):
        user_filename = cls._get_user_filename(prefs_instance, event_type)
        if user_filename:
            user_sfx_path = cls._get_user_sfx_path()
            user_file_path = os.path.join(user_sfx_path, user_filename)
            if os.path.exists(user_file_path) and _is_supported_format(user_file_path):
                return user_file_path
        
        default_path = cls._get_default_path(event_type)
        if default_path and os.path.exists(default_path):
            return default_path
        return None
    
    @classmethod
    def _load_sound(cls, filepath):
        if not filepath or not os.path.exists(filepath):
            return None
        try:
            sound = aud.Sound(filepath)
            return sound
        except:
            return None
    
    @classmethod
    def load_all_from_preferences(cls, prefs_instance):
        cls._cache.clear()
        for event_type in [cls.RENDER_DONE, cls.BAKE_DONE, cls.NODE_ADD, cls.SIDEBAR_OPEN]:
            path = cls._get_effective_path(prefs_instance, event_type)
            if path:
                sound = cls._load_sound(path)
                if sound:
                    cls._cache[event_type] = sound
    
    @classmethod
    def reload_one(cls, prefs_instance, event_type):
        path = cls._get_effective_path(prefs_instance, event_type)
        if path:
            sound = cls._load_sound(path)
            if sound:
                cls._cache[event_type] = sound
            elif event_type in cls._cache:
                del cls._cache[event_type]
        elif event_type in cls._cache:
            del cls._cache[event_type]
    
    @classmethod
    def play(cls, event_type):
        addon_name = _get_addon_name()
        addon_prefs = bpy.context.preferences.addons.get(addon_name)
        if not addon_prefs:
            return
        prefs_instance = addon_prefs.preferences
        
        if not prefs_instance.sfx_enabled:
            return
        
        if event_type not in cls._cache:
            cls.reload_one(prefs_instance, event_type)
        
        if event_type in cls._cache and cls._device:
            sound = cls._cache[event_type]
            handle = cls._device.play(sound)
            handle.volume = prefs_instance.sfx_volume

