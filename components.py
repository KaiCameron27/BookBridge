import tkinter as tk
from tkinter import ttk
import sys

# Color Palette
BG_DARK = "#F1F5F9"
BG_SURFACE = "#FFFFFF"
BG_SURFACE_LIGHT = "#E2E8F0"
TEXT_PRIMARY = "#0F172A"
TEXT_SECONDARY = "#64748B"
ACCENT_BLUE = "#3B82F6"
ACCENT_PURPLE = "#2563EB"
ACCENT_PURPLE_HOVER = "#1D4ED8"
BORDER_COLOR = "#CBD5E1"
SUCCESS_COLOR = "#10B981"
WARNING_COLOR = "#F59E0B"
ERROR_COLOR = "#EF4444"

# Fonts
FONT_FAMILY = "Segoe UI"
FONT_TITLE = (FONT_FAMILY, 18, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 14, "bold")
FONT_BODY = (FONT_FAMILY, 10)
FONT_BODY_BOLD = (FONT_FAMILY, 10, "bold")
FONT_CAPTION = (FONT_FAMILY, 9)
FONT_CAPTION_MUTED = (FONT_FAMILY, 9, "italic")

def apply_global_styles(root):
    """Configures global ttk style overrides to match dark mode theme."""
    style = ttk.Style(root)
    # Set theme to 'clam' to allow customization
    if sys.platform.startswith("win"):
        style.theme_use("clam")
        
    style.configure(".", background=BG_DARK, foreground=TEXT_PRIMARY, font=FONT_BODY)
    style.configure("TLabel", background=BG_DARK, foreground=TEXT_PRIMARY, font=FONT_BODY)
    style.configure("TFrame", background=BG_DARK)
    
    # Notebook/Tabs styling
    style.configure("TNotebook", background=BG_DARK, borderwidth=0)
    style.configure("TNotebook.Tab", background=BG_SURFACE, foreground=TEXT_SECONDARY, padding=[15, 8], font=FONT_BODY_BOLD)
    style.map("TNotebook.Tab",
              background=[("selected", BG_DARK), ("active", BG_SURFACE_LIGHT)],
              foreground=[("selected", ACCENT_PURPLE), ("active", TEXT_PRIMARY)])

