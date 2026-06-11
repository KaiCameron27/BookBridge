import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import database as db
import analytics
from components import (
    BG_DARK, BG_SURFACE, BG_SURFACE_LIGHT, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_BLUE, ACCENT_PURPLE, ACCENT_PURPLE_HOVER, BORDER_COLOR,
    SUCCESS_COLOR, WARNING_COLOR, ERROR_COLOR,
    FONT_FAMILY, FONT_TITLE, FONT_SUBTITLE, FONT_BODY, FONT_BODY_BOLD, FONT_CAPTION, FONT_CAPTION_MUTED,
    ModernButton, ModernInput, ScrollableFrame, StarRating, ToastNotification
)

class BookBridgeWindow(tk.Tk):
    """Main application window manager responsible for switching screens and session state."""
    def __init__(self):
        super().__init__()
        self.title("BookBridge - The Ultimate Booklovers Marketplace")
        self.geometry("1100x700")
        self.configure(bg=BG_DARK)
        self.minsize(1000, 600)
        
        # Initialize Database
        db.init_db()
        
        # Session State
        self.current_user = None
        
        # Screen Container
        self.container = tk.Frame(self, bg=BG_DARK)
        self.container.pack(fill="both", expand=True)
        
        # Initial Screen
        self.show_screen("login")

    def show_screen(self, screen_name):
        """Swaps the current screen inside the main container."""
        # Clear container
        for widget in self.container.winfo_children():
            widget.destroy()
            
        if screen_name == "login":
            screen = LoginScreen(self.container, self)
        elif screen_name == "register":
            screen = RegisterScreen(self.container, self)
        elif screen_name == "dashboard":
            screen = DashboardScreen(self.container, self)
        elif screen_name == "admin_dashboard":
            screen = AdminDashboardScreen(self.container, self)
        else:
            return
            
        screen.pack(fill="both", expand=True)

    def login_user(self, user, as_admin=False):
        """Sets the session user and redirects to the dashboard."""
        self.current_user = dict(user)
        self.show_toast(f"Welcome back, {self.current_user['username']}!")
        if as_admin:
            self.show_screen("admin_dashboard")
        else:
            self.show_screen("dashboard")

    def logout_user(self):
        """Clears the session user and redirects to the login screen."""
        if self.current_user:
            self.show_toast(f"Logged out of session: {self.current_user['username']}")
        self.current_user = None
        self.show_screen("login")

    def refresh_user_data(self):
        """Reloads user data from DB to update balance and profiles in state."""
        if self.current_user:
            updated = db.get_user_by_id(self.current_user['id'])
            if updated:
                self.current_user = dict(updated)

    def show_toast(self, message, is_error=False):
        """Triggers a sliding visual feedback toast notification."""
        ToastNotification(self, message, is_error)


