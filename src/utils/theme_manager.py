class ThemeManager:
    LIGHT_THEME = {
        'bg': '#ffffff',
        'fg': '#000000',
        'accent': '#007bff',
        'frame_bg': '#f8f9fa',
        'button_bg': '#e9ecef',
        'button_active': '#007bff',
        'button_pressed': '#0056b3',
        'process_colors': [
            '#FF9999', '#66B2FF', '#99FF99', '#FFCC99',
            '#FF99CC', '#99FFCC', '#FFB366', '#FF99FF'
        ],
        'gantt_bg': '#ffffff',
        'gantt_grid': '#e9ecef',
        'text_bg': '#ffffff',
        'text_fg': '#000000',
        'header_bg': '#007bff',
        'header_fg': '#ffffff',
        'selection_bg': '#007bff',
        'selection_fg': '#ffffff',
        'tree_alt_bg': '#f8f9fa',
        'scale_bg': '#e9ecef',
        'scale_trough': '#007bff',
        'menu_bg': '#ffffff',
        'menu_fg': '#000000',
        'menu_active_bg': '#007bff',
        'menu_active_fg': '#ffffff',
        'label_bg': '#ffffff',
        'label_fg': '#000000'
    }
    
    DARK_THEME = {
        'bg': '#2b2b2b',
        'fg': '#ffffff',
        'accent': '#3399ff',
        'frame_bg': '#363636',
        'button_bg': '#404040',
        'button_active': '#3399ff',
        'button_pressed': '#1a75ff',
        'process_colors': [
            '#FF5D5D', '#3399FF', '#66FF66', '#FFB366',
            '#FF66B2', '#66FFE6', '#FF944D', '#FF66FF'
        ],
        'gantt_bg': '#2b2b2b',
        'gantt_grid': '#404040',
        'text_bg': '#363636',
        'text_fg': '#ffffff',
        'header_bg': '#1a1a1a',
        'header_fg': '#ffffff',
        'selection_bg': '#3399ff',
        'selection_fg': '#ffffff',
        'tree_alt_bg': '#363636',
        'scale_bg': '#404040',
        'scale_trough': '#3399ff',
        'menu_bg': '#363636',
        'menu_fg': '#ffffff',
        'menu_active_bg': '#3399ff',
        'menu_active_fg': '#ffffff',
        'label_bg': '#363636',
        'label_fg': '#ffffff'
    }
    
    def __init__(self):
        self.current_theme = self.LIGHT_THEME
        self._theme_listeners = []
        
    def toggle_theme(self):
        self.current_theme = (
            self.DARK_THEME if self.current_theme == self.LIGHT_THEME
            else self.LIGHT_THEME
        )
        self._notify_listeners()
        
    def add_theme_listener(self, callback):
        """Add a callback to be notified when theme changes"""
        if callback not in self._theme_listeners:
            self._theme_listeners.append(callback)
            
    def remove_theme_listener(self, callback):
        """Remove a theme change callback"""
        if callback in self._theme_listeners:
            self._theme_listeners.remove(callback)
            
    def _notify_listeners(self):
        """Notify all listeners of theme change"""
        for callback in self._theme_listeners:
            try:
                callback(self.current_theme)
            except Exception as e:
                print(f"Error notifying theme listener: {e}")
                
    def get_color(self, key):
        return self.current_theme.get(key)
        
    def get_process_color(self, index):
        colors = self.current_theme['process_colors']
        return colors[index % len(colors)]