class ModernButton(tk.Frame):
    """A clean, modern flat button with hover effects and rounded look (simulated)."""
    def __init__(self, parent, text, command=None, bg=ACCENT_PURPLE, fg=TEXT_PRIMARY, hover_bg=ACCENT_PURPLE_HOVER, width=12, padding=(10, 5), font=FONT_BODY_BOLD, **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        self.command = command
        self.bg = bg
        self.hover_bg = hover_bg
        
        self.label = tk.Label(
            self, 
            text=text, 
            bg=bg, 
            fg=fg, 
            font=font, 
            padx=padding[0], 
            pady=padding[1],
            cursor="hand2"
        )
        self.label.pack(fill="both", expand=True)
        
        # Event binding for hover effects
        self.label.bind("<Enter>", self._on_enter)
        self.label.bind("<Leave>", self._on_leave)
        self.label.bind("<Button-1>", self._on_click)
        
        # Outer container styling
        self.configure(padx=1, pady=1, bg=BORDER_COLOR) # Simulated border
        self.label.configure(bg=bg)

    def _on_enter(self, event):
        self.label.configure(bg=self.hover_bg)
        self.configure(bg=self.hover_bg)

    def _on_leave(self, event):
        self.label.configure(bg=self.bg)
        self.configure(bg=BORDER_COLOR)

    def _on_click(self, event):
        if self.command:
            self.command()
            
    def configure_text(self, text):
        self.label.configure(text=text)

class ModernInput(tk.Frame):
    """A styled entry widget with a clean border, dark background, and custom placeholder."""
    def __init__(self, parent, label_text="", placeholder="", show="", width=30, **kwargs):
        super().__init__(parent, bg=BG_DARK, **kwargs)
        self.placeholder = placeholder
        self.show_char = show
        
        if label_text:
            self.label = tk.Label(self, text=label_text, fg=TEXT_SECONDARY, bg=BG_DARK, font=FONT_CAPTION, anchor="w")
            self.label.pack(fill="x", pady=(0, 4))
            
        self.border_frame = tk.Frame(self, bg=BORDER_COLOR, padx=1, pady=1)
        self.border_frame.pack(fill="x")
        
        self.entry = tk.Entry(
            self.border_frame, 
            bg=BG_SURFACE, 
            fg=TEXT_PRIMARY, 
            insertbackground=TEXT_PRIMARY, 
            relief="flat", 
            bd=0, 
            font=FONT_BODY,
            width=width,
            highlightthickness=0
        )
        # Give internal padding
        self.entry.pack(fill="x", padx=8, pady=8)
        
        # Bind focus events for border highlights and placeholder
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        
        if placeholder:
            self.entry.insert(0, placeholder)
            self.entry.configure(fg=TEXT_SECONDARY)
            if self.show_char:
                self.entry.configure(show="")

    def _on_focus_in(self, event):
        self.border_frame.configure(bg=ACCENT_PURPLE)
        if self.placeholder and self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.configure(fg=TEXT_PRIMARY)
            if self.show_char:
                self.entry.configure(show=self.show_char)

    def _on_focus_out(self, event):
        self.border_frame.configure(bg=BORDER_COLOR)
        if self.placeholder and not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.configure(fg=TEXT_SECONDARY)
            if self.show_char:
                self.entry.configure(show="")

    def get(self):
        val = self.entry.get()
        if self.placeholder and val == self.placeholder:
            return ""
        return val

    def set(self, text):
        self.entry.delete(0, tk.END)
        self.entry.configure(fg=TEXT_PRIMARY)
        if self.show_char:
            self.entry.configure(show=self.show_char)
        self.entry.insert(0, text)
        
    def clear(self):
        self.entry.delete(0, tk.END)
        self._on_focus_out(None)

class ScrollableFrame(tk.Frame):
    """A highly reusable frame that supports vertical scrolling using a canvas."""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg=BG_DARK, *args, **kwargs)
        
        # Canvas and Scrollbar
        self.canvas = tk.Canvas(self, bg=BG_DARK, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        # Inner scrollable frame
        self.scrollable_frame = tk.Frame(self.canvas, bg=BG_DARK)
        
        # Configure binding
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Adjust canvas width to match scrollable frame when sized
        self.canvas.bind('<Configure>', self._configure_canvas)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack layouts
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Mousewheel scroll support
        self.bind_mouse_wheel(self)

    def _configure_canvas(self, event):
        # Update width of inner frame to match canvas
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def bind_mouse_wheel(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel)
        for child in widget.winfo_children():
            self.bind_mouse_wheel(child)

    def _on_mousewheel(self, event):
        # Windows mouse wheel scroll factor
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

class StarRating(tk.Frame):
    """A rating display that renders filled/empty stars (★ / ☆)."""
    def __init__(self, parent, rating=0, interactive=False, on_change=None, size=12, **kwargs):
        super().__init__(parent, bg=BG_DARK, **kwargs)
        self.rating = round(rating)
        self.interactive = interactive
        self.on_change = on_change
        self.size = size
        self.stars = []
        
        self.bg_color = kwargs.get("bg", BG_DARK)
        self.configure(bg=self.bg_color)
        
        self.render_stars()
        
    def render_stars(self):
        # Clear existing
        for star in self.stars:
            star.destroy()
        self.stars.clear()
        
        for i in range(1, 6):
            text = "★" if i <= self.rating else "☆"
            color = "#F59E0B" if i <= self.rating else TEXT_SECONDARY
            
            lbl = tk.Label(
                self, 
                text=text, 
                fg=color, 
                bg=self.bg_color, 
                font=(FONT_FAMILY, self.size),
                cursor="hand2" if self.interactive else "arrow"
            )
            lbl.pack(side="left", padx=1)
            
            if self.interactive:
                lbl.bind("<Button-1>", lambda event, r=i: self._set_rating(r))
                lbl.bind("<Enter>", lambda event, r=i: self._highlight_stars(r))
                lbl.bind("<Leave>", lambda event: self.render_stars())
                
            self.stars.append(lbl)

    def _set_rating(self, r):
        self.rating = r
        self.render_stars()
        if self.on_change:
            self.on_change(self.rating)

    def _highlight_stars(self, r):
        for i, star in enumerate(self.stars):
            idx = i + 1
            if idx <= r:
                star.configure(text="★", fg="#F59E0B")
            else:
                star.configure(text="☆", fg=TEXT_SECONDARY)

    def get_rating(self):
        return self.rating

class ToastNotification(tk.Toplevel):
    """A floating, self-destructing banner showing successes or errors."""
    def __init__(self, parent, message, is_error=False):
        super().__init__(parent)
        self.overrideredirect(True)
        self.configure(bg=BG_SURFACE)
        
        # Layout border
        border_color = ERROR_COLOR if is_error else SUCCESS_COLOR
        border_frame = tk.Frame(self, bg=border_color, padx=2, pady=2)
        border_frame.pack(fill="both", expand=True)
        
        inner_frame = tk.Frame(border_frame, bg=BG_SURFACE, padx=15, pady=10)
        inner_frame.pack(fill="both", expand=True)
        
        icon = "❌ " if is_error else "✨ "
        lbl = tk.Label(
            inner_frame, 
            text=icon + message, 
            fg=TEXT_PRIMARY, 
            bg=BG_SURFACE, 
            font=FONT_BODY_BOLD,
            wraplength=300,
            justify="left"
        )
        lbl.pack()
        
        # Position at top-right of main window
        self.update_idletasks()
        px = parent.winfo_x()
        py = parent.winfo_y()
        pw = parent.winfo_width()
        
        w = self.winfo_width()
        h = self.winfo_height()
        
        # Calculate screen coordinates
        x = px + pw - w - 20
        y = py + 50
        
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.attributes("-topmost", True)
        
        # Self-destruct after 3 seconds
        self.after(3000, self.destroy)