class LoginScreen(tk.Frame):
    """Login panel using modern aligned inputs and background branding."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        
        # Center card frame
        card = tk.Frame(self, bg=BG_SURFACE, padx=40, pady=40, highlightbackground=BORDER_COLOR, highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo / Branding
        logo_label = tk.Label(card, text="📚 BookBridge", fg=ACCENT_PURPLE, bg=BG_SURFACE, font=(FONT_TITLE[0], 24, "bold"))
        logo_label.pack(pady=(0, 5))
        
        subtitle = tk.Label(card, text="A Cozy Haven for Book Lovers", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION)
        subtitle.pack(pady=(0, 25))
        
        # Form fields
        self.username_input = ModernInput(card, label_text="Username", placeholder="Enter your username")
        self.username_input.pack(fill="x", pady=10)
        
        self.password_input = ModernInput(card, label_text="Password", placeholder="••••••••", show="*")
        self.password_input.pack(fill="x", pady=10)
        
        # Actions Frame
        actions_frame = tk.Frame(card, bg=BG_SURFACE)
        actions_frame.pack(fill="x", pady=(20, 10))
        
        btn_user_login = ModernButton(
            actions_frame, 
            text="Log In as User", 
            command=lambda: self.handle_login(as_admin=False),
            bg=ACCENT_BLUE,
            hover_bg="#2563EB",
            padding=(10, 8)
        )
        btn_user_login.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        btn_admin_login = ModernButton(
            actions_frame, 
            text="Log In as Admin", 
            command=lambda: self.handle_login(as_admin=True),
            bg=ACCENT_PURPLE,
            hover_bg=ACCENT_PURPLE_HOVER,
            padding=(10, 8)
        )
        btn_admin_login.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        register_link = tk.Label(card, text="New reader? Sign Up here", fg=ACCENT_BLUE, bg=BG_SURFACE, font=FONT_CAPTION, cursor="hand2")
        register_link.pack(pady=(5, 0))
        register_link.bind("<Button-1>", lambda e: controller.show_screen("register"))

    def handle_login(self, as_admin=False):
        username = self.username_input.get().strip()
        password = self.password_input.get().strip()
        
        if not username or not password:
            self.controller.show_toast("Please fill in all fields.", is_error=True)
            return
            
        user = db.verify_user(username, password)
        if user:
            if as_admin and user.get('is_admin') != 1:
                self.controller.show_toast("Access Denied: Account is not an administrator.", is_error=True)
            else:
                self.controller.login_user(user, as_admin=as_admin)
        else:
            self.controller.show_toast("Invalid username or password.", is_error=True)


class RegisterScreen(tk.Frame):
    """Registration screen with support for default address settings."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        
        # Center card frame
        card = tk.Frame(self, bg=BG_SURFACE, padx=40, pady=30, highlightbackground=BORDER_COLOR, highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo / Branding
        logo_label = tk.Label(card, text="Join BookBridge", fg=ACCENT_PURPLE, bg=BG_SURFACE, font=FONT_TITLE)
        logo_label.pack(pady=(0, 5))
        
        subtitle = tk.Label(card, text="Buy, sell, swap, and track your library worldwide.", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION)
        subtitle.pack(pady=(0, 20))
        
        # Form fields
        self.username_input = ModernInput(card, label_text="Username", placeholder="e.g. bookworm99")
        self.username_input.pack(fill="x", pady=5)
        
        self.email_input = ModernInput(card, label_text="Email Address", placeholder="e.g. reader@domain.com")
        self.email_input.pack(fill="x", pady=5)
        
        self.password_input = ModernInput(card, label_text="Password", placeholder="••••••••", show="*")
        self.password_input.pack(fill="x", pady=5)
        
        self.address_input = ModernInput(card, label_text="Delivery Address", placeholder="e.g. 123 Library Lane, NY")
        self.address_input.pack(fill="x", pady=5)
        
        # Actions
        btn_register = ModernButton(card, text="Create Account", command=self.handle_register, width=20)
        btn_register.pack(fill="x", pady=(15, 10))
        
        login_link = tk.Label(card, text="Already a member? Log In", fg=ACCENT_BLUE, bg=BG_SURFACE, font=FONT_CAPTION, cursor="hand2")
        login_link.pack(pady=(5, 0))
        login_link.bind("<Button-1>", lambda e: controller.show_screen("login"))

    def handle_register(self):
        username = self.username_input.get().strip()
        email = self.email_input.get().strip()
        password = self.password_input.get().strip()
        address = self.address_input.get().strip()
        
        if not username or not email or not password or not address:
            self.controller.show_toast("All fields are required.", is_error=True)
            return
            
        if "@" not in email or "." not in email:
            self.controller.show_toast("Please enter a valid email address.", is_error=True)
            return
            
        success_id = db.add_user(username, password, email, address)
        if success_id:
            # Login immediately
            user = db.verify_user(username, password)
            if user:
                self.controller.login_user(user)
        else:
            self.controller.show_toast("Username already exists.", is_error=True)


class DashboardScreen(tk.Frame):
    """Main dashboard housing sidebar navigation and content swapping frame."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        
        # Sidebar Frame
        self.sidebar = tk.Frame(self, bg=BG_SURFACE, width=220, highlightbackground=BORDER_COLOR, highlightthickness=1)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Main Content Frame
        self.content_area = tk.Frame(self, bg=BG_DARK)
        self.content_area.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        # Set up Sidebar contents
        self.setup_sidebar()
        
        # Active views tracker
        self.active_button = None
        self.current_content = None
        
        # Initial Content View
        self.switch_view("store")

    def setup_sidebar(self):
        # Header Info
        header_lbl = tk.Label(
            self.sidebar, 
            text="📚 BookBridge", 
            fg=ACCENT_PURPLE, 
            bg=BG_SURFACE, 
            font=(FONT_FAMILY, 18, "bold")
        )
        header_lbl.pack(pady=(25, 5))
        
        user_lbl = tk.Label(
            self.sidebar, 
            text=f"Hello, {self.controller.current_user['username']}!", 
            fg=TEXT_PRIMARY, 
            bg=BG_SURFACE, 
            font=FONT_BODY_BOLD
        )
        user_lbl.pack(pady=(0, 20))
        
        # Navigation Buttons
        self.nav_buttons = {}
        nav_items = [
            ("store", "🔍 Browse Catalog"),
            ("sell", "➕ Sell / Exchange"),
            ("orders", "📦 My Orders"),
            ("listings", "🏷️ My Listings"),
            ("wishlist", "💖 Wishlist"),
            ("exchanges", "🔄 Exchanges"),
            ("profile", "📊 Profile & Stats"),
        ]
        
        for view_id, label in nav_items:
            btn = SidebarButton(self.sidebar, label, command=lambda v=view_id: self.switch_view(v))
            btn.pack(fill="x", padx=15, pady=4)
            self.nav_buttons[view_id] = btn
            
        # Spacer
        spacer = tk.Label(self.sidebar, bg=BG_SURFACE)
        spacer.pack(fill="both", expand=True)
        
        # Logout
        btn_logout = SidebarButton(
            self.sidebar, 
            "🚪 Sign Out", 
            command=self.controller.logout_user, 
            active_color=ERROR_COLOR
        )
        btn_logout.pack(fill="x", padx=15, pady=(0, 25))

    def switch_view(self, view_name):
        """Swaps the content pane to the specified subview."""
        # Highlight active button
        if self.active_button:
            self.active_button.set_active(False)
        if view_name in self.nav_buttons:
            self.active_button = self.nav_buttons[view_name]
            self.active_button.set_active(True)
            
        # Clean current contents
        if self.current_content:
            self.current_content.destroy()
            
        # Fetch updated user state for calculations
        self.controller.refresh_user_data()
        
        # Mount new view
        if view_name == "store":
            self.current_content = StoreView(self.content_area, self.controller)
        elif view_name == "sell":
            self.current_content = SellView(self.content_area, self.controller, self)
        elif view_name == "orders":
            self.current_content = OrdersView(self.content_area, self.controller)
        elif view_name == "listings":
            self.current_content = ListingsView(self.content_area, self.controller)
        elif view_name == "wishlist":
            self.current_content = WishlistView(self.content_area, self.controller)
        elif view_name == "exchanges":
            self.current_content = ExchangesView(self.content_area, self.controller)
        elif view_name == "profile":
            self.current_content = ProfileView(self.content_area, self.controller)
            
        self.current_content.pack(fill="both", expand=True)


class SidebarButton(tk.Frame):
    """Custom hoverable button style for navigation bar."""
    def __init__(self, parent, text, command, active_color=ACCENT_PURPLE):
        super().__init__(parent, bg=BG_SURFACE)
        self.command = command
        self.active_color = active_color
        self.is_active = False
        
        self.label = tk.Label(
            self, 
            text=text, 
            bg=BG_SURFACE, 
            fg=TEXT_SECONDARY, 
            font=FONT_BODY, 
            anchor="w", 
            padx=15, 
            pady=10,
            cursor="hand2"
        )
        self.label.pack(fill="x")
        
        self.label.bind("<Enter>", self._on_enter)
        self.label.bind("<Leave>", self._on_leave)
        self.label.bind("<Button-1>", self._on_click)

    def set_active(self, state):
        self.is_active = state
        self.label.configure(
            fg=TEXT_PRIMARY if state else TEXT_SECONDARY,
            bg=BG_SURFACE_LIGHT if state else BG_SURFACE,
            font=FONT_BODY_BOLD if state else FONT_BODY
        )
        self.configure(bg=self.active_color if state else BG_SURFACE)

    def _on_enter(self, event):
        if not self.is_active:
            self.label.configure(fg=TEXT_PRIMARY, bg=BG_SURFACE_LIGHT)

    def _on_leave(self, event):
        if not self.is_active:
            self.label.configure(fg=TEXT_SECONDARY, bg=BG_SURFACE)

    def _on_click(self, event):
        self.command()


# ==========================================
# 1. CATALOG / STORE VIEW
# ==========================================
class StoreView(tk.Frame):
    """Browse catalog view with robust searches, language badges, and detail modals."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        
        # Header Area
        header = tk.Frame(self, bg=BG_DARK)
        header.pack(fill="x", pady=(0, 15))
        
        title_lbl = tk.Label(header, text="Browse Book Marketplace", fg=TEXT_PRIMARY, bg=BG_DARK, font=FONT_TITLE)
        title_lbl.pack(side="left")
        
        # Filters Pane
        filter_bar = tk.Frame(self, bg=BG_SURFACE, padx=15, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        filter_bar.pack(fill="x", pady=(0, 15))
        
        # Search Box
        tk.Label(filter_bar, text="Search", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION).grid(row=0, column=0, sticky="w", padx=5)
        self.search_entry = tk.Entry(filter_bar, bg=BG_SURFACE_LIGHT, fg=TEXT_PRIMARY, relief="flat", font=FONT_BODY, width=22)
        self.search_entry.grid(row=1, column=0, padx=5, pady=2)
        
        # Language dropdown
        tk.Label(filter_bar, text="Language", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION).grid(row=0, column=1, sticky="w", padx=5)
        languages = ["All Languages"] + db.get_unique_languages()
        self.lang_var = tk.StringVar(value="All Languages")
        self.lang_drop = ttk.Combobox(filter_bar, textvariable=self.lang_var, values=languages, state="readonly", width=14)
        self.lang_drop.grid(row=1, column=1, padx=5, pady=2)
        
        # Genre dropdown
        tk.Label(filter_bar, text="Genre", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION).grid(row=0, column=2, sticky="w", padx=5)
        genres = ["All Genres"] + db.get_unique_genres()
        self.genre_var = tk.StringVar(value="All Genres")
        self.genre_drop = ttk.Combobox(filter_bar, textvariable=self.genre_var, values=genres, state="readonly", width=14)
        self.genre_drop.grid(row=1, column=2, padx=5, pady=2)
        
        # Price spinbox
        tk.Label(filter_bar, text="Max Price ($)", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION).grid(row=0, column=3, sticky="w", padx=5)
        self.price_entry = tk.Entry(filter_bar, bg=BG_SURFACE_LIGHT, fg=TEXT_PRIMARY, relief="flat", font=FONT_BODY, width=8)
        self.price_entry.grid(row=1, column=3, padx=5, pady=2)
        
        # Action buttons
        btn_search = ModernButton(filter_bar, text="Apply Filter", command=self.load_books, width=10, bg=ACCENT_PURPLE, hover_bg=ACCENT_PURPLE_HOVER)
        btn_search.grid(row=1, column=4, padx=(15, 5), pady=2)
        
        btn_reset = ModernButton(filter_bar, text="Reset", command=self.reset_filters, width=8, bg=BG_SURFACE_LIGHT, hover_bg=BORDER_COLOR)
        btn_reset.grid(row=1, column=5, padx=5, pady=2)
        
        # Scrollable listings
        self.scroll_frame = ScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True)
        
        # Load initial books
        self.load_books()

    def reset_filters(self):
        self.search_entry.delete(0, tk.END)
        self.lang_var.set("All Languages")
        self.genre_var.set("All Genres")
        self.price_entry.delete(0, tk.END)
        self.load_books()

    def load_books(self):
        # Clear scroll frame
        for child in self.scroll_frame.scrollable_frame.winfo_children():
            child.destroy()
            
        # Get query parameters
        search = self.search_entry.get().strip()
        lang = self.lang_var.get()
        genre = self.genre_var.get()
        price_str = self.price_entry.get().strip()
        
        search_query = search if search else None
        language = lang if lang != "All Languages" else None
        genre_filter = genre if genre != "All Genres" else None
        
        max_price = None
        if price_str:
            try:
                max_price = float(price_str)
            except ValueError:
                self.controller.show_toast("Invalid max price entered.", is_error=True)
                
        # Exclude current user's listings to avoid buying from yourself
        books = db.get_available_books(
            search_query=search_query,
            language=language,
            genre=genre_filter,
            max_price=max_price,
            exclude_user_id=self.controller.current_user['id']
        )
        
        if not books:
            lbl = tk.Label(
                self.scroll_frame.scrollable_frame, 
                text="No books found matches your filters. Adjust settings to browse!",
                fg=TEXT_SECONDARY,
                bg=BG_DARK,
                font=FONT_BODY
            )
            lbl.pack(pady=40)
            return
            
        # Draw books in dynamic grid
        container = self.scroll_frame.scrollable_frame
        
        row_frame = None
        for i, book in enumerate(books):
            if i % 2 == 0:
                row_frame = tk.Frame(container, bg=BG_DARK)
                row_frame.pack(fill="x", pady=8)
                
            card = BookCardFrame(row_frame, book, self.open_book_details, self.controller)
            card.pack(side="left", fill="both", expand=True, padx=8)
            
            # If odd count, pad the right side
            if i == len(books) - 1 and len(books) % 2 != 0:
                spacer = tk.Frame(row_frame, bg=BG_DARK)
                spacer.pack(side="left", fill="both", expand=True, padx=8)

    def open_book_details(self, book_id):
        """Opens the detailed modal window for the selected book."""
        BookDetailsModal(self, self.controller, book_id, self.load_books)


class BookCardFrame(tk.Frame):
    """Individual book listing card containing summary information and action link."""
    def __init__(self, parent, book, view_details_callback, controller):
        super().__init__(parent, bg=BG_SURFACE, highlightbackground=BORDER_COLOR, highlightthickness=1)
        self.book = book
        self.callback = view_details_callback
        
        # Padding margin
        inner = tk.Frame(self, bg=BG_SURFACE, padx=15, pady=15)
        inner.pack(fill="both", expand=True)
        
        # Tags/Badges Row
        badge_row = tk.Frame(inner, bg=BG_SURFACE)
        badge_row.pack(fill="x", pady=(0, 8))
        
        # Genre tag
        genre_lbl = tk.Label(
            badge_row, 
            text=book['genre'].upper(), 
            fg=ACCENT_PURPLE, 
            bg=BG_SURFACE_LIGHT, 
            font=(FONT_FAMILY, 8, "bold"),
            padx=8,
            pady=2
        )
        genre_lbl.pack(side="left")
        
        # Language tag
        lang_lbl = tk.Label(
            badge_row, 
            text=book['language'], 
            fg=TEXT_SECONDARY, 
            bg=BG_SURFACE, 
            font=FONT_CAPTION,
            padx=5
        )
        lang_lbl.pack(side="left", padx=5)
        
        # E-Book tag
        if book['format'] != 'Paper':
            format_lbl = tk.Label(
                badge_row,
                text=book['format'],
                fg=ACCENT_BLUE,
                bg=BG_SURFACE_LIGHT,
                font=(FONT_FAMILY, 8, "bold"),
                padx=8,
                pady=2
            )
            format_lbl.pack(side="left", padx=5)
            
        # Exchange Tag
        if book['listing_type'] == 'Exchange':
            ex_lbl = tk.Label(
                badge_row,
                text="EXCHANGE",
                fg="#10B981",
                bg=BG_SURFACE_LIGHT,
                font=(FONT_FAMILY, 8, "bold"),
                padx=8,
                pady=2
            )
            ex_lbl.pack(side="left", padx=5)
        
        # Secondary Seller indicator
        if book['owner_id'] is not None:
            secondary_lbl = tk.Label(
                badge_row,
                text="Used",
                fg="#F59E0B",
                bg=BG_SURFACE_LIGHT,
                font=(FONT_FAMILY, 8, "bold"),
                padx=8,
                pady=2
            )
            secondary_lbl.pack(side="right")
            
        # Title and Author
        title_lbl = tk.Label(
            inner, 
            text=book['title'], 
            fg=TEXT_PRIMARY, 
            bg=BG_SURFACE, 
            font=FONT_SUBTITLE, 
            anchor="w",
            wraplength=350,
            justify="left"
        )
        title_lbl.pack(fill="x", pady=(0, 2))
        
        author_lbl = tk.Label(
            inner, 
            text=f"by {book['author']}", 
            fg=TEXT_SECONDARY, 
            bg=BG_SURFACE, 
            font=FONT_CAPTION, 
            anchor="w"
        )
        author_lbl.pack(fill="x", pady=(0, 8))
        
        # Description excerpt
        desc = book['description']
        desc_excerpt = desc if len(desc) <= 90 else desc[:87] + "..."
        desc_lbl = tk.Label(
            inner, 
            text=desc_excerpt, 
            fg=TEXT_SECONDARY, 
            bg=BG_SURFACE, 
            font=FONT_BODY,
            justify="left",
            wraplength=350,
            anchor="nw",
            height=3
        )
        desc_lbl.pack(fill="x", pady=(0, 10))
        
        # Bottom Row: Price and Button
        bottom_row = tk.Frame(inner, bg=BG_SURFACE)
        bottom_row.pack(fill="x", side="bottom")
        
        # Show "Exchange" tag or price
        if book['listing_type'] == 'Exchange':
            price_lbl = tk.Label(
                bottom_row,
                text="🔄 Swap Offer",
                fg="#10B981",
                bg=BG_SURFACE,
                font=(FONT_FAMILY, 13, "bold")
            )
        else:
            price_lbl = tk.Label(
                bottom_row, 
                text=f"${book['price']:.2f}", 
                fg=TEXT_PRIMARY, 
                bg=BG_SURFACE, 
                font=(FONT_FAMILY, 14, "bold")
            )
        price_lbl.pack(side="left")
        
        btn_details = ModernButton(
            bottom_row, 
            text="View Details", 
            command=lambda: self.callback(book['id']),
            bg=ACCENT_BLUE,
            hover_bg="#2563EB",
            font=FONT_BODY_BOLD,
            padding=(10, 4)
        )
        btn_details.pack(side="right")


class BookDetailsModal(tk.Toplevel):
    """Detailed popup modal showing full descriptions, reviews, chats, and checkout/exchange proposal prompts."""
    def __init__(self, parent, controller, book_id, refresh_callback):
        super().__init__(parent)
        self.controller = controller
        self.book_id = book_id
        self.refresh_callback = refresh_callback
        
        self.title("Book Details")
        self.geometry("700x620")
        self.configure(bg=BG_DARK)
        self.transient(parent)
        self.grab_set()
        
        # Fetch data
        self.book = db.get_book_by_id(book_id)
        if not self.book:
            self.destroy()
            return
            
        # Root Frame with Scroll
        self.root_frame = ScrollableFrame(self)
        self.root_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.draw_details()

    def draw_details(self):
        container = self.root_frame.scrollable_frame
        
        # Back/Close button
        btn_close = ModernButton(container, text="← Back to Catalog", command=self.destroy, bg=BG_SURFACE_LIGHT, hover_bg=BORDER_COLOR, width=15)
        btn_close.pack(anchor="w", pady=(0, 15))
        
        # Title Card
        title_card = tk.Frame(container, bg=BG_SURFACE, padx=20, pady=20, highlightbackground=BORDER_COLOR, highlightthickness=1)
        title_card.pack(fill="x", pady=(0, 15))
        
        genre_lang = tk.Frame(title_card, bg=BG_SURFACE)
        genre_lang.pack(fill="x", pady=(0, 5))
        
        tk.Label(genre_lang, text=self.book['genre'].upper(), fg=ACCENT_PURPLE, bg=BG_SURFACE_LIGHT, font=(FONT_FAMILY, 9, "bold"), padx=10, pady=2).pack(side="left")
        tk.Label(genre_lang, text=f"Language: {self.book['language']}", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION).pack(side="left", padx=10)
        
        # Format Badge
        tk.Label(genre_lang, text=f"Format: {self.book['format']}", fg=ACCENT_BLUE, bg=BG_SURFACE_LIGHT, font=(FONT_FAMILY, 9, "bold"), padx=8, pady=2).pack(side="left", padx=5)
        
        # Seller
        seller_text = "BookBridge Official" if self.book['owner_id'] is None else f"Seller ID: {self.book['owner_id']}"
        tk.Label(genre_lang, text=f"Source: {seller_text}", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION).pack(side="right")
        
        tk.Label(title_card, text=self.book['title'], fg=TEXT_PRIMARY, bg=BG_SURFACE, font=(FONT_FAMILY, 22, "bold"), anchor="w", justify="left", wraplength=550).pack(fill="x", pady=5)
        tk.Label(title_card, text=f"by {self.book['author']}", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_SUBTITLE, anchor="w").pack(fill="x", pady=(0, 15))
        
        # Rating summary
        rating_summary = db.get_book_rating_summary(self.book_id)
        rating_row = tk.Frame(title_card, bg=BG_SURFACE)
        rating_row.pack(fill="x", pady=(0, 10))
        
        if rating_summary['avg_rating']:
            StarRating(rating_row, rating=rating_summary['avg_rating'], size=14, bg=BG_SURFACE).pack(side="left")
            tk.Label(rating_row, text=f"({rating_summary['avg_rating']:.1f}/5.0 based on {rating_summary['rating_count']} reviews)", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION).pack(side="left", padx=8)
        else:
            tk.Label(rating_row, text="No ratings yet. Be the first to review!", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION_MUTED).pack(side="left")
            
        # Divider line
        tk.Frame(title_card, height=1, bg=BORDER_COLOR).pack(fill="x", pady=10)
        
        # Buy/Wishlist Action Row
        action_row = tk.Frame(title_card, bg=BG_SURFACE)
        action_row.pack(fill="x", pady=5)
        
        if self.book['listing_type'] == 'Exchange':
            price_lbl = tk.Label(
                action_row, 
                text=f"🔄 Exchange for:\n\"{self.book['wanted_book']}\"", 
                fg="#10B981", 
                bg=BG_SURFACE, 
                font=(FONT_FAMILY, 12, "bold"),
                justify="left"
            )
        else:
            price_lbl = tk.Label(action_row, text=f"${self.book['price']:.2f}", fg=TEXT_PRIMARY, bg=BG_SURFACE, font=(FONT_FAMILY, 20, "bold"))
            
        price_lbl.pack(side="left")
        
        # Check if already wishlisted
        is_wish = db.is_in_wishlist(self.controller.current_user['id'], self.book_id)
        wish_text = "❤️ In Wishlist" if is_wish else "🖤 Add to Wishlist"
        wish_bg = BG_SURFACE_LIGHT if is_wish else ACCENT_BLUE
        
        self.btn_wish = ModernButton(action_row, text=wish_text, command=self.handle_wishlist, bg=wish_bg, hover_bg=BORDER_COLOR)
        self.btn_wish.pack(side="right", padx=10)
        
        # Choose checkout button depending on listing type
        if self.book['listing_type'] == 'Exchange':
            btn_buy = ModernButton(action_row, text="🔄 Propose Exchange", command=self.handle_exchange, bg=ACCENT_PURPLE, hover_bg=ACCENT_PURPLE_HOVER)
        else:
            btn_buy = ModernButton(action_row, text="💳 Purchase Now", command=self.handle_purchase, bg=SUCCESS_COLOR, hover_bg="#059669")
        btn_buy.pack(side="right")
            
        # Full Description
        desc_card = tk.Frame(container, bg=BG_SURFACE, padx=20, pady=20, highlightbackground=BORDER_COLOR, highlightthickness=1)
        desc_card.pack(fill="x", pady=(0, 15))
        
        tk.Label(desc_card, text="Description", fg=TEXT_PRIMARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").pack(fill="x", pady=(0, 5))
        tk.Label(desc_card, text=self.book['description'], fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY, anchor="w", justify="left", wraplength=550).pack(fill="x")
        
        # --- REVIEWS SECTION ---
        reviews_card = tk.Frame(container, bg=BG_SURFACE, padx=20, pady=20, highlightbackground=BORDER_COLOR, highlightthickness=1)
        reviews_card.pack(fill="x", pady=(0, 15))
        
        tk.Label(reviews_card, text="Reviews & Discussion", fg=TEXT_PRIMARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").pack(fill="x", pady=(0, 10))
        
        # Leave a Review widget
        review_input_frame = tk.Frame(reviews_card, bg=BG_SURFACE_LIGHT, padx=12, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        review_input_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(review_input_frame, text="Leave a Review:", fg=TEXT_PRIMARY, bg=BG_SURFACE_LIGHT, font=FONT_BODY_BOLD).grid(row=0, column=0, sticky="w", pady=2)
        
        self.rating_entry = StarRating(review_input_frame, rating=5, interactive=True, bg=BG_SURFACE_LIGHT)
        self.rating_entry.grid(row=0, column=1, sticky="w", padx=10, pady=2)
        
        self.review_text = tk.Entry(review_input_frame, bg=BG_SURFACE, fg=TEXT_PRIMARY, relief="flat", font=FONT_BODY, width=45)
        self.review_text.grid(row=1, column=0, columnspan=2, sticky="ew", pady=8)
        
        btn_submit_review = ModernButton(
            review_input_frame, 
            text="Post", 
            command=self.submit_review, 
            bg=ACCENT_PURPLE, 
            hover_bg=ACCENT_PURPLE_HOVER,
            padding=(12, 4)
        )
        btn_submit_review.grid(row=1, column=2, sticky="e", padx=(10, 0))
        
        # List Reviews
        reviews = db.get_book_reviews(self.book_id)
        if not reviews:
            self.no_reviews_lbl = tk.Label(reviews_card, text="No reviews yet for this copy.", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION_MUTED)
            self.no_reviews_lbl.pack(pady=10)
        else:
            self.reviews_list_frame = tk.Frame(reviews_card, bg=BG_SURFACE)
            self.reviews_list_frame.pack(fill="x")
            
            for rev in reviews:
                self.draw_review_item(self.reviews_list_frame, rev)

    def draw_review_item(self, parent, rev):
        item = tk.Frame(parent, bg=BG_SURFACE, pady=8)
        item.pack(fill="x")
        
        header = tk.Frame(item, bg=BG_SURFACE)
        header.pack(fill="x")
        
        tk.Label(header, text=rev['username'], fg=TEXT_PRIMARY, bg=BG_SURFACE, font=FONT_BODY_BOLD).pack(side="left")
        StarRating(header, rating=rev['rating'], size=10, bg=BG_SURFACE).pack(side="left", padx=10)
        tk.Label(header, text=rev['date'], fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION).pack(side="right")
        
        tk.Label(item, text=rev['comment'], fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY, anchor="w", justify="left", wraplength=550).pack(fill="x", pady=(2, 0))
        tk.Frame(parent, height=1, bg=BG_SURFACE_LIGHT).pack(fill="x")

    def handle_wishlist(self):
        added = db.toggle_wishlist(self.controller.current_user['id'], self.book_id)
        if added:
            self.controller.show_toast("Added book to your wishlist!")
            self.btn_wish.configure_text("❤️ In Wishlist")
            self.btn_wish.label.configure(bg=BG_SURFACE_LIGHT)
            self.btn_wish.bg = BG_SURFACE_LIGHT
        else:
            self.controller.show_toast("Removed book from wishlist.")
            self.btn_wish.configure_text("🖤 Add to Wishlist")
            self.btn_wish.label.configure(bg=ACCENT_BLUE)
            self.btn_wish.bg = ACCENT_BLUE

    def handle_purchase(self):
        self.controller.refresh_user_data()
        buyer = self.controller.current_user
        
        # Confirm prompt
        shipping_desc = "instantly via digital delivery" if self.book['format'] != 'Paper' else f"to your address:\n{buyer['address']}"
        confirm = messagebox.askyesno(
            "Confirm Purchase", 
            f"Are you sure you want to buy '{self.book['title']}' for ${self.book['price']:.2f}?\n\nIt will be delivered {shipping_desc}."
        )
        
        if confirm:
            try:
                success = db.buy_book(buyer['id'], self.book_id, buyer['address'])
                if success:
                    # Calculate points earned (equivalent to 1 point per 1000 UZS)
                    pts = int(self.book['price'] * 12.5)
                    self.controller.show_toast(f"Purchase successful! +{pts} bonus points earned!")
                    self.refresh_callback()
                    self.destroy()
            except Exception as e:
                self.controller.show_toast(str(e), is_error=True)

    def handle_exchange(self):
        """Launches exchange selection popup."""
        ProposeExchangeModal(self, self.controller, self.book)

    def submit_review(self):
        comment = self.review_text.get().strip()
        rating = self.rating_entry.get_rating()
        
        if not comment:
            self.controller.show_toast("Please write a comment.", is_error=True)
            return
            
        success = db.add_review(self.book_id, self.controller.current_user['id'], rating, comment)
        if success:
            self.controller.show_toast("Review posted successfully!")
            self.review_text.delete(0, tk.END)
            self.destroy()
            BookDetailsModal(self.master, self.controller, self.book_id, self.refresh_callback)
        else:
            self.controller.show_toast("Error posting review.", is_error=True)


# ==========================================
# 2. SELL / EXCHANGE SECONDARY BOOK VIEW
# ==========================================
class SellView(tk.Frame):
    """Form to list secondary books for sale or exchange with format options."""
    def __init__(self, parent, controller, dashboard):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        self.dashboard = dashboard
        
        title_lbl = tk.Label(self, text="List a Book for Sale or Exchange", fg=TEXT_PRIMARY, bg=BG_DARK, font=FONT_TITLE)
        title_lbl.pack(anchor="w", pady=(0, 20))
        
        # Form Container
        form_card = tk.Frame(self, bg=BG_SURFACE, padx=30, pady=25, highlightbackground=BORDER_COLOR, highlightthickness=1)
        form_card.pack(fill="both", expand=True)
        
        form_card.columnconfigure(0, weight=1)
        form_card.columnconfigure(1, weight=1)
        
        # Row 0: Title & Author
        self.title_input = ModernInput(form_card, label_text="Book Title", placeholder="e.g. 1984")
        self.title_input.grid(row=0, column=0, padx=10, pady=6, sticky="ew")
        
        self.author_input = ModernInput(form_card, label_text="Author", placeholder="e.g. George Orwell")
        self.author_input.grid(row=0, column=1, padx=10, pady=6, sticky="ew")
        
        # Row 1: Language & Genre
        self.lang_input = ModernInput(form_card, label_text="Language", placeholder="e.g. English, Spanish")
        self.lang_input.grid(row=1, column=0, padx=10, pady=6, sticky="ew")
        
        self.genre_input = ModernInput(form_card, label_text="Genre", placeholder="e.g. Sci-Fi, Fiction")
        self.genre_input.grid(row=1, column=1, padx=10, pady=6, sticky="ew")
        
        # Row 2: Format & Listing Type
        fmt_lbl = tk.Label(form_card, text="Format Type", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION, anchor="w")
        fmt_lbl.grid(row=2, column=0, sticky="w", padx=10, pady=(6, 2))
        self.format_var = tk.StringVar(value="Paper")
        self.format_drop = ttk.Combobox(form_card, textvariable=self.format_var, values=["Paper", "PDF", "EPUB"], state="readonly")
        self.format_drop.grid(row=3, column=0, padx=10, pady=(0, 6), sticky="ew")
        
        list_lbl = tk.Label(form_card, text="Offer Type", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION, anchor="w")
        list_lbl.grid(row=2, column=1, sticky="w", padx=10, pady=(6, 2))
        self.list_type_var = tk.StringVar(value="Sell")
        self.list_type_drop = ttk.Combobox(form_card, textvariable=self.list_type_var, values=["Sell", "Exchange"], state="readonly")
        self.list_type_drop.grid(row=3, column=1, padx=10, pady=(0, 6), sticky="ew")
        self.list_type_drop.bind("<<ComboboxSelected>>", self.on_list_type_change)
        
        # Row 4: Pricing / Exchange Swap Details (Dynamic)
        self.price_container = tk.Frame(form_card, bg=BG_SURFACE)
        self.price_container.grid(row=4, column=0, columnspan=2, sticky="ew")
        self.price_container.columnconfigure(0, weight=1)
        self.price_container.columnconfigure(1, weight=1)
        
        self.price_input = ModernInput(self.price_container, label_text="Selling Price ($)", placeholder="e.g. 9.50")
        self.price_input.grid(row=0, column=0, padx=10, pady=6, sticky="ew")
        
        self.wanted_input = ModernInput(self.price_container, label_text="Wanted Book Title (For Exchange)", placeholder="e.g. The Master and Margarita")
        
        # Row 5: Textbox description
        desc_label = tk.Label(form_card, text="Book Condition & Description", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION, anchor="w")
        desc_label.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 2))
        
        desc_border = tk.Frame(form_card, bg=BORDER_COLOR, padx=1, pady=1)
        desc_border.grid(row=6, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 10))
        form_card.rowconfigure(6, weight=1)
        
        self.desc_text = tk.Text(
            desc_border, 
            bg=BG_SURFACE_LIGHT, 
            fg=TEXT_PRIMARY, 
            insertbackground=TEXT_PRIMARY, 
            relief="flat", 
            font=FONT_BODY,
            bd=0
        )
        self.desc_text.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Actions
        btn_submit = ModernButton(
            form_card, 
            text="🚀 List Book on BookBridge", 
            command=self.handle_submit, 
            bg=ACCENT_PURPLE,
            hover_bg=ACCENT_PURPLE_HOVER,
            width=22
        )
        btn_submit.grid(row=7, column=0, columnspan=2, pady=10)

    def on_list_type_change(self, event):
        val = self.list_type_var.get()
        if val == "Exchange":
            self.price_input.grid_remove()
            self.wanted_input.grid(row=0, column=0, columnspan=2, padx=10, pady=6, sticky="ew")
        else:
            self.wanted_input.grid_remove()
            self.price_input.grid(row=0, column=0, padx=10, pady=6, sticky="ew")

    def handle_submit(self):
        title = self.title_input.get().strip()
        author = self.author_input.get().strip()
        lang = self.lang_input.get().strip()
        genre = self.genre_input.get().strip()
        fmt = self.format_var.get()
        list_type = self.list_type_var.get()
        desc = self.desc_text.get("1.0", tk.END).strip()
        
        price = 0.0
        wanted_book = None
        
        if list_type == "Exchange":
            wanted_book = self.wanted_input.get().strip()
            if not title or not author or not lang or not genre or not wanted_book or not desc:
                self.controller.show_toast("Please fill in all form details.", is_error=True)
                return
        else:
            price_str = self.price_input.get().strip()
            if not title or not author or not lang or not genre or not price_str or not desc:
                self.controller.show_toast("Please fill in all form details.", is_error=True)
                return
            try:
                price = float(price_str)
                if price < 0:
                    raise ValueError()
            except ValueError:
                self.controller.show_toast("Price must be a valid positive number.", is_error=True)
                return
                
        # Mock download url for secondary digital files
        durl = f"{title.lower().replace(' ', '_')}.pdf" if fmt != "Paper" else None
            
        db.add_book(
            title=title,
            author=author,
            description=desc,
            price=price,
            language=lang.capitalize(),
            genre=genre.capitalize(),
            owner_id=self.controller.current_user['id'],
            format=fmt,
            download_url=durl,
            listing_type=list_type,
            wanted_book=wanted_book
        )
        
        self.controller.show_toast("Successfully listed your book!")
        self.dashboard.switch_view("listings")


# ==========================================
# 3. MY ORDERS & TRACKING
# ==========================================
class OrdersView(tk.Frame):
    """Displays user purchases and allows simulating shipment logs or downloading E-books."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        
        title_lbl = tk.Label(self, text="My Orders & Deliveries", fg=TEXT_PRIMARY, bg=BG_DARK, font=FONT_TITLE)
        title_lbl.pack(anchor="w", pady=(0, 15))
        
        # Scrollable contents
        self.scroll_frame = ScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True)
        
        self.load_orders()

    def load_orders(self):
        for child in self.scroll_frame.scrollable_frame.winfo_children():
            child.destroy()
            
        purchases = db.get_user_purchases(self.controller.current_user['id'])
        if not purchases:
            lbl = tk.Label(
                self.scroll_frame.scrollable_frame, 
                text="You have not purchased any books yet. Visit the catalog to buy your first book!",
                fg=TEXT_SECONDARY,
                bg=BG_DARK,
                font=FONT_BODY
            )
            lbl.pack(pady=40)
            return
            
        for tx in purchases:
            self.draw_order_card(self.scroll_frame.scrollable_frame, tx)

    def draw_order_card(self, parent, tx):
        card = tk.Frame(parent, bg=BG_SURFACE, highlightbackground=BORDER_COLOR, highlightthickness=1, pady=15, padx=20)
        card.pack(fill="x", pady=8)
        
        # Top line: Title & Price
        top = tk.Frame(card, bg=BG_SURFACE)
        top.pack(fill="x")
        
        # Display title with format indicator
        title_text = tx['title'] if tx['format'] == 'Paper' else f"{tx['title']} [{tx['format']}]"
        tk.Label(top, text=title_text, fg=TEXT_PRIMARY, bg=BG_SURFACE, font=FONT_SUBTITLE).pack(side="left")
        tk.Label(top, text=f"${tx['price']:.2f}", fg=TEXT_PRIMARY, bg=BG_SURFACE, font=FONT_SUBTITLE).pack(side="right")
        
        # Mid metadata
        mid = tk.Frame(card, bg=BG_SURFACE)
        mid.pack(fill="x", pady=(2, 8))
        
        seller = tx['seller_name'] if tx['seller_name'] else "BookBridge Official"
        tk.Label(mid, text=f"by {tx['author']}  |  Seller: {seller}  |  Ordered: {tx['date']}", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION).pack(side="left")
        
        # Status Badge
        status = tx['status']
        status_color = WARNING_COLOR if status == 'Pending' else ACCENT_BLUE if status == 'Shipped' else SUCCESS_COLOR
        badge = tk.Label(
            mid, 
            text=status.upper(), 
            fg=status_color, 
            bg=BG_SURFACE_LIGHT, 
            font=(FONT_FAMILY, 9, "bold"),
            padx=8,
            pady=1
        )
        badge.pack(side="right")
        
        # Address
        tk.Label(card, text=f"📍 Delivery Address: {tx['delivery_address']}", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION, anchor="w").pack(fill="x", pady=(0, 10))
        
        # Tracking Timeline Box
        tracking_box = tk.Frame(card, bg=BG_DARK, padx=12, pady=10)
        tracking_box.pack(fill="x", pady=(0, 10))
        
        tk.Label(tracking_box, text="Transit History Logs:", fg=TEXT_SECONDARY, bg=BG_DARK, font=FONT_BODY_BOLD, anchor="w").pack(fill="x", pady=(0, 4))
        
        # Renders the tracking events list
        for event in tx['tracking_info'].strip().split("\n"):
            if event:
                tk.Label(tracking_box, text=event, fg=TEXT_PRIMARY, bg=BG_DARK, font=FONT_CAPTION, anchor="w", justify="left", wraplength=700).pack(fill="x", pady=2)
                
        # Action Row (Simulate Courier / Digital downloads)
        action_row = tk.Frame(card, bg=BG_SURFACE)
        action_row.pack(fill="x", side="bottom")
        
        if tx['format'] in ('PDF', 'EPUB'):
            # Download E-Book Button
            btn_download = ModernButton(
                action_row,
                text=f"📥 Download E-Book ({tx['format']})",
                command=lambda t=tx['title'], f=tx['format']: self.download_ebook(t, f),
                bg=SUCCESS_COLOR,
                hover_bg="#059669",
                padding=(12, 4)
            )
            btn_download.pack(side="left")
        else:
            # Physical Package dispatch simulation
            if status == 'Pending':
                btn_ship = ModernButton(
                    action_row, 
                    text="🚚 Dispatch Item (Simulate)", 
                    command=lambda tx_id=tx['id']: self.simulate_ship(tx_id),
                    bg=ACCENT_BLUE,
                    hover_bg="#2563EB",
                    padding=(12, 4)
                )
                btn_ship.pack(side="left")
                
            elif status == 'Shipped':
                btn_deliver = ModernButton(
                    action_row, 
                    text="✅ Confirm Delivery Received", 
                    command=lambda tx_id=tx['id']: self.simulate_delivered(tx_id),
                    bg=SUCCESS_COLOR,
                    hover_bg="#059669",
                    padding=(12, 4)
                )
                btn_deliver.pack(side="left")
            else:
                tk.Label(action_row, text="📦 Package Delivered safely. Thank you for shopping!", fg=SUCCESS_COLOR, bg=BG_SURFACE, font=FONT_BODY_BOLD).pack(side="left")

    def simulate_ship(self, tx_id):
        db.update_transaction_status(
            transaction_id=tx_id, 
            status='Shipped', 
            tracking_note='Package handed to courier. In transit to destination distribution hub.'
        )
        self.controller.show_toast("Courier has picked up package!")
        self.load_orders()

    def simulate_delivered(self, tx_id):
        db.update_transaction_status(
            transaction_id=tx_id, 
            status='Delivered', 
            tracking_note='Package successfully signed and delivered to doorstep.'
        )
        self.controller.show_toast("Package delivered successfully!")
        self.load_orders()

    def download_ebook(self, title, fmt):
        """Simulates download dialog and exports mock document."""
        ext = ".pdf" if fmt == "PDF" else ".epub"
        file_path = filedialog.asksaveasfilename(
            title="Download E-Book",
            initialfile=f"{title.lower().replace(' ', '_')}_ebook",
            defaultextension=ext,
            filetypes=[("PDF Documents", "*.pdf")] if fmt == "PDF" else [("EPUB Books", "*.epub")]
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("BookBridge Digital Library\n")
                    f.write("==========================\n\n")
                    f.write(f"Title: {title}\n")
                    f.write(f"Format: {fmt}\n")
                    f.write(f"Downloaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write("This is a simulated secure download copy of your purchased E-Book from the BookBridge Marketplace.\n")
                    f.write("Thank you for choosing digital solutions to improve the lives of readers everywhere.\n")
                self.controller.show_toast("E-Book downloaded successfully!")
            except Exception as e:
                self.controller.show_toast(f"Error saving: {str(e)}", is_error=True)


# ==========================================
# 4. MY LISTINGS (SELLING STATS)
# ==========================================
class ListingsView(tk.Frame):
    """Tracks active sales/exchanges listings created by the user."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        
        title_lbl = tk.Label(self, text="My Listed Secondary Books", fg=TEXT_PRIMARY, bg=BG_DARK, font=FONT_TITLE)
        title_lbl.pack(anchor="w", pady=(0, 15))
        
        self.scroll_frame = ScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True)
        
        self.load_listings()

    def load_listings(self):
        for child in self.scroll_frame.scrollable_frame.winfo_children():
            child.destroy()
            
        listings = db.get_user_listings(self.controller.current_user['id'])
        sales = db.get_user_sales(self.controller.current_user['id'])
        
        container = self.scroll_frame.scrollable_frame
        
        # Active Listings Section
        tk.Label(container, text="Active Listings For Sale / Swap", fg=TEXT_PRIMARY, bg=BG_DARK, font=FONT_SUBTITLE, anchor="w").pack(fill="x", pady=(10, 5))
        active_list = [b for b in listings if b['is_sold'] == 0]
        
        if not active_list:
            tk.Label(container, text="You have no active listings. Click 'Sell / Exchange' to list some books!", fg=TEXT_SECONDARY, bg=BG_DARK, font=FONT_CAPTION_MUTED, anchor="w").pack(fill="x", pady=15)
        else:
            for book in active_list:
                self.draw_listing_card(container, book, is_sold=False)
                
        # Sold Listings Section
        tk.Label(container, text="Transaction History (Sold & Swapped)", fg=TEXT_PRIMARY, bg=BG_DARK, font=FONT_SUBTITLE, anchor="w").pack(fill="x", pady=(20, 5))
        
        if not sales:
            tk.Label(container, text="No books sold yet.", fg=TEXT_SECONDARY, bg=BG_DARK, font=FONT_CAPTION_MUTED, anchor="w").pack(fill="x", pady=15)
        else:
            for sale in sales:
                self.draw_sale_card(container, sale)

    def draw_listing_card(self, parent, book, is_sold):
        card = tk.Frame(parent, bg=BG_SURFACE, highlightbackground=BORDER_COLOR, highlightthickness=1, pady=12, padx=15)
        card.pack(fill="x", pady=5)
        
        title_lbl = tk.Label(card, text=book['title'], fg=TEXT_PRIMARY, bg=BG_SURFACE, font=FONT_BODY_BOLD)
        title_lbl.pack(side="left")
        
        meta = f"by {book['author']} | Language: {book['language']} | Format: {book['format']}"
        if book['listing_type'] == 'Exchange':
            meta += f" | 🔄 Swap for: {book['wanted_book']}"
            
        tk.Label(card, text=meta, fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION).pack(side="left", padx=15)
        
        if book['listing_type'] == 'Exchange':
            tk.Label(card, text="EXCHANGE", fg="#10B981", bg=BG_SURFACE, font=FONT_BODY_BOLD).pack(side="right")
        else:
            tk.Label(card, text=f"${book['price']:.2f}", fg=ACCENT_PURPLE, bg=BG_SURFACE, font=FONT_BODY_BOLD).pack(side="right")

    def draw_sale_card(self, parent, sale):
        card = tk.Frame(parent, bg=BG_SURFACE, highlightbackground=BORDER_COLOR, highlightthickness=1, pady=12, padx=15)
        card.pack(fill="x", pady=5)
        
        info = tk.Frame(card, bg=BG_SURFACE)
        info.pack(side="left")
        
        title_lbl = tk.Label(info, text=sale['title'], fg=TEXT_PRIMARY, bg=BG_SURFACE, font=FONT_BODY_BOLD)
        title_lbl.pack(side="left")
        
        trade_type = "Swapped to" if sale['price'] == 0 else "Sold to"
        tk.Label(info, text=f"{trade_type}: {sale['buyer_name']}  |  Date: {sale['date']}", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION).pack(side="left", padx=15)
        
        right_frame = tk.Frame(card, bg=BG_SURFACE)
        right_frame.pack(side="right")
        
        display_val = "SWAP AGREED" if sale['price'] == 0 else f"+${sale['price']:.2f}"
        tk.Label(right_frame, text=display_val, fg=SUCCESS_COLOR, bg=BG_SURFACE, font=FONT_BODY_BOLD).pack(side="left", padx=10)
        
        status_lbl = tk.Label(
            right_frame, 
            text=sale['status'].upper(), 
            fg=SUCCESS_COLOR if sale['status'] == 'Delivered' else WARNING_COLOR, 
            bg=BG_SURFACE_LIGHT, 
            font=(FONT_FAMILY, 8, "bold"),
            padx=8,
            pady=1
        )
        status_lbl.pack(side="left")


