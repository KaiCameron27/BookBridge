import os
import sys
import unittest
import mysql.connector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db
import analytics

class TestBookBridgeDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Override database to a testing database
        db.MYSQL_CONFIG['database'] = 'test_bookbridge'
        
        # Drop and recreate test database
        try:
            conn = db.get_connection(include_db=False)
            cursor = conn.cursor()
            cursor.execute("DROP DATABASE IF EXISTS test_bookbridge;")
            cursor.execute("CREATE DATABASE test_bookbridge;")
            conn.commit()
            cursor.close()
            conn.close()
        except mysql.connector.Error as e:
            raise unittest.SkipTest(f"Failed to connect to MySQL server. Please make sure MySQL Server is running and configure credentials in database.py. Details: {e}")
            
        db.init_db()

    @classmethod
    def tearDownClass(cls):
        # Optional cleanup
        try:
            conn = db.get_connection(include_db=False)
            cursor = conn.cursor()
            cursor.execute("DROP DATABASE IF EXISTS test_bookbridge;")
            conn.commit()
            cursor.close()
            conn.close()
        except Exception:
            pass

    def test_1_database_seeding(self):
        """Verifies database created the seed records, including E-books."""
        books = db.get_available_books()
        self.assertGreaterEqual(len(books), 10, "There should be at least 10 seeded books.")
        
        # Verify e-books are seeded
        ebooks = [b for b in books if b['format'] in ('PDF', 'EPUB')]
        self.assertGreaterEqual(len(ebooks), 2, "There should be E-books seeded.")
        self.assertIsNotNone(ebooks[0]['download_url'])

    def test_2_user_registration_and_login(self):
        """Verifies adding users and checking credentials."""
        user_id = db.add_user("testuser", "password123", "test@bookbridge.com", "123 Story Road, NYC")
        self.assertIsNotNone(user_id)
        
        dup_id = db.add_user("testuser", "password456", "dup@bookbridge.com", "456 Main St")
        self.assertIsNone(dup_id)
        
        valid_user = db.verify_user("testuser", "password123")
        self.assertIsNotNone(valid_user)
        self.assertEqual(valid_user['email'], "test@bookbridge.com")

    def test_3_list_and_search_books(self):
        """Verifies listing secondary books (for sale and exchange)."""
        seller_id = db.add_user("seller_bob", "pass1", "bob@example.com", "Bob Cabin")
        
        # List a book for exchange
        book_id = db.add_book(
            title="The Hobbit Legacy",
            author="J.R.R. Tolkien",
            description="Exchange copies welcomed.",
            price=0.0,
            language="English",
            genre="Fantasy",
            owner_id=seller_id,
            listing_type="Exchange",
            wanted_book="The Silmarillion"
        )
        self.assertIsNotNone(book_id)
        
        # Search by keyword
        results = db.get_available_books(search_query="Hobbit Legacy")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['wanted_book'], "The Silmarillion")
        self.assertEqual(results[0]['listing_type'], "Exchange")

    def test_4_purchase_and_ledgers(self):
        """Verifies buy flow, balance updates, and transaction logging."""
        buyer_id = db.add_user("buyer_alice", "pass2", "alice@example.com", "Alice Place")
        
        # Seed a book for sale
        bob = db.verify_user("seller_bob", "pass1")
        bob_id = bob['id']
        book_id = db.add_book(
            title="Design Patterns",
            author="Gang of Four",
            description="Must read.",
            price=40.00,
            language="English",
            genre="Fiction",
            owner_id=bob_id
        )
        
        # Purchase book
        success = db.buy_book(buyer_id, book_id, "Alice Place")
        self.assertTrue(success)
        
        # Verify balance changes
        updated_buyer = db.get_user_by_id(buyer_id)
        self.assertEqual(updated_buyer['balance'], 60.00)  # 100 - 40
        
        updated_seller = db.get_user_by_id(bob_id)
        self.assertEqual(updated_seller['balance'], 140.00) # 100 + 40

    def test_5_analytics_plots(self):
        """Verifies analytics generator outputs valid Matplotlib figures."""
        user = db.verify_user("buyer_alice", "pass2")
        self.assertIsNotNone(user)
        
        fig_genre = analytics.generate_genre_chart(user['id'])
        self.assertIsNotNone(fig_genre)
        
        fig_spend = analytics.generate_spending_chart(user['id'])
        self.assertIsNotNone(fig_spend)

    def test_6_messaging_system(self):
        """Verifies sending messages and reading chat history."""
        user1 = db.verify_user("buyer_alice", "pass2")
        user2 = db.verify_user("seller_bob", "pass1")
        
        books = db.get_available_books()
        book_id = books[0]['id']
        
        db.send_message(user1['id'], user2['id'], book_id, "Hello! Is it available?")
        db.send_message(user2['id'], user1['id'], book_id, "Yes, it is!")
        
        history = db.get_chat_history(user1['id'], user2['id'], book_id)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['message'], "Hello! Is it available?")
        self.assertEqual(history[1]['message'], "Yes, it is!")
        
        chats = db.get_user_chats(user1['id'])
        self.assertGreaterEqual(len(chats), 1)
        self.assertEqual(chats[0]['other_username'], "seller_bob")

    def test_7_bonus_points(self):
        """Verifies that buying awards points and points can be redeemed for store cash."""
        uid = db.add_user("points_user", "pass", "points@test.com", "Main Rd")
        user = db.get_user_by_id(uid)
        self.assertEqual(user['points'], 0)
        
        book_id = db.add_book("Test Book", "Author", "Desc", 20.00, "English", "Fiction", None)
        db.buy_book(uid, book_id, "Main Rd")
        
        user_after = db.get_user_by_id(uid)
        self.assertEqual(user_after['points'], 250)
        
        cash = db.redeem_points(uid, 200)
        self.assertEqual(cash, 2.00)
        
        user_redeemed = db.get_user_by_id(uid)
        self.assertEqual(user_redeemed['points'], 50)
        self.assertEqual(user_redeemed['balance'], 82.00)

    def test_8_book_exchange(self):
        """Verifies exchange proposals and swap owner resolutions."""
        user_a = db.add_user("user_a", "pass", "a@test.com", "Loc A")
        user_b = db.add_user("user_b", "pass", "b@test.com", "Loc B")
        
        book_a = db.add_book("Book A", "Author A", "D1", 0.0, "English", "Fiction", user_a, listing_type="Exchange", wanted_book="Book B")
        book_b = db.add_book("Book B", "Author B", "D2", 0.0, "English", "Fiction", user_b, listing_type="Exchange", wanted_book="Book A")
        
        db.propose_exchange(user_a, user_b, book_a, book_b)
        
        proposals = db.get_received_exchange_proposals(user_b)
        self.assertEqual(len(proposals), 1)
        self.assertEqual(proposals[0]['proposer_name'], "user_a")
        
        db.respond_to_exchange(proposals[0]['id'], "Accepted")
        
        updated_a = db.get_book_by_id(book_a)
        updated_b = db.get_book_by_id(book_b)
        
        self.assertEqual(updated_a['owner_id'], user_b)
        self.assertEqual(updated_b['owner_id'], user_a)
        self.assertTrue(updated_a['is_sold'])
        self.assertTrue(updated_b['is_sold'])

    def test_9_admin_operations(self):
        """Verifies admin catalog operations (get all, update, delete)."""
        # Verify the seeded admin user
        admin = db.verify_user("admin", "admin123")
        self.assertIsNotNone(admin)
        self.assertEqual(admin['is_admin'], 1)
        
        # Test admin add book
        book_id = db.add_book(
            title="Admin Book",
            author="Admin Author",
            description="Official guide",
            price=9.99,
            language="English",
            genre="Fiction",
            owner_id=None
        )
        self.assertIsNotNone(book_id)
        
        # Test admin get all
        all_books = db.admin_get_all_books()
        my_book = [b for b in all_books if b['id'] == book_id]
        self.assertEqual(len(my_book), 1)
        self.assertEqual(my_book[0]['title'], "Admin Book")
        
        # Test admin update
        success = db.admin_update_book(
            book_id,
            title="Admin Book Updated",
            author="Admin Author",
            description="Official updated guide",
            price=12.99,
            language="English",
            genre="Fiction",
            format="Paper",
            download_url=None,
            listing_type="Sell",
            wanted_book=None
        )
        self.assertTrue(success)
        
        updated_book = db.get_book_by_id(book_id)
        self.assertEqual(updated_book['title'], "Admin Book Updated")
        self.assertEqual(updated_book['price'], 12.99)
        
        # Test admin delete
        del_success = db.admin_delete_book(book_id)
        self.assertTrue(del_success)
        
        deleted_book = db.get_book_by_id(book_id)
        self.assertIsNone(deleted_book)
        
        # Test admin review operations
        user_id = db.add_user("review_user", "password", "reviewer@test.com", "Address")
        book_id2 = db.add_book("Review Book", "Author", "Desc", 10.00, "English", "Fiction", None)
        review_success = db.add_review(book_id2, user_id, 4, "A nice read!")
        self.assertTrue(review_success)
        
        all_reviews = db.admin_get_all_reviews()
        my_review = [r for r in all_reviews if r['comment'] == "A nice read!"]
        self.assertEqual(len(my_review), 1)
        self.assertEqual(my_review[0]['reviewer_name'], "review_user")
        self.assertEqual(my_review[0]['book_title'], "Review Book")
        
        del_rev_success = db.admin_delete_review(my_review[0]['id'])
        self.assertTrue(del_rev_success)
        
        all_reviews_after = db.admin_get_all_reviews()
        my_review_after = [r for r in all_reviews_after if r['comment'] == "A nice read!"]
        self.assertEqual(len(my_review_after), 0)
        
        # Test admin transaction overrides
        buyer_id = db.add_user("buyer_tx", "password", "buyer_tx@test.com", "Buyer Address")
        db.buy_book(buyer_id, book_id2, "Buyer Address")
        
        txs = db.admin_get_all_transactions()
        my_tx = [t for t in txs if t['buyer_name'] == "buyer_tx"]
        self.assertEqual(len(my_tx), 1)
        self.assertEqual(my_tx[0]['status'], "Pending")
        
        db.update_transaction_status(my_tx[0]['id'], "Shipped", "Shipped by admin courier service.")
        
        txs_after = db.admin_get_all_transactions()
        my_tx_after = [t for t in txs_after if t['id'] == my_tx[0]['id']]
        self.assertEqual(my_tx_after[0]['status'], "Shipped")
        self.assertIn("Shipped by admin courier service.", my_tx_after[0]['tracking_info'])

if __name__ == "__main__":
    print("Running automated verification tests for BookBridge Phase 2 on MySQL...")
    unittest.main()