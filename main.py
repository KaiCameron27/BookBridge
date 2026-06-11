import sys
from gui import BookBridgeWindow
from components import apply_global_styles

def setup_dpi_awareness():
    """Настройка четкости шрифтов на Windows (High-DPI)"""
    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

def main():
    setup_dpi_awareness()
    
    # Инициализация приложения
    app = BookBridgeWindow()
    
    # Применение темы оформления
    apply_global_styles(app)
    
    app.mainloop()

if __name__ == "__main__":
    main()