# ==========================================
# 5. WISHLIST VIEW
# ==========================================
class WishlistView(tk.Frame):
    """Lists books flagged in wishlist and redirects details."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        
        title_lbl = tk.Label(self, text="My Wishlist", fg=TEXT_PRIMARY, bg=BG_DARK, font=FONT_TITLE)
        title_lbl.pack(anchor="w", pady=(0, 15))
        
        self.scroll_frame = ScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True)
        
        self.load_wishlist()

    def load_wishlist(self):
        for child in self.scroll_frame.scrollable_frame.winfo_children():
            child.destroy()
            
        wish_books = db.get_user_wishlist(self.controller.current_user['id'])
        if not wish_books:
            lbl = tk.Label(
                self.scroll_frame.scrollable_frame, 
                text="Your wishlist is empty. Browse the store to add books you like!",
                fg=TEXT_SECONDARY,
                bg=BG_DARK,
                font=FONT_BODY
            )
            lbl.pack(pady=40)
            return
            
        container = self.scroll_frame.scrollable_frame
        
        row_frame = None
        for i, book in enumerate(wish_books):
            if i % 2 == 0:
                row_frame = tk.Frame(container, bg=BG_DARK)
                row_frame.pack(fill="x", pady=8)
                
            card = BookCardFrame(row_frame, book, self.open_book_details, self.controller)
            card.pack(side="left", fill="both", expand=True, padx=8)
            
            if i == len(wish_books) - 1 and len(wish_books) % 2 != 0:
                spacer = tk.Frame(row_frame, bg=BG_DARK)
                spacer.pack(side="left", fill="both", expand=True, padx=8)

    def open_book_details(self, book_id):
        BookDetailsModal(self, self.controller, book_id, self.load_wishlist)


# 6. MESSAGES VIEW AND CHAT WINDOW DELETED


# ==========================================
# 7. BOOK EXCHANGES VIEW (NEW)
# ==========================================
class ExchangesView(tk.Frame):
    """Tab space to accept, reject, and review Book Exchange proposals."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        
        title_lbl = tk.Label(self, text="🔄 Book Exchange Hub", fg=TEXT_PRIMARY, bg=BG_DARK, font=FONT_TITLE)
        title_lbl.pack(anchor="w", pady=(0, 10))
        
        # Sub-Navigation headers
        self.tab_frame = tk.Frame(self, bg=BG_DARK)
        self.tab_frame.pack(fill="x", pady=(0, 10))
        
        self.btn_received = ModernButton(self.tab_frame, text="📩 Received Proposals", command=self.show_received, bg=ACCENT_PURPLE, padding=(12, 5))
        self.btn_received.pack(side="left", padx=5)
        
        self.btn_sent = ModernButton(self.tab_frame, text="📤 Sent Proposals", command=self.show_sent, bg=BG_SURFACE_LIGHT, padding=(12, 5))
        self.btn_sent.pack(side="left", padx=5)
        
        # Scrollable contents
        self.scroll_frame = ScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True)
        
        self.current_tab = "received"
        self.show_received()

    def show_received(self):
        self.current_tab = "received"
        self.btn_received.label.configure(bg=ACCENT_PURPLE)
        self.btn_received.bg = ACCENT_PURPLE
        self.btn_sent.label.configure(bg=BG_SURFACE_LIGHT)
        self.btn_sent.bg = BG_SURFACE_LIGHT
        self.load_exchanges()

    def show_sent(self):
        self.current_tab = "sent"
        self.btn_sent.label.configure(bg=ACCENT_PURPLE)
        self.btn_sent.bg = ACCENT_PURPLE
        self.btn_received.label.configure(bg=BG_SURFACE_LIGHT)
        self.btn_received.bg = BG_SURFACE_LIGHT
        self.load_exchanges()

    def load_exchanges(self):
        for child in self.scroll_frame.scrollable_frame.winfo_children():
            child.destroy()
            
        container = self.scroll_frame.scrollable_frame
        user_id = self.controller.current_user['id']
        
        if self.current_tab == "received":
            proposals = db.get_received_exchange_proposals(user_id)
            if not proposals:
                tk.Label(container, text="No incoming exchange proposals yet.", fg=TEXT_SECONDARY, bg=BG_DARK, font=FONT_CAPTION_MUTED).pack(pady=40)
                return
            for prop in proposals:
                self.draw_received_card(container, prop)
        else:
            proposals = db.get_sent_exchange_proposals(user_id)
            if not proposals:
                tk.Label(container, text="You have not proposed any exchanges yet.", fg=TEXT_SECONDARY, bg=BG_DARK, font=FONT_CAPTION_MUTED).pack(pady=40)
                return
            for prop in proposals:
                self.draw_sent_card(container, prop)

    def draw_received_card(self, parent, prop):
        card = tk.Frame(parent, bg=BG_SURFACE, highlightbackground=BORDER_COLOR, highlightthickness=1, pady=15, padx=20)
        card.pack(fill="x", pady=6)
        
        # Details layout
        content = tk.Frame(card, bg=BG_SURFACE)
        content.pack(fill="x")
        
        lbl_info = tk.Label(
            content,
            text=f"👤 {prop['proposer_name']} wants to trade:\n"
                 f"👉 Their: \"{prop['proposer_book_title']}\" by {prop['proposer_book_author']}\n"
                 f"👈 In exchange for your: \"{prop['receiver_book_title']}\"",
            fg=TEXT_PRIMARY,
            bg=BG_SURFACE,
            font=FONT_BODY,
            justify="left",
            anchor="w"
        )
        lbl_info.pack(side="left")
        
        # Action buttons
        actions = tk.Frame(card, bg=BG_SURFACE)
        actions.pack(fill="x", pady=(10, 0))
        
        btn_accept = ModernButton(
            actions, 
            text="✅ Accept Swap", 
            command=lambda ex_id=prop['id']: self.respond(ex_id, "Accepted"), 
            bg=SUCCESS_COLOR, 
            hover_bg="#059669",
            padding=(10, 4)
        )
        btn_accept.pack(side="left")
        
        btn_reject = ModernButton(
            actions, 
            text="❌ Reject", 
            command=lambda ex_id=prop['id']: self.respond(ex_id, "Rejected"), 
            bg=ERROR_COLOR, 
            hover_bg="#DC2626",
            padding=(10, 4)
        )
        btn_reject.pack(side="left", padx=10)

    def draw_sent_card(self, parent, prop):
        card = tk.Frame(parent, bg=BG_SURFACE, highlightbackground=BORDER_COLOR, highlightthickness=1, pady=15, padx=20)
        card.pack(fill="x", pady=6)
        
        content = tk.Frame(card, bg=BG_SURFACE)
        content.pack(fill="x")
        
        lbl_info = tk.Label(
            content,
            text=f"Proposed trade to 👤 {prop['receiver_name']}:\n"
                 f"👉 You offer: \"{prop['proposer_book_title']}\"\n"
                 f"👈 For their: \"{prop['receiver_book_title']}\" by {prop['receiver_book_author']}",
            fg=TEXT_PRIMARY,
            bg=BG_SURFACE,
            font=FONT_BODY,
            justify="left",
            anchor="w"
        )
        lbl_info.pack(side="left")
        
        # Status
        status = prop['status']
        status_color = WARNING_COLOR if status == 'Pending' else SUCCESS_COLOR if status == 'Accepted' else ERROR_COLOR
        lbl_status = tk.Label(
            card,
            text=status.upper(),
            fg=status_color,
            bg=BG_SURFACE_LIGHT,
            font=(FONT_FAMILY, 9, "bold"),
            padx=10,
            pady=2
        )
        lbl_status.pack(side="right")

    def respond(self, ex_id, response):
        try:
            db.respond_to_exchange(ex_id, response)
            self.controller.show_toast(f"Exchange offer {response.lower()}!")
            self.load_exchanges()
        except Exception as e:
            self.controller.show_toast(str(e), is_error=True)


