import sqlite3

DATABASE_NAME = "database/campus.db"

def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def initialize_database():
    connection = get_connection()

    with open("database/schema.sql" , "r") as file:
        schema = file.read()

    connection.executescript(schema)
    connection.close()

if __name__ == "__main__":
    initialize_database()
    print("Database Initialized Successfully.")

def create_user(name , regno , email, password_hash , department , year):
    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO users(name , regno , email , password_hash ,department, year)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (name , regno, email ,password_hash, department ,year)
    )

    connection.commit()

    user_id = cursor.lastrowid

    connection.close()
    return user_id

def get_users():
    connection = get_connection()

    cursor = connection.execute(
        "SELECT * FROM users"
    )

    users = cursor.fetchall()

    connection.close()
    return users


def create_item(seller_id ,title ,description ,category ,listing_type ,
                price , image_path = None , condition = None):

    connection = get_connection()

    cursor = connection.execute(

        """
        INSERT INTO items(

            seller_id,
            title,
            description,
            category,
            listing_type,
            price,
            image_path,
            condition
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,

        (
            seller_id,
            title,
            description,
            category,
            listing_type,
            price,
            image_path,
            condition
        )
    )

    connection.commit()

    item_id = cursor.lastrowid

    connection.close()
    return item_id

def get_items():
    connection = get_connection()

    cursor = connection.execute(
        """
        SELECT * 
        FROM items 
        WHERE status = 'available'
        ORDER BY created_at DESC
        """
    )

    items = cursor.fetchall()

    connection.close()
    return items


def search_items(query):
    connection = get_connection()

    cursor = connection.execute(
        """
        SELECT *
        FROM items
        WHERE status = 'available'
        AND (
            title LIKE ?
            OR description LIKE ?
            OR category LIKE ?
        )
        ORDER BY created_at DESC
        """,
        (
            f"%{query}%",
            f"%{query}%",
            f"%{query}%"
        )
    )

    items = cursor.fetchall()

    connection.close()
    return items

def create_lost_found_report(
    user_id,
    report_type,
    title,
    description,
    category,
    image_path,
    location
):
    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO lost_found
        (
            user_id,
            report_type,
            title,
            description,
            category,
            image_path,
            location
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            report_type,
            title,
            description,
            category,
            image_path,
            location
        )
    )

    connection.commit()

    report_id = cursor.lastrowid

    connection.close()
    return report_id

def log_search(user_id, query, category=None):
    connection = get_connection()

    connection.execute(
        """
        INSERT INTO searches
        (user_id, query, category)
        VALUES (?, ?, ?)
        """,
        (user_id, query, category)
    )

    connection.commit()
    connection.close()

def log_interaction(user_id, item_id, action):
    connection = get_connection()

    connection.execute(
        """
        INSERT INTO interactions
        (user_id, item_id, action)
        VALUES (?, ?, ?)
        """,
        (user_id, item_id, action)
    )

    connection.commit()
    connection.close()

