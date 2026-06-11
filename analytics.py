import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import mysql.connector
from database import get_connection

# Цветовое оформление графиков
BG_COLOR = "#1E1E1E"
TEXT_COLOR = "#E5E7EB"
ACCENT_COLORS = ["#3B82F6", "#8B5CF6", "#10B981", "#F59E0B", "#EF4444", "#EC4899", "#06B6D4"]

def configure_matplotlib_theme(fig, ax):
    """Применяет параметры темной темы к графикам"""
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    
    ax.spines['bottom'].set_color('#4B5563')
    ax.spines['top'].set_color('#4B5563')
    ax.spines['left'].set_color('#4B5563')
    ax.spines['right'].set_color('#4B5563')
    
    ax.tick_params(axis='x', colors=TEXT_COLOR)
    ax.tick_params(axis='y', colors=TEXT_COLOR)
    ax.yaxis.label.set_color(TEXT_COLOR)
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.title.set_color(TEXT_COLOR)

def generate_genre_chart(user_id):
    """Строит круговую диаграмму любимых жанров пользователя"""
    fig = Figure(figsize=(5, 3.5), dpi=100)
    ax = fig.add_subplot(111)
    
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT b.genre
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        WHERE t.buyer_id = %s;
    """
    cursor.execute(query, (user_id,))
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    df = pd.DataFrame(rows, columns=columns)
    
    cursor.close()
    conn.close()
    
    configure_matplotlib_theme(fig, ax)
    
    if df.empty:
        ax.text(0.5, 0.5, "No purchase history yet.\nBuy books to see genre breakdown!", 
                color=TEXT_COLOR, ha='center', va='center', fontsize=11, wrap=True)
        ax.axis('off')
        ax.set_title("Favorite Genres", pad=10, fontsize=12, fontweight='bold')
        return fig
        
    genre_counts = df['genre'].value_counts()
    
    wedges, texts, autotexts = ax.pie(
        genre_counts, 
        labels=genre_counts.index, 
        autopct='%1.0f%%', 
        startangle=140, 
        colors=ACCENT_COLORS[:len(genre_counts)],
        textprops=dict(color=TEXT_COLOR)
    )
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_weight('bold')
        
    ax.set_title("Favorite Genres", pad=15, fontsize=12, fontweight='bold')
    fig.tight_layout()
    return fig

def generate_spending_chart(user_id):
    """Строит график ежемесячных трат пользователя на книги"""
    fig = Figure(figsize=(5, 3.5), dpi=100)
    ax = fig.add_subplot(111)
    
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT price, date
        FROM transactions
        WHERE buyer_id = %s;
    """
    cursor.execute(query, (user_id,))
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    df = pd.DataFrame(rows, columns=columns)
    
    cursor.close()
    conn.close()
    
    configure_matplotlib_theme(fig, ax)
    
    if df.empty:
        ax.text(0.5, 0.5, "No spending history yet.\nYour purchase history will show up here.", 
                color=TEXT_COLOR, ha='center', va='center', fontsize=11, wrap=True)
        ax.axis('off')
        ax.set_title("Monthly Spending", pad=10, fontsize=12, fontweight='bold')
        return fig
        
    df['date'] = pd.to_datetime(df['date'])
    df['month_year'] = df['date'].dt.strftime('%b %Y')
    
    monthly_spending = df.groupby('month_year', sort=False)['price'].sum().reset_index()
    
    bars = ax.bar(
        monthly_spending['month_year'], 
        monthly_spending['price'], 
        color="#8B5CF6", 
        width=0.4,
        edgecolor="#A78BFA",
        linewidth=1
    )
    
    for bar in bars:
        yval = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2.0, 
            yval + (max(monthly_spending['price']) * 0.02), 
            f"${yval:.2f}", 
            ha='center', 
            va='bottom', 
            color=TEXT_COLOR, 
            fontsize=8
        )
        
    ax.set_ylabel("Spent ($)", fontsize=10)
    ax.set_title("Monthly Spending", pad=15, fontsize=12, fontweight='bold')
    
    ax.grid(axis='y', linestyle='--', alpha=0.2, color=TEXT_COLOR)
    ax.set_axisbelow(True)
    
    if not monthly_spending.empty:
        ax.set_ylim(0, max(monthly_spending['price']) * 1.15)
        
    fig.tight_layout()
    return fig