class ProposeExchangeModal(tk.Toplevel):
    """Modal dialog displaying active user listings to pick from when proposing a swap."""
    def __init__(self, parent, controller, target_book):
        super().__init__(parent)
        self.controller = controller
        self.target_book = target_book
        
        self.title("Propose Book Swap")
        self.geometry("500x400")
        self.configure(bg=BG_DARK)
        self.transient(parent)
        self.grab_set()
        
        tk.Label(
            self, 
            text=f"Choose a book to offer in exchange for:\n\"{target_book['title']}\"", 
            fg=TEXT_PRIMARY, 
            bg=BG_DARK, 
            font=FONT_SUBTITLE,
            justify="center"
        ).pack(pady=15)
        
        self.scroll = ScrollableFrame(self)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.load_user_offerings()

    def load_user_offerings(self):
        for child in self.scroll.scrollable_frame.winfo_children():
            child.destroy()
            
        listings = db.get_user_listings(self.controller.current_user['id'])
        # User can only offer books that are currently active and not sold
        offerings = [b for b in listings if b['is_sold'] == 0]
        
        container = self.scroll.scrollable_frame
        if not offerings:
            tk.Label(container, text="You don't have any active book listings.\nList a book in the 'Sell / Exchange' tab first!", fg=TEXT_SECONDARY, bg=BG_DARK, font=FONT_BODY, justify="center").pack(pady=40)
            return
            
        for book in offerings:
            self.draw_offering_item(container, book)

    def draw_offering_item(self, parent, book):
        item = tk.Frame(parent, bg=BG_SURFACE, highlightbackground=BORDER_COLOR, highlightthickness=1)
        item.pack(fill="x", pady=4, padx=5)
        
        btn = tk.Label(
            item, 
            text=f"📚 {book['title']} ({book['format']}) - by {book['author']}", 
            fg=TEXT_PRIMARY, 
            bg=BG_SURFACE, 
            font=FONT_BODY,
            anchor="w",
            padx=15,
            pady=10,
            cursor="hand2"
        )
        btn.pack(fill="both", expand=True)
        btn.bind("<Button-1>", lambda event, b=book: self.confirm_proposal(b))

    def confirm_proposal(self, user_book):
        confirm = messagebox.askyesno(
            "Confirm Swap Offer",
            f"Propose swapping your book \"{user_book['title']}\" for their \"{self.target_book['title']}\"?"
        )
        if confirm:
            try:
                db.propose_exchange(
                    proposer_id=self.controller.current_user['id'],
                    receiver_id=self.target_book['owner_id'],
                    proposer_book_id=user_book['id'],
                    receiver_book_id=self.target_book['id']
                )
                self.controller.show_toast("Exchange proposal sent successfully!")
                self.destroy()
            except Exception as e:
                self.controller.show_toast(str(e), is_error=True)


