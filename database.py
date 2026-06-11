import mysql.connector
from datetime import datetime

# Настройки подключения к вашему серверу MySQL
# Измените их, если у вас заданы пароль или порт в MySQL Workbench
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Kamron_2710SQL',       # Введите сюда ваш пароль к MySQL root
    'database': 'bookbridge',
    'port': 3306
}

def get_connection(include_db=True):
    """Возвращает соединение к MySQL. 
    Позволяет подключаться без указания конкретной БД (для её автоматического создания)."""
    config = MYSQL_CONFIG.copy()
    if not include_db:
        config.pop('database', None)
    
    conn = mysql.connector.connect(**config)
    return conn

def init_db():
    """Создает базу данных и все таблицы, если их нет, а также заполняет каталог книгами."""
    # Шаг 1: Подключение к серверу и создание базы данных
    conn = get_connection(include_db=False)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']};")
    conn.commit()
    cursor.close()
    conn.close()

    # Шаг 2: Подключение к базе данных и создание таблиц
    conn = get_connection(include_db=True)
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        balance DOUBLE DEFAULT 100.0,
        address TEXT NOT NULL,
        points INT DEFAULT 0,
        is_admin INT DEFAULT 0
    ) ENGINE=InnoDB;
    """)

    # Проверка и миграция для добавления колонки is_admin, если таблица users уже существовала
    try:
        cursor.execute("SHOW COLUMNS FROM users LIKE 'is_admin';")
        column_exists = cursor.fetchone()
        if not column_exists:
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin INT DEFAULT 0;")
            conn.commit()
    except Exception as e:
        print(f"Migration error for users table is_admin column: {e}")

    # Таблица книг
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        author VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        price DOUBLE NOT NULL,
        language VARCHAR(100) NOT NULL,
        genre VARCHAR(100) NOT NULL,
        owner_id INT,
        is_sold INT DEFAULT 0,
        date_added VARCHAR(100) NOT NULL,
        format VARCHAR(50) DEFAULT 'Paper',
        download_url VARCHAR(255),
        listing_type VARCHAR(50) DEFAULT 'Sell',
        wanted_book VARCHAR(255),
        FOREIGN KEY(owner_id) REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """)

    # Таблица транзакций (покупок)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        buyer_id INT NOT NULL,
        seller_id INT,
        book_id INT NOT NULL,
        price DOUBLE NOT NULL,
        status VARCHAR(50) NOT NULL,
        delivery_address TEXT NOT NULL,
        date VARCHAR(100) NOT NULL,
        tracking_info TEXT NOT NULL,
        FOREIGN KEY(buyer_id) REFERENCES users(id) ON DELETE RESTRICT,
        FOREIGN KEY(seller_id) REFERENCES users(id) ON DELETE SET NULL,
        FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE RESTRICT
    ) ENGINE=InnoDB;
    """)

    # Таблица отзывов
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INT AUTO_INCREMENT PRIMARY KEY,
        book_id INT NOT NULL,
        user_id INT NOT NULL,
        rating INT CHECK(rating BETWEEN 1 AND 5),
        comment TEXT NOT NULL,
        date VARCHAR(100) NOT NULL,
        FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """)

    # Таблица списка желаемого (wishlist)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wishlist (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        book_id INT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE,
        UNIQUE KEY user_book_uniq (user_id, book_id)
    ) ENGINE=InnoDB;
    """)

    # Таблица личных сообщений (чат)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INT AUTO_INCREMENT PRIMARY KEY,
        sender_id INT NOT NULL,
        receiver_id INT NOT NULL,
        book_id INT NOT NULL,
        message TEXT NOT NULL,
        timestamp VARCHAR(100) NOT NULL,
        FOREIGN KEY(sender_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(receiver_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """)

    # Таблица предложений обмена книгами
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exchanges (
        id INT AUTO_INCREMENT PRIMARY KEY,
        proposer_id INT NOT NULL,
        receiver_id INT NOT NULL,
        proposer_book_id INT NOT NULL,
        receiver_book_id INT NOT NULL,
        status VARCHAR(50) DEFAULT 'Pending',
        date VARCHAR(100) NOT NULL,
        FOREIGN KEY(proposer_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(receiver_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(proposer_book_id) REFERENCES books(id) ON DELETE CASCADE,
        FOREIGN KEY(receiver_book_id) REFERENCES books(id) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """)

    conn.commit()

    # Заполнение администратора по умолчанию
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin';")
    admin_count = cursor.fetchone()[0]
    if admin_count == 0:
        cursor.execute(
            "INSERT INTO users (username, password, email, address, balance, points, is_admin) VALUES ('admin', 'admin123', 'admin@bookbridge.com', 'Admin HQ', 100.0, 0, 1);"
        )
        conn.commit()

    # Заполнение каталога книг по умолчанию
    seed_books(conn)

    cursor.close()
    conn.close()

def seed_books(conn):
    """Заполняет каталог стандартными книгами разных форматов и языков."""
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    seeds = [
        # Don Quixote
        ("Don Quixote", "Miguel de Cervantes", "Alonso Quixano, an aging nobleman, becomes obsessed with chivalric romances and sets out as a knight-errant to revive chivalry.", 14.99, "English", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Don Quijote de la Mancha", "Miguel de Cervantes", "La historia del hidalgo Alonso Quijano, quien pierde la razón de tanto leer libros de caballerías y decide convertirse en caballero andante.", 14.99, "Spanish", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Дон Кихот", "Мигель де Сервантес", "История о приключениях идальго Алонсо Кихано, который, начитавшись рыцарских романов, решает стать странствующим рыцарем.", 14.99, "Russian", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Don Quichotte", "Miguel de Cervantes", "L'histoire d'Alonso Quichano, un gentilhomme campagnard obsédé par les romans de chevalerie, qui décide de devenir chevalier errant.", 14.99, "French", "Fiction", None, 0, now, "Paper", None, "Sell", None),

        # The Little Prince
        ("The Little Prince", "Antoine de Saint-Exupéry", "A pilot stranded in the desert meets a young prince who fallen to Earth from a tiny asteroid, sharing philosophical stories about human nature.", 9.99, "English", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("El Principito", "Antoine de Saint-Exupéry", "Un piloto varado en el desierto se encuentra con un pequeño príncipe que viene de otro planeta, quien le enseña el valor de la amistad y la vida.", 9.99, "Spanish", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Маленький принц", "Антуан де Сент-Экзюпери", "Философская сказка о дружбе, любви, верности и ответственности, рассказанная маленьким принцем, прилетевшим с астероида.", 9.99, "Russian", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Le Petit Prince", "Antoine de Saint-Exupéry", "Un pilote en panne dans le Sahara rencontre un petit garçon venu d'un astéroïde, qui lui raconte sa vie et ses voyages sur d'autres planètes.", 9.99, "French", "Fiction", None, 0, now, "Paper", None, "Sell", None),

        # One Hundred Years of Solitude
        ("One Hundred Years of Solitude", "Gabriel García Márquez", "The rise and fall, love and misfortune of the Buendía family in the mythical town of Macondo, a masterpiece of magical realism.", 15.99, "English", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Cien años de soledad", "Gabriel García Márquez", "La obra maestra del realismo mágico cuenta la historia de la familia Buendía a lo largo de siete generaciones en el pueblo de Macondo.", 15.99, "Spanish", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Сто лет одиночества", "Габриэль Гарсиа Маркес", "История семи поколений рода Буэндиа в отрезанном от мира городке Макондо, олицетворяющая историю человечества и одиночества.", 15.99, "Russian", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Cent ans de solitude", "Gabriel García Márquez", "La chronique de la famille Buendía sur sept générations dans le village imaginaire de Macondo, œuvre majeure du réalisme magique.", 15.99, "French", "Fiction", None, 0, now, "Paper", None, "Sell", None),

        # Crime and Punishment
        ("Crime and Punishment", "Fyodor Dostoevsky", "The mental anguish and moral dilemmas of Rodion Raskolnikov, an impoverished ex-student in Saint Petersburg who formulates a plan to kill an unscrupulous pawnbroker.", 12.99, "English", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Crimen y castigo", "Fiódor Dostoyevski", "La angustia mental y el dilema moral de Raskólnikov, un joven estudiante que asesina a una usurera usurpadora en San Petersburgo.", 12.99, "Spanish", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Преступление и наказание", "Фёдор Достоевский", "Психологический роман о бедном студенте Родионе Раскольникове, решившемся на убийство ради высшей цели, и его последующем раскаянии.", 12.99, "Russian", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Crime et Châtiment", "Fiodor Dostoïevski", "Le calvaire psychologique de Rodion Raskolnikov, un ancien étudiant qui commet le meurtre d'une vieille prêteuse sur gages.", 12.99, "French", "Fiction", None, 0, now, "Paper", None, "Sell", None),

        # The Great Gatsby
        ("The Great Gatsby", "F. Scott Fitzgerald", "A portrait of the Jazz Age in all its decadence and excess, exploring themes of wealth, class, and the elusive American Dream.", 11.99, "English", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("El gran Gatsby", "F. Scott Fitzgerald", "Una novela clásica sobre el misterioso millonario Jay Gatsby y su obsesión con la bella Daisy Buchanan durante la época del jazz.", 11.99, "Spanish", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Великий Гэтсби", "Ф. Скотт Фицджеральд", "Блистательный портрет «эпохи джаза» с её декадансом и излишествами, рассказывающий о трагической любви Джея Гэтсби к Дейзи Бьюкенен.", 11.99, "Russian", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Gatsby le Magnifique", "F. Scott Fitzgerald", "Une critique de l'illusion du rêve américain à travers le destin tragique du mystérieux millionnaire Jay Gatsby dans les années folles.", 11.99, "French", "Fiction", None, 0, now, "Paper", None, "Sell", None),

        # 1984
        ("1984", "George Orwell", "A dystopian masterpiece exploring the dangers of totalitarianism, surveillance, and repressive regimentation of individuals.", 10.99, "English", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("1984 (Español)", "George Orwell", "Una obra maestra distópica que advierte sobre los peligros del totalitarismo, la vigilancia extrema y el control del pensamiento.", 10.99, "Spanish", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("1984 (Русский)", "Джордж Оруэлл", "Знаменитый антиутопический роман о тоталитарном государстве, всеобщем контроле, Большом Брате и борьбе человека за свободу мысли.", 10.99, "Russian", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("1984 (Français)", "George Orwell", "Le roman d'anticipation dystopique le plus célèbre, décrivant une société totalitaire gouvernée par le personnage omnipotent de Big Brother.", 10.99, "French", "Fiction", None, 0, now, "Paper", None, "Sell", None),

        # To Kill a Mockingbird
        ("To Kill a Mockingbird", "Harper Lee", "Atticus Finch defends a Black man falsely accused of rape in a Southern town, exploring racial injustice and the destruction of innocence.", 13.99, "English", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Matar a un ruiseñor", "Harper Lee", "El abogado Atticus Finch defiende a un hombre negro acusado injustamente en una pequeña ciudad sureña de Estados Unidos.", 13.99, "Spanish", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Убить пересмешника", "Харпер Ли", "История о расовых предрассудках, справедливости и взрослении детей в американском городке глазами маленькой девочки Глазастик.", 13.99, "Russian", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Ne tirez pas sur l'oiseau moqueur", "Harper Lee", "Dans l'Alabama des années 1930, Atticus Finch, un avocat intègre, accepte de défendre un homme noir faussement accusé de viol.", 13.99, "French", "Fiction", None, 0, now, "Paper", None, "Sell", None),

        # The Odyssey
        ("The Odyssey", "Homer", "The epic journey of Odysseus as he struggles to return home to Ithaca after the Trojan War, facing monsters and the wrath of gods.", 12.50, "English", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("La Odisea", "Homero", "El gran poema épico griego que narra el viaje de regreso a casa de Odiseo tras la caída de Troya, lleno de aventuras extraordinarias.", 12.50, "Spanish", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Одиссея", "Гомер", "Величайшая эпическая поэма об опасном десятилетнем возвращении царя Итаки Одиссея домой после победы в Троянской войне.", 12.50, "Russian", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("L'Odyssée", "Homère", "Le grand chant épique narrant le retour tumultueux d'Ulysse vers son royaume d'Ithaque après la guerre de Troie.", 12.50, "French", "Fiction", None, 0, now, "Paper", None, "Sell", None),

        # Pride and Prejudice
        ("Pride and Prejudice", "Jane Austen", "The romantic clash between Elizabeth Bennet and Mr. Darcy, exploring class distinction, reputation, and the folly of quick judgments.", 11.50, "English", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Orgullo y prejuicio", "Jane Austen", "La comedia romántica clásica sobre Elizabeth Bennet y Fitzwilliam Darcy, que desafía las convenciones sociales de su época.", 11.50, "Spanish", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Гордость и предубеждение", "Джейн Остин", "История о непростых взаимоотношениях Элизабет Беннет и мистера Дарси, преодолевающих взаимную гордость и социальные предрассудки.", 11.50, "Russian", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Orgueil et Préjugés", "Jane Austen", "L'histoire d'amour complexe d'Elizabeth Bennet et de Mr Darcy dans la société rurale anglaise du XIXe siècle.", 11.50, "French", "Fiction", None, 0, now, "Paper", None, "Sell", None),

        # The Hobbit
        ("The Hobbit", "J.R.R. Tolkien", "Bilbo Baggins is swept into a quest to reclaim the Lonely Mountain from the dragon Smaug, discovering a magical ring along the way.", 14.50, "English", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("El Hobbit", "J.R.R. Tolkien", "Bilbo Bolsón es reclutado por el mago Gandalf y un grupo de enanos para recuperar el tesoro custodiado por el temible dragón Smaug.", 14.50, "Spanish", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Хоббит", "Дж. Р. Р. Толкин", "Увлекательное путешествие хоббита Бильбо Бэггинса и гномов к Одинокой горе, чтобы вернуть похищенные драконом Смаугом сокровища.", 14.50, "Russian", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Le Hobbit", "J.R.R. Tolkien", "Les aventures de Bilbo Bessac, entraîné malgré lui by Gandalf et une troupe de nains pour reprendre la Montagne Solitaire du dragon Smaug.", 14.50, "French", "Fiction", None, 0, now, "Paper", None, "Sell", None),

        # Hamlet
        ("Hamlet", "William Shakespeare", "Prince Hamlet is urged by his father's ghost to avenge his murder, leading to tragedy, madness, and deep philosophical contemplations.", 8.99, "English", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Hamlet (Español)", "William Shakespeare", "El príncipe Hamlet de Dinamarca busca vengar la muerte de su padre, asesinado por su tío Claudio, cayendo en la locura y la tragedia.", 8.99, "Spanish", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Гамлет", "Уильям Шекспир", "Трагедия принца датского Гамлета, пытающегося отомстить за убийство своего отца и размышляющего о смысле жизни и смерти.", 8.99, "Russian", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Hamlet (Français)", "William Shakespeare", "Le prince de Danemark, hanté par le spectre de son père, découvre qu'il a été assassiné par son oncle Claudius et jure de le venger.", 8.99, "French", "Fiction", None, 0, now, "Paper", None, "Sell", None),

        # The Catcher in the Rye
        ("The Catcher in the Rye", "J.D. Salinger", "Holden Caulfield wanders through New York City after being expelled from prep school, exploring themes of alienation, identity, and loss.", 10.50, "English", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("El guardián entre el centeno", "J.D. Salinger", "La icónica novela sobre el adolescent alienado Holden Caulfield en la ciudad de Nueva York tras ser expulsado de su escuela.", 10.50, "Spanish", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Над пропастью во ржи", "Дж. Д. Сэлинджер", "История подростка Холдена Колфилда, блуждающего по Нью-Йорку после исключения из школы и выражающего бунт против фальши взрослого мира.", 10.50, "Russian", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("L'Attrape-cœurs", "J.D. Salinger", "Le récit à la première personne de la dérive de Holden Caulfield, un adolescent rebelle, dans New York après son renvoi du lycée.", 10.50, "French", "Fiction", None, 0, now, "Paper", None, "Sell", None),

         # War and Peace
        ("War and Peace", "Leo Tolstoy", "A monumental chronicle of Russian society during the Napoleonic Wars, interwoven with deep philosophical inquiries into history and human fate.", 19.99, "English", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Guerra y paz", "León Tolstói", "La colosal obra maestra que detalla la invasión napoleónica de Rusia a través de los ojos de varias familias aristocráticas.", 19.99, "Spanish", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Война и мир", "Лев Толстой", "Эпический роман-эпопея, воссоздающий жизнь русского общества в эпоху войн против Наполеона и раскрывающий судьбы сотен персонажей.", 19.99, "Russian", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Guerre et Paix", "Léon Tolstoï", "Une fresque magistrale décrivant l'histoire de la Russie et de son aristocratie pendant l'invasion napoléonienne.", 19.99, "French", "Fiction", None, 0, now, "Paper", None, "Sell", None),
       
         # The Divine Comedy
        ("The Divine Comedy", "Dante Alighieri", "An epic narrative poem tracing Dante's journey through Inferno, Purgatorio, and Paradiso, representing the soul's journey towards God.", 13.99, "English", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("La Divina Comedia", "Dante Alighieri", "El poema monumental que describe el viaje de Dante a través del Infierno, el Purgatorio y el Paraíso.", 13.99, "Spanish", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Божественная комедия", "Данте Алигьери", "Величайшая философская поэма, в которой Данте совершает путешествие сквозь Ад, Чистилище и Рай к познанию божественной любви.", 13.99, "Russian", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("La Divine Comédie", "Dante Alighieri", "Le poème allégorique majeur narrant le voyage spirituel de Dante à travers l'Enfer, le Purgatoire et le Paradis.", 13.99, "French", "Fiction", None, 0, now, "Paper", None, "Sell", None),
       
         # The Stranger
        ("The Stranger", "Albert Camus", "An absurdist masterpiece detailing Meursault's emotional detachment, his crime on an Algerian beach, and his subsequent trial.", 9.50, "English", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("El extranjero", "Albert Camus", "La influyente novela existencialista sobre Meursault, un hombre indiferente ante las convenciones sociales y morales de la vida.", 9.50, "Spanish", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("Посторонний", "Альберт Камю", "Философский роман о французе Мерсо, живущем в Алжире и обвиняемом обществом скорее в нежелании лгать и плакать на похоронах матери, чем в убийстве.", 9.50, "Russian", "Fiction", None, 0, now, "Paper", None, "Sell", None),
        ("L'Étranger", "Albert Camus", "Un roman incontournable décrivant l'indifférence de Meursault face au monde, de la mort de sa mère jusqu'à sa propre condamnation à mort.", 9.50, "French", "Fiction", None, 0, now, "Paper", None, "Sell", None),
       
         # Non-Fiction/Sci-Fi/Self-Help to keep complete test compatibility and diversity
        ("Dune", "Frank Herbert", "Set on the desert planet Arrakis, Dune is the story of the boy Paul Atreides, who would become the mysterious man known as Muad'Dib.", 15.45, "English", "Sci-Fi", None, 0, now, "Paper", None, "Sell", None),
        ("Atomic Habits", "James Clear", "An easy and proven way to build good habits and break bad ones, drawing on ideas from biology, psychology, and neuroscience.", 18.99, "English", "Self-Help", None, 0, now, "Paper", None, "Sell", None),
        ("Clean Code", "Robert C. Martin", "Even bad code can function. But if code isn't clean, it can bring a development organization to its knees. This digital guide helps programmers write clean code.", 24.99, "English", "Fiction", None, 0, now, "PDF", "clean_code_ebook.pdf", "Sell", None),
        ("Design Patterns: Elements of Reusable Object-Oriented Software", "Erich Gamma", "A master-class in design patterns that provides solutions to common software development problems. Essential reading for engineers.", 29.50, "English", "Fiction", None, 0, now, "EPUB", "design_patterns.epub", "Sell", None),
        ("Le Petit Prince (E-Book)", "Antoine de Saint-Exupéry", "Une édition numérique du conte philosophique sur l'amitié, l'amour et le sens de la vie.", 6.99, "French", "Fiction", None, 0, now, "PDF", "le_petit_prince.pdf", "Sell", None),
        ("Ficciones", "Jorge Luis Borges", "Una colección de laberintos, acertijos y fantasías filosóficas que desafían la naturaleza misma de la realidad y del tiempo.", 13.50, "Spanish", "Mystery", None, 0, now, "Paper", None, "Sell", None),
        ("Мастер и Маргарита", "Михаил Булгаков", "Фантастический роман о визите дьявола в советскую Москву, переплетённый с историей Понтия Пилата.", 14.50, "Russian", "Fantasy", None, 0, now, "Paper", None, "Sell", None)
    ]
    
    for seed in seeds:
        cursor.execute("SELECT COUNT(*) FROM books WHERE title = %s AND language = %s;", (seed[0], seed[4]))
        exists = cursor.fetchone()[0]
        if exists == 0:
            cursor.execute(
                """INSERT INTO books (title, author, description, price, language, genre, owner_id, is_sold, date_added, format, download_url, listing_type, wanted_book)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                seed
            )
            
    conn.commit()
    cursor.close()

def add_user(username, password, email, address):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, email, address, points) VALUES (%s, %s, %s, %s, 0);",
            (username, password, email, address)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    except mysql.connector.Error:
        return None
    finally:
        cursor.close()
        conn.close()

def verify_user(username, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM users WHERE username = %s AND password = %s;",
        (username, password)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s;", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def update_user_profile(user_id, email, address, balance):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET email = %s, address = %s, balance = %s WHERE id = %s;",
        (email, address, balance, user_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def redeem_points(user_id, points_to_redeem):
    """Погашение бонусных баллов за баланс магазина (100 баллов = $1.00)"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT points, balance FROM users WHERE id = %s;", (user_id,))
        row = cursor.fetchone()
        if not row:
            raise Exception("User not found.")
            
        current_points = row['points']
        current_balance = row['balance']
        
        if current_points < points_to_redeem:
            raise Exception(f"Insufficient points. You only have {current_points} points.")
            
        cash_bonus = points_to_redeem / 100.0
        new_points = current_points - points_to_redeem
        new_balance = current_balance + cash_bonus
        
        cursor.execute(
            "UPDATE users SET points = %s, balance = %s WHERE id = %s;",
            (new_points, new_balance, user_id)
        )
        conn.commit()
        return cash_bonus
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def add_book(title, author, description, price, language, genre, owner_id, format='Paper', download_url=None, listing_type='Sell', wanted_book=None):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """INSERT INTO books (title, author, description, price, language, genre, owner_id, date_added, format, download_url, listing_type, wanted_book)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
        (title, author, description, price, language, genre, owner_id, now, format, download_url, listing_type, wanted_book)
    )
    conn.commit()
    book_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return book_id

def get_available_books(search_query=None, language=None, genre=None, max_price=None, exclude_user_id=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = "SELECT * FROM books WHERE is_sold = 0"
    params = []
    
    if exclude_user_id is not None:
        query += " AND (owner_id IS NULL OR owner_id != %s)"
        params.append(exclude_user_id)
        
    if search_query:
        query += " AND (title LIKE %s OR author LIKE %s OR description LIKE %s)"
        term = f"%{search_query}%"
        params.extend([term, term, term])
        
    if language:
        query += " AND language = %s"
        params.append(language)
        
    if genre:
        query += " AND genre = %s"
        params.append(genre)
        
    if max_price is not None:
        query += " AND price <= %s"
        params.append(max_price)
        
    query += " ORDER BY date_added DESC;"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_unique_languages():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT language FROM books ORDER BY language;")
    languages = [r[0] for r in cursor.fetchall()]
    cursor.close()
    conn.close()
    return languages

def get_unique_genres():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT genre FROM books ORDER BY genre;")
    genres = [r[0] for r in cursor.fetchall()]
    cursor.close()
    conn.close()
    return genres

def get_book_by_id(book_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books WHERE id = %s;", (book_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def buy_book(buyer_id, book_id, address):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM books WHERE id = %s AND is_sold = 0;", (book_id,))
        book = cursor.fetchone()
        if not book:
            raise Exception("Book is no longer available.")
            
        cursor.execute("SELECT * FROM users WHERE id = %s;", (buyer_id,))
        buyer = cursor.fetchone()
        if not buyer:
            raise Exception("Buyer not found.")
            
        price = book['price']
        if buyer['balance'] < price:
            raise Exception("Insufficient funds. Please top up your balance in your profile.")
            
        new_buyer_balance = buyer['balance'] - price
        points_earned = int(price * 12.5)  # 1 USD = 12.5 баллов (1000 UZS = 1 балл)
        new_points = buyer['points'] + points_earned
        
        cursor.execute(
            "UPDATE users SET balance = %s, points = %s WHERE id = %s;",
            (new_buyer_balance, new_points, buyer_id)
        )
        
        seller_id = book['owner_id']
        if seller_id:
            cursor.execute("SELECT balance FROM users WHERE id = %s;", (seller_id,))
            seller = cursor.fetchone()
            if seller:
                new_seller_balance = seller['balance'] + price
                cursor.execute("UPDATE users SET balance = %s WHERE id = %s;", (new_seller_balance, seller_id))
                
        if seller_id is not None:
            cursor.execute("UPDATE books SET is_sold = 1 WHERE id = %s;", (book_id,))
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        is_digital = book['format'] in ('PDF', 'EPUB')
        
        status = 'Delivered' if is_digital else 'Pending'
        tracking_info = f"{now} - Order placed.\n"
        if is_digital:
            tracking_info += f"{now} - E-Book delivered digitally for download.\n"
        else:
            tracking_info += f"{now} - Preparing for shipment.\n"
            
        cursor.execute(
            "INSERT INTO transactions (buyer_id, seller_id, book_id, price, status, delivery_address, date, tracking_info) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);",
            (buyer_id, seller_id, book_id, price, status, address, now, tracking_info)
        )
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def get_user_purchases(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.*, b.title, b.author, b.language, b.genre, b.format, b.download_url, u.username as seller_name
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        LEFT JOIN users u ON t.seller_id = u.id
        WHERE t.buyer_id = %s
        ORDER BY t.date DESC;
    """, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_user_listings(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books WHERE owner_id = %s ORDER BY date_added DESC;", (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_user_sales(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.*, b.title, b.author, b.language, b.genre, u.username as buyer_name
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        JOIN users u ON t.buyer_id = u.id
        WHERE t.seller_id = %s
        ORDER BY t.date DESC;
    """, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def update_transaction_status(transaction_id, status, tracking_note):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("SELECT tracking_info FROM transactions WHERE id = %s;", (transaction_id,))
    row = cursor.fetchone()
    if row:
        current_tracking = row['tracking_info']
        new_tracking = current_tracking + f"{now} - {tracking_note}\n"
        cursor.execute(
            "UPDATE transactions SET status = %s, tracking_info = %s WHERE id = %s;",
            (status, new_tracking, transaction_id)
        )
        conn.commit()
    cursor.close()
    conn.close()

def add_review(book_id, user_id, rating, comment):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute(
            "INSERT INTO reviews (book_id, user_id, rating, comment, date) VALUES (%s, %s, %s, %s, %s);",
            (book_id, user_id, rating, comment, now)
        )
        conn.commit()
        return True
    except mysql.connector.Error:
        return False
    finally:
        cursor.close()
        conn.close()

def get_book_reviews(book_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.*, u.username 
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.book_id = %s
        ORDER BY r.date DESC;
    """, (book_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_book_rating_summary(book_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT AVG(rating) as avg_rating, COUNT(rating) as rating_count FROM reviews WHERE book_id = %s GROUP BY book_id;", (book_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return dict(row) if row else {'avg_rating': None, 'rating_count': 0}

def toggle_wishlist(user_id, book_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM wishlist WHERE user_id = %s AND book_id = %s;", (user_id, book_id))
    row = cursor.fetchone()
    
    added = False
    if row:
        cursor.execute("DELETE FROM wishlist WHERE user_id = %s AND book_id = %s;", (user_id, book_id))
    else:
        cursor.execute("INSERT INTO wishlist (user_id, book_id) VALUES (%s, %s);", (user_id, book_id))
        added = True
        
    conn.commit()
    cursor.close()
    conn.close()
    return added

def is_in_wishlist(user_id, book_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM wishlist WHERE user_id = %s AND book_id = %s;", (user_id, book_id))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row is not None

def get_user_wishlist(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.* 
        FROM wishlist w
        JOIN books b ON w.book_id = b.id
        WHERE w.user_id = %s AND b.is_sold = 0
        ORDER BY b.date_added DESC;
    """, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# Messaging / Chat Operations
def send_message(sender_id, receiver_id, book_id, message):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO messages (sender_id, receiver_id, book_id, message, timestamp) VALUES (%s, %s, %s, %s, %s);",
        (sender_id, receiver_id, book_id, message, now)
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_chat_history(user1_id, user2_id, book_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT m.*, u_send.username as sender_name, u_rec.username as receiver_name
        FROM messages m
        JOIN users u_send ON m.sender_id = u_send.id
        JOIN users u_rec ON m.receiver_id = u_rec.id
        WHERE m.book_id = %s 
          AND ((m.sender_id = %s AND m.receiver_id = %s) OR (m.sender_id = %s AND m.receiver_id = %s))
        ORDER BY m.timestamp ASC;
    """, (book_id, user1_id, user2_id, user2_id, user1_id))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_user_chats(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT DISTINCT 
            m.book_id, 
            b.title as book_title,
            CASE WHEN m.sender_id = %s THEN m.receiver_id ELSE m.sender_id END as other_user_id,
            u.username as other_username
        FROM messages m
        JOIN books b ON m.book_id = b.id
        JOIN users u ON u.id = (CASE WHEN m.sender_id = %s THEN m.receiver_id ELSE m.sender_id END)
        WHERE (m.sender_id = %s OR m.receiver_id = %s) AND u.is_admin = 0;
    """, (user_id, user_id, user_id, user_id))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# Book Exchange operations
def propose_exchange(proposer_id, receiver_id, proposer_book_id, receiver_book_id):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        SELECT id FROM exchanges 
        WHERE proposer_id = %s AND receiver_id = %s AND proposer_book_id = %s AND receiver_book_id = %s AND status = 'Pending';
    """, (proposer_id, receiver_id, proposer_book_id, receiver_book_id))
    
    if cursor.fetchone():
        cursor.close()
        conn.close()
        raise Exception("You have already proposed this exchange.")
        
    cursor.execute(
        "INSERT INTO exchanges (proposer_id, receiver_id, proposer_book_id, receiver_book_id, date) VALUES (%s, %s, %s, %s, %s);",
        (proposer_id, receiver_id, proposer_book_id, receiver_book_id, now)
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_received_exchange_proposals(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT e.*, 
               u.username as proposer_name,
               b_prop.title as proposer_book_title, b_prop.author as proposer_book_author,
               b_rec.title as receiver_book_title
        FROM exchanges e
        JOIN users u ON e.proposer_id = u.id
        JOIN books b_prop ON e.proposer_book_id = b_prop.id
        JOIN books b_rec ON e.receiver_book_id = b_rec.id
        WHERE e.receiver_id = %s AND e.status = 'Pending'
        ORDER BY e.date DESC;
    """, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_sent_exchange_proposals(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT e.*, 
               u.username as receiver_name,
               b_prop.title as proposer_book_title,
               b_rec.title as receiver_book_title, b_rec.author as receiver_book_author
        FROM exchanges e
        JOIN users u ON e.receiver_id = u.id
        JOIN books b_prop ON e.proposer_book_id = b_prop.id
        JOIN books b_rec ON e.receiver_book_id = b_rec.id
        WHERE e.proposer_id = %s
        ORDER BY e.date DESC;
    """, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def respond_to_exchange(exchange_id, status):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM exchanges WHERE id = %s AND status = 'Pending';", (exchange_id,))
        exchange = cursor.fetchone()
        if not exchange:
            raise Exception("Proposal is no longer pending.")
            
        proposer_id = exchange['proposer_id']
        receiver_id = exchange['receiver_id']
        prop_book_id = exchange['proposer_book_id']
        rec_book_id = exchange['receiver_book_id']
        
        if status == 'Rejected':
            cursor.execute("UPDATE exchanges SET status = 'Rejected' WHERE id = %s;", (exchange_id,))
            conn.commit()
            return
            
        cursor.execute("SELECT is_sold, title FROM books WHERE id = %s;", (prop_book_id,))
        b1 = cursor.fetchone()
        cursor.execute("SELECT is_sold, title FROM books WHERE id = %s;", (rec_book_id,))
        b2 = cursor.fetchone()
        
        if not b1 or b1['is_sold'] or not b2 or b2['is_sold']:
            raise Exception("One or both books involved in this exchange are no longer available.")
            
        cursor.execute("UPDATE books SET owner_id = %s, is_sold = 1 WHERE id = %s;", (receiver_id, prop_book_id))
        cursor.execute("UPDATE books SET owner_id = %s, is_sold = 1 WHERE id = %s;", (proposer_id, rec_book_id))
        
        cursor.execute("UPDATE exchanges SET status = 'Accepted' WHERE id = %s;", (exchange_id,))
        
        cursor.execute("""
            UPDATE exchanges 
            SET status = 'Rejected' 
            WHERE status = 'Pending' 
              AND (proposer_book_id = %s OR receiver_book_id = %s OR proposer_book_id = %s OR receiver_book_id = %s);
        """, (prop_book_id, prop_book_id, rec_book_id, rec_book_id))
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        tx_info1 = f"{now} - Exchange agreed. Owners swapped.\n"
        cursor.execute(
            "INSERT INTO transactions (buyer_id, seller_id, book_id, price, status, delivery_address, date, tracking_info) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);",
            (receiver_id, proposer_id, prop_book_id, 0.0, 'Delivered', 'Exchange Swap', now, tx_info1)
        )
        
        tx_info2 = f"{now} - Exchange agreed. Owners swapped.\n"
        cursor.execute(
            "INSERT INTO transactions (buyer_id, seller_id, book_id, price, status, delivery_address, date, tracking_info) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);",
            (proposer_id, receiver_id, rec_book_id, 0.0, 'Delivered', 'Exchange Swap', now, tx_info2)
        )
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def admin_get_all_books():
    """Возвращает все книги (включая проданные) для панели администратора."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.*, u.username as owner_name 
        FROM books b
        LEFT JOIN users u ON b.owner_id = u.id
        ORDER BY b.date_added DESC;
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def admin_delete_book(book_id):
    """Удаляет книгу из каталога."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM books WHERE id = %s;", (book_id,))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        conn.rollback()
        raise Exception("Cannot delete this book because it is referenced by past transactions.")
    finally:
        cursor.close()
        conn.close()

def admin_update_book(book_id, title, author, description, price, language, genre, format, download_url, listing_type, wanted_book):
    """Обновляет все метаданные книги."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE books 
            SET title = %s, author = %s, description = %s, price = %s, language = %s, 
                genre = %s, format = %s, download_url = %s, listing_type = %s, wanted_book = %s
            WHERE id = %s;
        """, (title, author, description, price, language, genre, format, download_url, listing_type, wanted_book, book_id))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def admin_get_all_users():
    """Возвращает список всех зарегистрированных пользователей."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users ORDER BY id ASC;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def admin_update_user_balance_points(user_id, balance, points):
    """Обновляет баланс и бонусные очки пользователя."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET balance = %s, points = %s WHERE id = %s;", (balance, points, user_id))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def admin_toggle_user_admin(user_id):
    """Переключает статус администратора для пользователя (продвижение/демоут)."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT is_admin, username FROM users WHERE id = %s;", (user_id,))
        row = cursor.fetchone()
        if not row:
            raise Exception("User not found.")
        if row['username'] == 'admin':
            raise Exception("Cannot demote the default master admin account.")
            
        new_val = 0 if row['is_admin'] == 1 else 1
        cursor.execute("UPDATE users SET is_admin = %s WHERE id = %s;", (new_val, user_id))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def admin_delete_user(user_id):
    """Удаляет пользователя из системы."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT username FROM users WHERE id = %s;", (user_id,))
        row = cursor.fetchone()
        if not row:
            raise Exception("User not found.")
        if row['username'] == 'admin':
            raise Exception("Cannot delete the default master admin account.")
            
        cursor.execute("DELETE FROM users WHERE id = %s;", (user_id,))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        conn.rollback()
        raise Exception("Cannot delete user because they have active listings, purchases, or bids. Clean their records first.")
    finally:
        cursor.close()
        conn.close()

def admin_get_all_transactions():
    """Возвращает список всех транзакций в системе."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.*, b.title as book_title, u_buy.username as buyer_name, u_sell.username as seller_name
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        JOIN users u_buy ON t.buyer_id = u_buy.id
        LEFT JOIN users u_sell ON t.seller_id = u_sell.id
        ORDER BY t.date DESC;
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def admin_get_all_reviews():
    """Возвращает все отзывы во всей системе для модерации."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.*, b.title as book_title, u.username as reviewer_name
        FROM reviews r
        JOIN books b ON r.book_id = b.id
        JOIN users u ON r.user_id = u.id
        ORDER BY r.date DESC;
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def admin_delete_review(review_id):
    """Удаляет отзыв из системы."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM reviews WHERE id = %s;", (review_id,))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()