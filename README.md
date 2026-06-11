# 📚 BookBridge — The Ultimate Booklovers Marketplace

**BookBridge** is a feature-rich desktop marketplace application built with **Python**, **Tkinter**, and **MySQL**. It offers a complete platform for book enthusiasts to buy, sell, exchange (swap) books, discuss reviews, chat with other readers, and track delivery routes in real-time.

---

## 🌟 Key Features

### 👤 User Capabilities (Buyer & Seller Dashboard)
* **Browse Marketplace**: Search and filter available books by title, author, language, genre, and price.
* **Buy Books**: Instantly purchase books using your store wallet balance.
* **Earn & Redeem Points**: Earn bonus points on every purchase (12.5 points per $1) and redeem them for store cash.
* **Sell or Swap Books**: Create standard listings for sale or propose exchange deals ("Swap Book A for Book B").
* **Wishlist**: Save books to your personal wishlist.
* **Reviews & Ratings**: Rate books (1-5 stars) and write comments.
* **Private Chat System**: Chat directly with sellers/buyers regarding a specific listing.
* **Order Tracking**: Track your purchased books via a delivery history timeline.
* **Personal Analytics**: View spending charts and genre breakdowns built with Matplotlib.

### 👑 Administrator Capabilities (Admin Dashboard)
* **Inventory Control**: Add official books, edit metadata, and delete listings from the catalog.
* **User Management**: Adjust user wallet balances, modify bonus points, promote/demote administrator privileges, and delete user accounts.
* **Review Moderation**: View all platform reviews in a unified feed and delete spam or inappropriate remarks.
* **Transaction Audits**: Inspect all system-wide transactions (sales and swaps).
* **System Override & Timeline Logs**: Manually transition any order status (`Pending` ➔ `Shipped` ➔ `Delivered`) and append custom tracking timeline notes (e.g., *"Custom clearance delayed"*).
* **Platform Insights**: View system-wide metrics and charts representing catalog format ratios and top genres.

---

## 🛠️ Technology Stack

* **Language**: Python 3.13
* **GUI Framework**: Tkinter (with custom modern styling, glassmorphism, and Toast notifications)
* **Database**: MySQL Server
* **Analytics & Graphs**: Matplotlib, Pandas
* **Test Suite**: Unittest (Python standard library)

---

## ⚙️ Installation & Setup

### Prerequisites
1. **Python 3.13** (or higher) installed.
2. **MySQL Server** installed and running locally.
3. Install required Python packages:
   ```bash
   pip install mysql-connector-python pandas matplotlib
   ```

### Database Connection
Ensure your MySQL credentials match the connection configuration in `database.py`:
```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_MYSQL_ROOT_PASSWORD',
    'database': 'bookbridge',
    'port': 3306
}
```

### Running the App
Run the main script to automatically initialize the database schema, perform migrations, seed initial data, and launch the application:
```bash
python main.py
```

---

## 🧪 Testing

The codebase includes a comprehensive test suite covering database seeding, user registration, buy/sell flow, analytics generation, messaging, bonus points, book exchanges, review moderation, and admin overrides.

To run the automated tests:
```bash
python verify_app.py
```

---

## 🔑 Default Credentials

To test the **Administrator Dashboard**, log in with the following default credentials:
* **Username**: `admin`
* **Password**: `admin123`

To test the **User Dashboard**, register a new account through the Sign Up panel or log in with any seeded credentials.