# ==========================================
# 8. PROFILE & ANALYTICS VIEW
# ==========================================
class ProfileView(tk.Frame):
    """Displays user profile parameters, Matplotlib charts, and the Point Shop."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        
        self.scroll_frame = ScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True)
        
        self.draw_profile()

    def draw_profile(self):
        container = self.scroll_frame.scrollable_frame
        user = self.controller.current_user
        
        # Title
        tk.Label(container, text="User Profile & Analytics", fg=TEXT_PRIMARY, bg=BG_DARK, font=FONT_TITLE, anchor="w").pack(fill="x", pady=(0, 15))
        
        # Profile & Wallet (Horizontal Split)
        meta_row = tk.Frame(container, bg=BG_DARK)
        meta_row.pack(fill="x", pady=(0, 15))
        
        # Account details
        details_card = tk.Frame(meta_row, bg=BG_SURFACE, padx=20, pady=20, highlightbackground=BORDER_COLOR, highlightthickness=1)
        details_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        tk.Label(details_card, text="Account Details", fg=TEXT_PRIMARY, bg=BG_SURFACE, font=FONT_SUBTITLE, anchor="w").pack(fill="x", pady=(0, 10))
        
        info_lines = [
            ("Username:", user['username']),
            ("Email Address:", user['email']),
            ("Delivery Destination:", user['address'])
        ]
        for lbl_txt, val_txt in info_lines:
            row = tk.Frame(details_card, bg=BG_SURFACE)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=lbl_txt, fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, width=18, anchor="w").pack(side="left")
            tk.Label(row, text=val_txt, fg=TEXT_PRIMARY, bg=BG_SURFACE, font=FONT_BODY, anchor="w").pack(side="left")
            
        # Wallet and point redemption
        wallet_card = tk.Frame(meta_row, bg=BG_SURFACE, padx=20, pady=20, highlightbackground=BORDER_COLOR, highlightthickness=1)
        wallet_card.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        tk.Label(wallet_card, text="Wallet & Point Shop", fg=TEXT_PRIMARY, bg=BG_SURFACE, font=FONT_SUBTITLE, anchor="w").pack(fill="x", pady=(0, 10))
        
        balance_row = tk.Frame(wallet_card, bg=BG_SURFACE)
        balance_row.pack(fill="x", pady=2)
        tk.Label(balance_row, text="Simulated Balance:", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY).pack(side="left")
        self.bal_lbl = tk.Label(balance_row, text=f"${user['balance']:.2f}", fg=SUCCESS_COLOR, bg=BG_SURFACE, font=(FONT_FAMILY, 15, "bold"))
        self.bal_lbl.pack(side="left", padx=10)
        
        # Points counter
        points_row = tk.Frame(wallet_card, bg=BG_SURFACE)
        points_row.pack(fill="x", pady=2)
        tk.Label(points_row, text="Bonus Points:", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY).pack(side="left")
        
        uzs_val = user['points'] * 1000
        pts_text = f"{user['points']} pts (approx. {uzs_val:,} UZS value)"
        self.pts_lbl = tk.Label(points_row, text=pts_text, fg="#F59E0B", bg=BG_SURFACE, font=(FONT_FAMILY, 11, "bold"))
        self.pts_lbl.pack(side="left", padx=10)
        
        # Points Shop
        shop_row = tk.Frame(wallet_card, bg=BG_SURFACE)
        shop_row.pack(fill="x", pady=(10, 0))
        
        tk.Label(shop_row, text="Redeem Points:", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION).pack(anchor="w", pady=(0, 2))
        
        self.redeem_var = tk.StringVar(value="Select points")
        self.redeem_drop = ttk.Combobox(shop_row, textvariable=self.redeem_var, values=["100 pts ($1.00)", "200 pts ($2.00)", "500 pts ($5.00)", "1000 pts ($10.00)"], state="readonly", width=16)
        self.redeem_drop.pack(side="left", padx=(0, 10))
        
        btn_redeem = ModernButton(shop_row, text="🎁 Redeem", command=self.handle_redemption, bg=ACCENT_PURPLE, hover_bg=ACCENT_PURPLE_HOVER, padding=(10, 3))
        btn_redeem.pack(side="left")
        
        # Add Funds top up
        topup_row = tk.Frame(wallet_card, bg=BG_SURFACE)
        topup_row.pack(fill="x", pady=(15, 0))
        self.topup_entry = ModernInput(topup_row, label_text="Top Up Balance ($)", placeholder="e.g. 50.00", width=12)
        self.topup_entry.pack(side="left", padx=(0, 10))
        
        btn_topup = ModernButton(topup_row, text="💰 Deposit", command=self.handle_topup, bg=BG_SURFACE_LIGHT, hover_bg=BORDER_COLOR, padding=(12, 5))
        btn_topup.pack(side="left", pady=(15, 0))
        
        # Aggregated summary stats banners
        stats = analytics.get_profile_summary_stats(user['id'])
        
        stats_row = tk.Frame(container, bg=BG_DARK)
        stats_row.pack(fill="x", pady=(0, 20))
        
        stat_boxes = [
            ("Books Purchased", f"{stats['books_bought']} copies", ACCENT_BLUE),
            ("Books Sold/Swapped", f"{stats['books_sold']} copies", SUCCESS_COLOR),
            ("Total Spending", f"${stats['total_spent']:.2f}", ERROR_COLOR),
            ("Total Earnings", f"${stats['total_earned']:.2f}", WARNING_COLOR)
        ]
        
        for title, val, color in stat_boxes:
            box = tk.Frame(stats_row, bg=BG_SURFACE, padx=15, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
            box.pack(side="left", fill="both", expand=True, padx=5)
            
            tk.Label(box, text=title, fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION).pack(anchor="w")
            tk.Label(box, text=val, fg=color, bg=BG_SURFACE, font=(FONT_FAMILY, 14, "bold")).pack(anchor="w", pady=(3, 0))

        # --- CHARTS AREA (Pandas + Matplotlib) ---
        charts_header = tk.Label(container, text="Reading Habits & Marketplace Analytics", fg=TEXT_PRIMARY, bg=BG_DARK, font=FONT_SUBTITLE, anchor="w")
        charts_header.pack(fill="x", pady=(10, 10))
        
        charts_row = tk.Frame(container, bg=BG_DARK)
        charts_row.pack(fill="x", pady=5)
        
        # 1. Favorite Genres Pie Chart
        genre_frame = tk.Frame(charts_row, bg=BG_SURFACE, highlightbackground=BORDER_COLOR, highlightthickness=1)
        genre_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        fig_genre = analytics.generate_genre_chart(user['id'])
        canvas_genre = FigureCanvasTkAgg(fig_genre, master=genre_frame)
        canvas_genre.draw()
        canvas_genre.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # 2. Spending Trends Bar Chart
        spending_frame = tk.Frame(charts_row, bg=BG_SURFACE, highlightbackground=BORDER_COLOR, highlightthickness=1)
        spending_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        fig_spend = analytics.generate_spending_chart(user['id'])
        canvas_spend = FigureCanvasTkAgg(fig_spend, master=spending_frame)
        canvas_spend.draw()
        canvas_spend.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def handle_topup(self):
        amount_str = self.topup_entry.get().strip()
        if not amount_str:
            return
            
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            self.controller.show_toast("Please enter a valid positive dollar amount.", is_error=True)
            return
            
        user = self.controller.current_user
        new_balance = user['balance'] + amount
        
        db.update_user_profile(
            user_id=user['id'],
            email=user['email'],
            address=user['address'],
            balance=new_balance
        )
        
        self.controller.show_toast(f"Deposited ${amount:.2f} successfully!")
        self.topup_entry.clear()
        self.draw_profile()

    def handle_redemption(self):
        val = self.redeem_var.get()
        if val == "Select points":
            return
            
        points = int(val.split()[0])
        try:
            bonus = db.redeem_points(self.controller.current_user['id'], points)
            self.controller.show_toast(f"Redeemed points! +${bonus:.2f} store credit added!")
            self.redeem_var.set("Select points")
            self.draw_profile()
        except Exception as e:
            self.controller.show_toast(str(e), is_error=True)


class AdminDashboardScreen(tk.Frame):
    """Admin dashboard housing sidebar navigation and content swapping frame."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        
        # Sidebar Frame
        self.sidebar = tk.Frame(self, bg=BG_SURFACE, width=220, highlightbackground=BORDER_COLOR, highlightthickness=1)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Main Content Frame
        self.content_area = tk.Frame(self, bg=BG_DARK)
        self.content_area.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        # Set up Sidebar contents
        self.setup_sidebar()
        
        # Active views tracker
        self.active_button = None
        self.current_content = None
        
        # Initial Content View
        self.switch_view("admin_inventory")

    def setup_sidebar(self):
        # Header Info
        header_lbl = tk.Label(
            self.sidebar, 
            text="📚 BookBridge Admin", 
            fg=ACCENT_PURPLE, 
            bg=BG_SURFACE, 
            font=(FONT_FAMILY, 16, "bold")
        )
        header_lbl.pack(pady=(25, 5))
        
        user_lbl = tk.Label(
            self.sidebar, 
            text="Administrator Mode", 
            fg=TEXT_SECONDARY, 
            bg=BG_SURFACE, 
            font=FONT_CAPTION
        )
        user_lbl.pack(pady=(0, 20))
        
        # Navigation Buttons
        self.nav_buttons = {}
        nav_items = [
            ("admin_inventory", "📦 Manage Catalog"),
            ("admin_users", "👤 Manage Users"),
            ("admin_reviews", "💬 Manage Reviews"),
            ("admin_transactions", "💸 System Transactions"),
            ("admin_stats", "📊 System Overview"),
        ]
        
        for view_id, label in nav_items:
            btn = SidebarButton(self.sidebar, label, command=lambda v=view_id: self.switch_view(v))
            btn.pack(fill="x", padx=15, pady=4)
            self.nav_buttons[view_id] = btn
            
        # Spacer
        spacer = tk.Label(self.sidebar, bg=BG_SURFACE)
        spacer.pack(fill="both", expand=True)
        
        # Logout
        btn_logout = SidebarButton(
            self.sidebar, 
            "🚪 Sign Out", 
            command=self.controller.logout_user, 
            active_color=ERROR_COLOR
        )
        btn_logout.pack(fill="x", padx=15, pady=(0, 25))

    def switch_view(self, view_name):
        """Swaps the content pane to the specified subview."""
        # Highlight active button
        if self.active_button:
            self.active_button.set_active(False)
        if view_name in self.nav_buttons:
            self.active_button = self.nav_buttons[view_name]
            self.active_button.set_active(True)
            
        # Clean current contents
        if self.current_content:
            self.current_content.destroy()
            
        # Mount new view
        if view_name == "admin_inventory":
            self.current_content = AdminInventoryView(self.content_area, self.controller)
        elif view_name == "admin_users":
            self.current_content = AdminUsersView(self.content_area, self.controller)
        elif view_name == "admin_reviews":
            self.current_content = AdminReviewsView(self.content_area, self.controller)
        elif view_name == "admin_transactions":
            self.current_content = AdminTransactionsView(self.content_area, self.controller)
        elif view_name == "admin_stats":
            self.current_content = AdminStatsView(self.content_area, self.controller)
            
        self.current_content.pack(fill="both", expand=True)