def get_profile_summary_stats(user_id):
    """Сбор статистики аккаунта для профиля"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT SUM(price) FROM transactions WHERE buyer_id = %s;", (user_id,))
    val = cursor.fetchone()[0]
    total_spent = val if val is not None else 0.0
    
    cursor.execute("SELECT SUM(price) FROM transactions WHERE seller_id = %s;", (user_id,))
    val = cursor.fetchone()[0]
    total_earned = val if val is not None else 0.0
    
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE buyer_id = %s;", (user_id,))
    books_bought = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE seller_id = %s;", (user_id,))
    books_sold = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM books WHERE owner_id = %s AND is_sold = 0;", (user_id,))
    active_listings = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return {
        "total_spent": total_spent,
        "total_earned": total_earned,
        "books_bought": books_bought,
        "books_sold": books_sold,
        "active_listings": active_listings
    }

def get_system_summary_stats():
    """Сбор статистики всей системы для админ-панели"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Total users (excluding admins)
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 0;")
    total_users = cursor.fetchone()[0]
    
    # 2. Total books
    cursor.execute("SELECT COUNT(*) FROM books;")
    total_books = cursor.fetchone()[0]
    
    # 3. Total transactions volume
    cursor.execute("SELECT SUM(price) FROM transactions;")
    val = cursor.fetchone()[0]
    total_sales = val if val is not None else 0.0
    
    # 4. Total swaps resolved
    cursor.execute("SELECT COUNT(*) FROM exchanges WHERE status = 'Accepted';")
    total_swaps = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return {
        "total_users": total_users,
        "total_books": total_books,
        "total_sales": total_sales,
        "total_swaps": total_swaps
    }

def generate_system_format_chart():
    """Диаграмма соотношения форматов книг в системе"""
    fig = Figure(figsize=(5, 3.5), dpi=100)
    ax = fig.add_subplot(111)
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT format FROM books;")
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    df = pd.DataFrame(rows, columns=columns)
    cursor.close()
    conn.close()
    
    configure_matplotlib_theme(fig, ax)
    
    if df.empty:
        ax.text(0.5, 0.5, "No books in system catalog.", color=TEXT_COLOR, ha='center', va='center')
        ax.axis('off')
        ax.set_title("Catalog by Format", pad=10, fontsize=12, fontweight='bold')
        return fig
        
    counts = df['format'].value_counts()
    
    wedges, texts, autotexts = ax.pie(
        counts, 
        labels=counts.index, 
        autopct='%1.0f%%', 
        startangle=90, 
        colors=ACCENT_COLORS[:len(counts)],
        textprops=dict(color=TEXT_COLOR)
    )
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_weight('bold')
        
    ax.set_title("Catalog by Format", pad=15, fontsize=12, fontweight='bold')
    fig.tight_layout()
    return fig

def generate_system_genre_chart():
    """Диаграмма популярности жанров книг в каталоге"""
    fig = Figure(figsize=(5, 3.5), dpi=100)
    ax = fig.add_subplot(111)
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT genre FROM books;")
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    df = pd.DataFrame(rows, columns=columns)
    cursor.close()
    conn.close()
    
    configure_matplotlib_theme(fig, ax)
    
    if df.empty:
        ax.text(0.5, 0.5, "No books in system catalog.", color=TEXT_COLOR, ha='center', va='center')
        ax.axis('off')
        ax.set_title("Popular Genres", pad=10, fontsize=12, fontweight='bold')
        return fig
        
    counts = df['genre'].value_counts().head(5)
    
    bars = ax.bar(
        counts.index, 
        counts.values, 
        color="#10B981", 
        width=0.4,
        edgecolor="#34D399",
        linewidth=1
    )
    
    for bar in bars:
        yval = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2.0, 
            yval + 0.1, 
            str(yval), 
            ha='center', 
            va='bottom', 
            color=TEXT_COLOR, 
            fontsize=8
        )
        
    ax.set_ylabel("Count", fontsize=10)
    ax.set_title("Popular Genres", pad=15, fontsize=12, fontweight='bold')
    ax.grid(axis='y', linestyle='--', alpha=0.2, color=TEXT_COLOR)
    ax.set_axisbelow(True)
    fig.tight_layout()
    return fig