class AdminInventoryView(tk.Frame):
    """Admin inventory view that displays all books, edit/delete actions, and an Add Book button."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        
        # Header Area
        header = tk.Frame(self, bg=BG_DARK)
        header.pack(fill="x", pady=(0, 15))
        
        title_lbl = tk.Label(header, text="Catalog Inventory Management", fg=TEXT_PRIMARY, bg=BG_DARK, font=FONT_TITLE)
        title_lbl.pack(side="left")
        
        btn_add = ModernButton(
            header,
            text="➕ Add Official Book",
            command=self.add_book,
            bg=SUCCESS_COLOR,
            hover_bg="#059669",
            padding=(12, 5)
        )
        btn_add.pack(side="right")
        
        # Table Header
        table_hdr = tk.Frame(self, bg=BG_SURFACE, highlightbackground=BORDER_COLOR, highlightthickness=1, padx=15, pady=8)
        table_hdr.pack(fill="x", pady=(0, 5))
        table_hdr.columnconfigure(0, weight=3) # Title & Author
        table_hdr.columnconfigure(1, weight=1) # Format
        table_hdr.columnconfigure(2, weight=1) # Price / Details
        table_hdr.columnconfigure(3, weight=1) # Seller
        table_hdr.columnconfigure(4, weight=1) # Status
        table_hdr.columnconfigure(5, weight=2) # Actions
        
        tk.Label(table_hdr, text="Title & Author", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=0, sticky="ew")
        tk.Label(table_hdr, text="Format", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=1, sticky="ew")
        tk.Label(table_hdr, text="Price/Offer", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=2, sticky="ew")
        tk.Label(table_hdr, text="Seller", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=3, sticky="ew")
        tk.Label(table_hdr, text="Status", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=4, sticky="ew")
        tk.Label(table_hdr, text="Actions", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=5, sticky="ew")
        
        # Scrollable listings
        self.scroll_frame = ScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True)
        
        self.load_inventory()

    def load_inventory(self):
        for child in self.scroll_frame.scrollable_frame.winfo_children():
            child.destroy()
            
        books = db.admin_get_all_books()
        container = self.scroll_frame.scrollable_frame
        
        if not books:
            tk.Label(container, text="The catalog is empty.", fg=TEXT_SECONDARY, bg=BG_DARK, font=FONT_BODY).pack(pady=40)
            return
            
        for i, book in enumerate(books):
            row_frame = tk.Frame(container, bg=BG_SURFACE_LIGHT if i % 2 == 0 else BG_SURFACE, padx=15, pady=8)
            row_frame.pack(fill="x", pady=2)
            row_frame.columnconfigure(0, weight=3)
            row_frame.columnconfigure(1, weight=1)
            row_frame.columnconfigure(2, weight=1)
            row_frame.columnconfigure(3, weight=1)
            row_frame.columnconfigure(4, weight=1)
            row_frame.columnconfigure(5, weight=2)
            
            # Title & Author
            title_txt = f"{book['title']}\nby {book['author']}"
            tk.Label(row_frame, text=title_txt, fg=TEXT_PRIMARY, bg=row_frame.cget("bg"), font=FONT_BODY_BOLD, justify="left", anchor="w").grid(row=0, column=0, sticky="w")
            
            # Format
            tk.Label(row_frame, text=book['format'], fg=TEXT_PRIMARY, bg=row_frame.cget("bg"), font=FONT_BODY).grid(row=0, column=1, sticky="w")
            
            # Price / Offer
            if book['listing_type'] == 'Exchange':
                val = f"🔄 Swap:\n\"{book['wanted_book']}\""
            else:
                val = f"${book['price']:.2f}"
            tk.Label(row_frame, text=val, fg=TEXT_PRIMARY, bg=row_frame.cget("bg"), font=FONT_BODY, justify="left", anchor="w").grid(row=0, column=2, sticky="w")
            
            # Seller
            seller = book['owner_name'] if book['owner_name'] else "Official Store"
            tk.Label(row_frame, text=seller, fg=TEXT_PRIMARY, bg=row_frame.cget("bg"), font=FONT_BODY).grid(row=0, column=3, sticky="w")
            
            # Status
            status = "Sold" if book['is_sold'] else "Active"
            color = ERROR_COLOR if book['is_sold'] else SUCCESS_COLOR
            tk.Label(row_frame, text=status, fg=color, bg=row_frame.cget("bg"), font=FONT_BODY_BOLD).grid(row=0, column=4, sticky="w")
            
            # Action Buttons: Edit / Delete
            act_frame = tk.Frame(row_frame, bg=row_frame.cget("bg"))
            act_frame.grid(row=0, column=5, sticky="e")
            
            btn_edit = ModernButton(
                act_frame,
                text="✏️ Edit",
                command=lambda b=book: self.edit_book(b),
                bg=ACCENT_BLUE,
                hover_bg="#2563EB",
                padding=(8, 3)
            )
            btn_edit.pack(side="left", padx=2)
            
            btn_del = ModernButton(
                act_frame,
                text="🗑️ Delete",
                command=lambda b_id=book['id']: self.delete_book(b_id),
                bg=ERROR_COLOR,
                hover_bg="#DC2626",
                padding=(8, 3)
            )
            btn_del.pack(side="left", padx=2)

    def add_book(self):
        AdminAddEditBookModal(self, self.controller, None, self.load_inventory)

    def edit_book(self, book):
        AdminAddEditBookModal(self, self.controller, book, self.load_inventory)

    def delete_book(self, book_id):
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this book from the catalog?")
        if confirm:
            try:
                db.admin_delete_book(book_id)
                self.controller.show_toast("Book deleted successfully!")
                self.load_inventory()
            except Exception as e:
                self.controller.show_toast(str(e), is_error=True)


class AdminAddEditBookModal(tk.Toplevel):
    """Modal to add or edit catalog books by administrator."""
    def __init__(self, parent, controller, book=None, refresh_callback=None):
        super().__init__(parent)
        self.controller = controller
        self.book = book
        self.refresh_callback = refresh_callback
        
        self.title("Add New Book" if not book else f"Edit: {book['title']}")
        self.geometry("600x550")
        self.configure(bg=BG_DARK)
        self.transient(parent)
        self.grab_set()
        
        # Header Label
        lbl_title = tk.Label(
            self,
            text="➕ Create Official Listing" if not book else f"✏️ Edit Book: ID {book['id']}",
            fg=TEXT_PRIMARY,
            bg=BG_DARK,
            font=FONT_SUBTITLE
        )
        lbl_title.pack(pady=10)
        
        # Form Container
        form = tk.Frame(self, bg=BG_SURFACE, padx=20, pady=20, highlightbackground=BORDER_COLOR, highlightthickness=1)
        form.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)
        
        # Row 0: Title & Author
        self.title_input = ModernInput(form, label_text="Book Title", placeholder="Enter title")
        self.title_input.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.author_input = ModernInput(form, label_text="Author", placeholder="Enter author")
        self.author_input.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Row 1: Language & Genre
        self.lang_input = ModernInput(form, label_text="Language", placeholder="e.g. English")
        self.lang_input.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        self.genre_input = ModernInput(form, label_text="Genre", placeholder="e.g. Fiction")
        self.genre_input.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Row 2: Format & Listing Type
        tk.Label(form, text="Format", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION, anchor="w").grid(row=2, column=0, sticky="w", padx=5, pady=(5, 1))
        self.format_var = tk.StringVar(value="Paper")
        self.format_drop = ttk.Combobox(form, textvariable=self.format_var, values=["Paper", "PDF", "EPUB"], state="readonly")
        self.format_drop.grid(row=3, column=0, padx=5, pady=(0, 5), sticky="ew")
        self.format_drop.bind("<<ComboboxSelected>>", self.on_format_change)
        
        tk.Label(form, text="Offer Type", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION, anchor="w").grid(row=2, column=1, sticky="w", padx=5, pady=(5, 1))
        self.list_type_var = tk.StringVar(value="Sell")
        self.list_type_drop = ttk.Combobox(form, textvariable=self.list_type_var, values=["Sell", "Exchange"], state="readonly")
        self.list_type_drop.grid(row=3, column=1, padx=5, pady=(0, 5), sticky="ew")
        self.list_type_drop.bind("<<ComboboxSelected>>", self.on_list_type_change)
        
        # Row 4: Pricing / Wanted / URL (Dynamic container)
        self.dynamic_frame = tk.Frame(form, bg=BG_SURFACE)
        self.dynamic_frame.grid(row=4, column=0, columnspan=2, sticky="ew")
        self.dynamic_frame.columnconfigure(0, weight=1)
        self.dynamic_frame.columnconfigure(1, weight=1)
        
        self.price_input = ModernInput(self.dynamic_frame, label_text="Price ($)", placeholder="e.g. 10.99")
        self.price_input.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.wanted_input = ModernInput(self.dynamic_frame, label_text="Wanted Book (Exchange)", placeholder="e.g. 1984")
        
        self.url_input = ModernInput(self.dynamic_frame, label_text="Download Filename/URL", placeholder="e.g. book.pdf")
        
        # Row 5: Description
        tk.Label(form, text="Book Description", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION, anchor="w").grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=(5, 1))
        desc_border = tk.Frame(form, bg=BORDER_COLOR, padx=1, pady=1)
        desc_border.grid(row=6, column=0, columnspan=2, sticky="nsew", padx=5, pady=(0, 10))
        form.rowconfigure(6, weight=1)
        
        self.desc_text = tk.Text(
            desc_border, 
            bg=BG_SURFACE_LIGHT, 
            fg=TEXT_PRIMARY, 
            insertbackground=TEXT_PRIMARY, 
            relief="flat", 
            font=FONT_BODY,
            bd=0
        )
        self.desc_text.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Save Button
        btn_save = ModernButton(
            form,
            text="💾 Save Changes" if book else "🚀 Create Listing",
            command=self.handle_save,
            bg=ACCENT_PURPLE,
            hover_bg=ACCENT_PURPLE_HOVER,
            width=20
        )
        btn_save.grid(row=7, column=0, columnspan=2, pady=(10, 0))
        
        # Fill values if edit mode
        if book:
            self.title_input.set(book['title'])
            self.author_input.set(book['author'])
            self.lang_input.set(book['language'])
            self.genre_input.set(book['genre'])
            self.format_var.set(book['format'])
            self.list_type_var.set(book['listing_type'])
            self.desc_text.insert("1.0", book['description'])
            
            if book['listing_type'] == 'Exchange':
                self.wanted_input.set(book['wanted_book'] or "")
            else:
                self.price_input.set(f"{book['price']:.2f}")
                
            if book['format'] != 'Paper':
                self.url_input.set(book['download_url'] or "")
                
        # Trigger layout updates
        self.on_format_change(None)
        self.on_list_type_change(None)

    def on_format_change(self, event):
        fmt = self.format_var.get()
        if fmt != "Paper":
            self.url_input.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        else:
            self.url_input.grid_remove()

    def on_list_type_change(self, event):
        val = self.list_type_var.get()
        if val == "Exchange":
            self.price_input.grid_remove()
            self.wanted_input.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        else:
            self.wanted_input.grid_remove()
            self.price_input.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    def handle_save(self):
        title = self.title_input.get().strip()
        author = self.author_input.get().strip()
        lang = self.lang_input.get().strip()
        genre = self.genre_input.get().strip()
        fmt = self.format_var.get()
        list_type = self.list_type_var.get()
        desc = self.desc_text.get("1.0", tk.END).strip()
        
        price = 0.0
        wanted_book = None
        durl = None
        
        if not title or not author or not lang or not genre or not desc:
            self.controller.show_toast("Please fill in all general fields.", is_error=True)
            return
            
        if list_type == "Exchange":
            wanted_book = self.wanted_input.get().strip()
            if not wanted_book:
                self.controller.show_toast("Please provide the wanted book name.", is_error=True)
                return
        else:
            price_str = self.price_input.get().strip()
            if not price_str:
                self.controller.show_toast("Please provide the price.", is_error=True)
                return
            try:
                price = float(price_str)
                if price < 0:
                    raise ValueError()
            except ValueError:
                self.controller.show_toast("Price must be a valid positive number.", is_error=True)
                return
                
        if fmt != "Paper":
            durl = self.url_input.get().strip()
            if not durl:
                durl = f"{title.lower().replace(' ', '_')}.pdf" if fmt == "PDF" else f"{title.lower().replace(' ', '_')}.epub"
                
        try:
            if not self.book:
                # Add new book (owner_id = None means official book)
                db.add_book(
                    title=title,
                    author=author,
                    description=desc,
                    price=price,
                    language=lang.capitalize(),
                    genre=genre.capitalize(),
                    owner_id=None,
                    format=fmt,
                    download_url=durl,
                    listing_type=list_type,
                    wanted_book=wanted_book
                )
                self.controller.show_toast("Successfully created a new official listing!")
            else:
                # Update existing book
                db.admin_update_book(
                    self.book['id'],
                    title=title,
                    author=author,
                    description=desc,
                    price=price,
                    language=lang.capitalize(),
                    genre=genre.capitalize(),
                    format=fmt,
                    download_url=durl,
                    listing_type=list_type,
                    wanted_book=wanted_book
                )
                self.controller.show_toast("Successfully updated book metadata!")
                
            if self.refresh_callback:
                self.refresh_callback()
            self.destroy()
        except Exception as e:
            self.controller.show_toast(str(e), is_error=True)


class AdminStatsView(tk.Frame):
    """Admin statistics view that displays system summary cards and embedded Matplotlib charts."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        
        self.scroll_frame = ScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True)
        
        self.draw_stats()

    def draw_stats(self):
        container = self.scroll_frame.scrollable_frame
        
        # Title
        tk.Label(container, text="System Statistics & Platform Insights", fg=TEXT_PRIMARY, bg=BG_DARK, font=FONT_TITLE, anchor="w").pack(fill="x", pady=(0, 15))
        
        # Summary banners row
        stats = analytics.get_system_summary_stats()
        
        stats_row = tk.Frame(container, bg=BG_DARK)
        stats_row.pack(fill="x", pady=(0, 20))
        
        stat_boxes = [
            ("Total Registered Readers", f"{stats['total_users']} users", ACCENT_BLUE),
            ("Total Catalog Items", f"{stats['total_books']} books", ACCENT_PURPLE),
            ("Platform Transaction Volume", f"${stats['total_sales']:.2f}", SUCCESS_COLOR),
            ("Successfully Resolved Swaps", f"{stats['total_swaps']} swaps", WARNING_COLOR)
        ]
        
        for title, val, color in stat_boxes:
            box = tk.Frame(stats_row, bg=BG_SURFACE, padx=15, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
            box.pack(side="left", fill="both", expand=True, padx=5)
            
            tk.Label(box, text=title, fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION).pack(anchor="w")
            tk.Label(box, text=val, fg=color, bg=BG_SURFACE, font=(FONT_FAMILY, 14, "bold")).pack(anchor="w", pady=(3, 0))

        # Embedded system-wide analytics charts
        charts_header = tk.Label(container, text="Catalog and Marketplace Analytics", fg=TEXT_PRIMARY, bg=BG_DARK, font=FONT_SUBTITLE, anchor="w")
        charts_header.pack(fill="x", pady=(10, 10))
        
        charts_row = tk.Frame(container, bg=BG_DARK)
        charts_row.pack(fill="x", pady=5)
        
        # 1. Catalog format breakdown pie chart
        fmt_frame = tk.Frame(charts_row, bg=BG_SURFACE, highlightbackground=BORDER_COLOR, highlightthickness=1)
        fmt_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        fig_fmt = analytics.generate_system_format_chart()
        canvas_fmt = FigureCanvasTkAgg(fig_fmt, master=fmt_frame)
        canvas_fmt.draw()
        canvas_fmt.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # 2. Top genres bar chart
        genre_frame = tk.Frame(charts_row, bg=BG_SURFACE, highlightbackground=BORDER_COLOR, highlightthickness=1)
        genre_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        fig_genre = analytics.generate_system_genre_chart()
        canvas_genre = FigureCanvasTkAgg(fig_genre, master=genre_frame)
        canvas_genre.draw()
        canvas_genre.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)


class AdminUsersView(tk.Frame):
    """Admin view to monitor registered users, adjust funds/points, promote roles, or delete users."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        
        # Header Area
        header = tk.Frame(self, bg=BG_DARK)
        header.pack(fill="x", pady=(0, 15))
        
        title_lbl = tk.Label(header, text="User Account Management", fg=TEXT_PRIMARY, bg=BG_DARK, font=FONT_TITLE)
        title_lbl.pack(side="left")
        
        # Table Header
        table_hdr = tk.Frame(self, bg=BG_SURFACE, highlightbackground=BORDER_COLOR, highlightthickness=1, padx=15, pady=8)
        table_hdr.pack(fill="x", pady=(0, 5))
        table_hdr.columnconfigure(0, weight=1) # ID
        table_hdr.columnconfigure(1, weight=2) # Username
        table_hdr.columnconfigure(2, weight=3) # Email
        table_hdr.columnconfigure(3, weight=2) # Balance
        table_hdr.columnconfigure(4, weight=2) # Points
        table_hdr.columnconfigure(5, weight=1) # Role
        table_hdr.columnconfigure(6, weight=3) # Actions
        
        tk.Label(table_hdr, text="ID", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=0, sticky="ew")
        tk.Label(table_hdr, text="Username", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=1, sticky="ew")
        tk.Label(table_hdr, text="Email Address", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=2, sticky="ew")
        tk.Label(table_hdr, text="Balance", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=3, sticky="ew")
        tk.Label(table_hdr, text="Points", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=4, sticky="ew")
        tk.Label(table_hdr, text="Role", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=5, sticky="ew")
        tk.Label(table_hdr, text="Actions", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=6, sticky="ew")
        
        # Scrollable listings
        self.scroll_frame = ScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True)
        
        self.load_users()

    def load_users(self):
        for child in self.scroll_frame.scrollable_frame.winfo_children():
            child.destroy()
            
        users = db.admin_get_all_users()
        container = self.scroll_frame.scrollable_frame
        
        for i, user in enumerate(users):
            row_frame = tk.Frame(container, bg=BG_SURFACE_LIGHT if i % 2 == 0 else BG_SURFACE, padx=15, pady=8)
            row_frame.pack(fill="x", pady=2)
            row_frame.columnconfigure(0, weight=1)
            row_frame.columnconfigure(1, weight=2)
            row_frame.columnconfigure(2, weight=3)
            row_frame.columnconfigure(3, weight=2)
            row_frame.columnconfigure(4, weight=2)
            row_frame.columnconfigure(5, weight=1)
            row_frame.columnconfigure(6, weight=3)
            
            # Fields
            tk.Label(row_frame, text=f"#{user['id']}", fg=TEXT_SECONDARY, bg=row_frame.cget("bg"), font=FONT_BODY).grid(row=0, column=0, sticky="w")
            tk.Label(row_frame, text=user['username'], fg=TEXT_PRIMARY, bg=row_frame.cget("bg"), font=FONT_BODY_BOLD).grid(row=0, column=1, sticky="w")
            tk.Label(row_frame, text=user['email'], fg=TEXT_SECONDARY, bg=row_frame.cget("bg"), font=FONT_BODY).grid(row=0, column=2, sticky="w")
            tk.Label(row_frame, text=f"${user['balance']:.2f}", fg=SUCCESS_COLOR, bg=row_frame.cget("bg"), font=FONT_BODY_BOLD).grid(row=0, column=3, sticky="w")
            
            uzs_equiv = user['points'] * 1000
            tk.Label(row_frame, text=f"{user['points']} pts\n({uzs_equiv:,} UZS)", fg=WARNING_COLOR, bg=row_frame.cget("bg"), font=FONT_CAPTION, justify="left").grid(row=0, column=4, sticky="w")
            
            role_str = "Admin" if user['is_admin'] else "User"
            role_color = ACCENT_PURPLE if user['is_admin'] else TEXT_SECONDARY
            tk.Label(row_frame, text=role_str, fg=role_color, bg=row_frame.cget("bg"), font=FONT_BODY_BOLD).grid(row=0, column=5, sticky="w")
            
            # Actions
            act_frame = tk.Frame(row_frame, bg=row_frame.cget("bg"))
            act_frame.grid(row=0, column=6, sticky="e")
            
            is_master = user['username'] == 'admin'
            
            btn_edit = ModernButton(
                act_frame,
                text="✏️ Edit",
                command=lambda u=user: self.edit_user(u),
                bg=ACCENT_BLUE,
                hover_bg="#2563EB",
                padding=(6, 2),
                font=FONT_CAPTION
            )
            btn_edit.pack(side="left", padx=2)
            
            if not is_master:
                btn_role = ModernButton(
                    act_frame,
                    text="👑 Toggle Role",
                    command=lambda u_id=user['id']: self.toggle_role(u_id),
                    bg=ACCENT_PURPLE,
                    hover_bg=ACCENT_PURPLE_HOVER,
                    padding=(6, 2),
                    font=FONT_CAPTION
                )
                btn_role.pack(side="left", padx=2)
                
                btn_del = ModernButton(
                    act_frame,
                    text="🗑️ Delete",
                    command=lambda u_id=user['id']: self.delete_user(u_id),
                    bg=ERROR_COLOR,
                    hover_bg="#DC2626",
                    padding=(6, 2),
                    font=FONT_CAPTION
                )
                btn_del.pack(side="left", padx=2)

    def edit_user(self, user):
        AdminEditUserModal(self, self.controller, user, self.load_users)

    def toggle_role(self, user_id):
        try:
            db.admin_toggle_user_admin(user_id)
            self.controller.show_toast("User role toggled successfully!")
            self.load_users()
        except Exception as e:
            self.controller.show_toast(str(e), is_error=True)

    def delete_user(self, user_id):
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this user from the system?")
        if confirm:
            try:
                db.admin_delete_user(user_id)
                self.controller.show_toast("User account deleted successfully!")
                self.load_users()
            except Exception as e:
                self.controller.show_toast(str(e), is_error=True)


class AdminEditUserModal(tk.Toplevel):
    """Modal dialog to adjust a user's balance and bonus points."""
    def __init__(self, parent, controller, user, refresh_callback):
        super().__init__(parent)
        self.controller = controller
        self.user = user
        self.refresh_callback = refresh_callback
        
        self.title(f"Adjust: {user['username']}")
        self.geometry("400x320")
        self.configure(bg=BG_DARK)
        self.transient(parent)
        self.grab_set()
        
        tk.Label(self, text=f"👤 Adjust User: {user['username']}", fg=TEXT_PRIMARY, bg=BG_DARK, font=FONT_SUBTITLE).pack(pady=15)
        
        form = tk.Frame(self, bg=BG_SURFACE, padx=20, text="", pady=20, highlightbackground=BORDER_COLOR, highlightthickness=1)
        form.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.balance_input = ModernInput(form, label_text="Adjust Balance ($)", placeholder=f"Current: ${user['balance']:.2f}")
        self.balance_input.pack(fill="x", pady=10)
        self.balance_input.set(f"{user['balance']:.2f}")
        
        self.points_input = ModernInput(form, label_text="Adjust Bonus Points", placeholder=f"Current: {user['points']} pts")
        self.points_input.pack(fill="x", pady=10)
        self.points_input.set(str(user['points']))
        
        btn_save = ModernButton(
            form,
            text="💾 Save Adjustments",
            command=self.handle_save,
            bg=ACCENT_PURPLE,
            hover_bg=ACCENT_PURPLE_HOVER,
            width=20
        )
        btn_save.pack(pady=(15, 0))

    def handle_save(self):
        bal_str = self.balance_input.get().strip()
        pts_str = self.points_input.get().strip()
        
        try:
            balance = float(bal_str)
            points = int(pts_str)
            if balance < 0 or points < 0:
                raise ValueError()
        except ValueError:
            self.controller.show_toast("Values must be non-negative numbers.", is_error=True)
            return
            
        try:
            db.admin_update_user_balance_points(self.user['id'], balance, points)
            self.controller.show_toast("User statistics adjusted successfully!")
            self.refresh_callback()
            self.destroy()
        except Exception as e:
            self.controller.show_toast(str(e), is_error=True)


class AdminReviewsView(tk.Frame):
    """Панель администратора для просмотра и удаления отзывов."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        
        # Header Area
        header = tk.Frame(self, bg=BG_DARK)
        header.pack(fill="x", pady=(0, 15))
        
        title_lbl = tk.Label(header, text="Review Moderation", fg=TEXT_PRIMARY, bg=BG_DARK, font=FONT_TITLE)
        title_lbl.pack(side="left")
        
        # Table Header
        table_hdr = tk.Frame(self, bg=BG_SURFACE, highlightbackground=BORDER_COLOR, highlightthickness=1, padx=15, pady=8)
        table_hdr.pack(fill="x", pady=(0, 5))
        table_hdr.columnconfigure(0, weight=2) # Book
        table_hdr.columnconfigure(1, weight=2) # User (Reviewer)
        table_hdr.columnconfigure(2, weight=1) # Rating
        table_hdr.columnconfigure(3, weight=2) # Date
        table_hdr.columnconfigure(4, weight=4) # Comment
        table_hdr.columnconfigure(5, weight=2) # Actions
        
        tk.Label(table_hdr, text="Book Title", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=0, sticky="ew")
        tk.Label(table_hdr, text="Reviewer", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=1, sticky="ew")
        tk.Label(table_hdr, text="Rating", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=2, sticky="ew")
        tk.Label(table_hdr, text="Date", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=3, sticky="ew")
        tk.Label(table_hdr, text="Comment", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=4, sticky="ew")
        tk.Label(table_hdr, text="Actions", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=5, sticky="ew")
        
        # Scrollable listings
        self.scroll_frame = ScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True)
        
        self.load_reviews()

    def load_reviews(self):
        for child in self.scroll_frame.scrollable_frame.winfo_children():
            child.destroy()
            
        reviews = db.admin_get_all_reviews()
        container = self.scroll_frame.scrollable_frame
        
        if not reviews:
            tk.Label(container, text="No reviews submitted in the system.", fg=TEXT_SECONDARY, bg=BG_DARK, font=FONT_BODY).pack(pady=40)
            return
            
        for i, rev in enumerate(reviews):
            row_frame = tk.Frame(container, bg=BG_SURFACE_LIGHT if i % 2 == 0 else BG_SURFACE, padx=15, pady=8)
            row_frame.pack(fill="x", pady=2)
            row_frame.columnconfigure(0, weight=2)
            row_frame.columnconfigure(1, weight=2)
            row_frame.columnconfigure(2, weight=1)
            row_frame.columnconfigure(3, weight=2)
            row_frame.columnconfigure(4, weight=4)
            row_frame.columnconfigure(5, weight=2)
            
            # Fields
            tk.Label(row_frame, text=rev['book_title'], fg=TEXT_PRIMARY, bg=row_frame.cget("bg"), font=FONT_BODY_BOLD, justify="left", anchor="w", wraplength=130).grid(row=0, column=0, sticky="w")
            tk.Label(row_frame, text=rev['reviewer_name'], fg=TEXT_PRIMARY, bg=row_frame.cget("bg"), font=FONT_BODY, justify="left", anchor="w").grid(row=0, column=1, sticky="w")
            
            # Rating stars/dots
            rating_frame = tk.Frame(row_frame, bg=row_frame.cget("bg"))
            rating_frame.grid(row=0, column=2, sticky="w")
            StarRating(rating_frame, rating=rev['rating'], size=10, bg=row_frame.cget("bg")).pack(side="left")
            
            tk.Label(row_frame, text=rev['date'].split()[0], fg=TEXT_SECONDARY, bg=row_frame.cget("bg"), font=FONT_BODY).grid(row=0, column=3, sticky="w")
            tk.Label(row_frame, text=rev['comment'], fg=TEXT_SECONDARY, bg=row_frame.cget("bg"), font=FONT_BODY, justify="left", anchor="w", wraplength=250).grid(row=0, column=4, sticky="w")
            
            # Action Buttons
            btn_frame = tk.Frame(row_frame, bg=row_frame.cget("bg"))
            btn_frame.grid(row=0, column=5, sticky="e")
            
            btn_del = ModernButton(
                btn_frame,
                text="🗑️ Delete",
                command=lambda r_id=rev['id']: self.delete_review(r_id),
                bg=ERROR_COLOR,
                hover_bg="#DC2626",
                padding=(8, 3),
                font=FONT_CAPTION
            )
            btn_del.pack(side="right", padx=2)

    def delete_review(self, review_id):
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this review?")
        if confirm:
            try:
                db.admin_delete_review(review_id)
                self.controller.show_toast("Review deleted successfully!")
                self.load_reviews()
            except Exception as e:
                self.controller.show_toast(str(e), is_error=True)


class AdminTransactionsView(tk.Frame):
    """Admin view to monitor all platform sales, purchases, and delivery status logs."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        
        # Header Area
        header = tk.Frame(self, bg=BG_DARK)
        header.pack(fill="x", pady=(0, 15))
        
        title_lbl = tk.Label(header, text="System Transaction Audits", fg=TEXT_PRIMARY, bg=BG_DARK, font=FONT_TITLE)
        title_lbl.pack(side="left")
        
        # Table Header
        table_hdr = tk.Frame(self, bg=BG_SURFACE, highlightbackground=BORDER_COLOR, highlightthickness=1, padx=15, pady=8)
        table_hdr.pack(fill="x", pady=(0, 5))
        table_hdr.columnconfigure(0, weight=1) # ID
        table_hdr.columnconfigure(1, weight=3) # Book
        table_hdr.columnconfigure(2, weight=2) # Buyer
        table_hdr.columnconfigure(3, weight=2) # Seller
        table_hdr.columnconfigure(4, weight=1) # Price
        table_hdr.columnconfigure(5, weight=2) # Date
        table_hdr.columnconfigure(6, weight=2) # Status
        table_hdr.columnconfigure(7, weight=2) # Actions
        
        tk.Label(table_hdr, text="ID", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=0, sticky="ew")
        tk.Label(table_hdr, text="Book Purchased", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=1, sticky="ew")
        tk.Label(table_hdr, text="Buyer", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=2, sticky="ew")
        tk.Label(table_hdr, text="Seller", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=3, sticky="ew")
        tk.Label(table_hdr, text="Price", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=4, sticky="ew")
        tk.Label(table_hdr, text="Date", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=5, sticky="ew")
        tk.Label(table_hdr, text="Status", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=6, sticky="ew")
        tk.Label(table_hdr, text="Actions", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, anchor="w").grid(row=0, column=7, sticky="ew")
        
        # Scrollable listings
        self.scroll_frame = ScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True)
        
        self.load_transactions()

    def load_transactions(self):
        for child in self.scroll_frame.scrollable_frame.winfo_children():
            child.destroy()
            
        txs = db.admin_get_all_transactions()
        container = self.scroll_frame.scrollable_frame
        
        if not txs:
            tk.Label(container, text="No transactions recorded yet in the system.", fg=TEXT_SECONDARY, bg=BG_DARK, font=FONT_BODY).pack(pady=40)
            return
            
        for i, tx in enumerate(txs):
            row_frame = tk.Frame(container, bg=BG_SURFACE_LIGHT if i % 2 == 0 else BG_SURFACE, padx=15, pady=8)
            row_frame.pack(fill="x", pady=2)
            row_frame.columnconfigure(0, weight=1)
            row_frame.columnconfigure(1, weight=3)
            row_frame.columnconfigure(2, weight=2)
            row_frame.columnconfigure(3, weight=2)
            row_frame.columnconfigure(4, weight=1)
            row_frame.columnconfigure(5, weight=2)
            row_frame.columnconfigure(6, weight=2)
            row_frame.columnconfigure(7, weight=2)
            
            # Fields
            tk.Label(row_frame, text=f"TX#{tx['id']}", fg=TEXT_SECONDARY, bg=row_frame.cget("bg"), font=FONT_BODY).grid(row=0, column=0, sticky="w")
            tk.Label(row_frame, text=tx['book_title'], fg=TEXT_PRIMARY, bg=row_frame.cget("bg"), font=FONT_BODY_BOLD, justify="left", anchor="w").grid(row=0, column=1, sticky="w")
            tk.Label(row_frame, text=tx['buyer_name'], fg=TEXT_PRIMARY, bg=row_frame.cget("bg"), font=FONT_BODY).grid(row=0, column=2, sticky="w")
            
            seller = tx['seller_name'] if tx['seller_name'] else "Official Store"
            tk.Label(row_frame, text=seller, fg=TEXT_PRIMARY, bg=row_frame.cget("bg"), font=FONT_BODY).grid(row=0, column=3, sticky="w")
            
            price_val = "Swap (Free)" if tx['price'] == 0 else f"${tx['price']:.2f}"
            tk.Label(row_frame, text=price_val, fg=TEXT_PRIMARY, bg=row_frame.cget("bg"), font=FONT_BODY_BOLD).grid(row=0, column=4, sticky="w")
            tk.Label(row_frame, text=tx['date'].split()[0], fg=TEXT_SECONDARY, bg=row_frame.cget("bg"), font=FONT_BODY).grid(row=0, column=5, sticky="w")
            
            status = tx['status']
            status_color = WARNING_COLOR if status == 'Pending' else ACCENT_BLUE if status == 'Shipped' else SUCCESS_COLOR
            tk.Label(row_frame, text=status.upper(), fg=status_color, bg=row_frame.cget("bg"), font=FONT_BODY_BOLD).grid(row=0, column=6, sticky="w")
            
            # Actions
            btn_view = ModernButton(
                row_frame,
                text="🔍 Track Logs",
                command=lambda t=tx: self.view_tracking_logs(t),
                bg=ACCENT_BLUE,
                hover_bg="#2563EB",
                padding=(8, 3),
                font=FONT_CAPTION
            )
            btn_view.grid(row=0, column=7, sticky="e")

    def view_tracking_logs(self, tx):
        AdminTrackingModal(self, tx)


class AdminTrackingModal(tk.Toplevel):
    """Modal displaying full shipment logs and routing context for system audits."""
    def __init__(self, parent, tx):
        super().__init__(parent)
        self.parent = parent
        self.tx_id = tx['id']
        
        self.title(f"Shipment Logs: TX#{self.tx_id}")
        self.geometry("520x620")
        self.configure(bg=BG_DARK)
        self.transient(parent)
        self.grab_set()
        
        self.draw_modal()

    def draw_modal(self):
        # Clear existing widgets if any
        for widget in self.winfo_children():
            widget.destroy()
            
        # Re-fetch transaction to get the latest status and timeline
        txs = db.admin_get_all_transactions()
        self.tx = next((t for t in txs if t['id'] == self.tx_id), None)
        if not self.tx:
            self.destroy()
            return
            
        tk.Label(self, text=f"📦 Transaction Audit Logs (TX#{self.tx['id']})", fg=TEXT_PRIMARY, bg=BG_DARK, font=FONT_SUBTITLE).pack(pady=15)
        
        box = tk.Frame(self, bg=BG_SURFACE, padx=20, pady=20, highlightbackground=BORDER_COLOR, highlightthickness=1)
        box.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Meta info
        info_lines = [
            ("Book Item:", self.tx['book_title']),
            ("Deliver To:", self.tx['delivery_address']),
            ("Order Date:", self.tx['date']),
            ("Current Status:", self.tx['status'].upper())
        ]
        for lbl, val in info_lines:
            row = tk.Frame(box, bg=BG_SURFACE)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=lbl, fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_BODY_BOLD, width=15, anchor="w").pack(side="left")
            tk.Label(row, text=val, fg=TEXT_PRIMARY, bg=BG_SURFACE, font=FONT_BODY, anchor="w").pack(side="left")
            
        tk.Frame(box, height=1, bg=BORDER_COLOR).pack(fill="x", pady=10)
        
        # Timeline Scrollbox
        tk.Label(box, text="Shipment History Timeline:", fg=TEXT_SECONDARY, bg=BG_SURFACE, font=FONT_CAPTION, anchor="w").pack(fill="x", pady=(0, 5))
        
        logs_frame = ScrollableFrame(box)
        logs_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        timeline_container = logs_frame.scrollable_frame
        for log in self.tx['tracking_info'].strip().split("\n"):
            if log:
                tk.Label(timeline_container, text=log, fg=TEXT_PRIMARY, bg=BG_DARK, font=FONT_CAPTION, anchor="w", justify="left", wraplength=400, padx=8, pady=4).pack(fill="x", pady=2)
                
        # Admin Override Controls
        ctrl_frame = tk.Frame(box, bg=BG_SURFACE_LIGHT, padx=12, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        ctrl_frame.pack(fill="x", side="bottom")
        ctrl_frame.columnconfigure(1, weight=1)
        
        tk.Label(ctrl_frame, text="Admin Override Controls", fg=TEXT_PRIMARY, bg=BG_SURFACE_LIGHT, font=FONT_BODY_BOLD).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        
        tk.Label(ctrl_frame, text="Update Status:", fg=TEXT_SECONDARY, bg=BG_SURFACE_LIGHT, font=FONT_CAPTION).grid(row=1, column=0, sticky="w")
        self.status_var = tk.StringVar(value=self.tx['status'])
        self.status_drop = ttk.Combobox(ctrl_frame, textvariable=self.status_var, values=["Pending", "Shipped", "Delivered"], state="readonly", width=12)
        self.status_drop.grid(row=1, column=1, sticky="w", padx=10)
        
        tk.Label(ctrl_frame, text="Tracking Note:", fg=TEXT_SECONDARY, bg=BG_SURFACE_LIGHT, font=FONT_CAPTION).grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.note_entry = tk.Entry(ctrl_frame, bg=BG_SURFACE, fg=TEXT_PRIMARY, relief="flat", font=FONT_BODY)
        self.note_entry.grid(row=2, column=1, sticky="ew", padx=10, pady=(8, 0))
        
        btn_update = ModernButton(
            ctrl_frame,
            text="💾 Update Status & Log",
            command=self.update_status,
            bg=ACCENT_PURPLE,
            hover_bg=ACCENT_PURPLE_HOVER,
            padding=(10, 4),
            font=FONT_CAPTION
        )
        btn_update.grid(row=3, column=0, columnspan=2, pady=(12, 0))

    def update_status(self):
        new_status = self.status_var.get()
        note = self.note_entry.get().strip()
        if not note:
            note = f"Status updated to {new_status} by system administrator."
            
        try:
            db.update_transaction_status(self.tx_id, new_status, note)
            self.parent.controller.show_toast("Transaction tracking timeline updated successfully!")
            self.parent.load_transactions()
            self.draw_modal()
        except Exception as e:
            self.parent.controller.show_toast(str(e), is_error=True)