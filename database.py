import sqlite3

DATABASE_NAME = "database/campus.db"

#=================  CONNECTION  =============================
def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def initialize_database():
    connection = get_connection()
    try:

        with open("database/schema.sql" , "r") as file:
            schema = file.read()

        connection.executescript(schema)
        connection.commit()
    finally:
        connection.close()


#===================    USERS   ==============================
def create_user(name , regno , email, password_hash , department , year):
    connection = get_connection()
    try:

        cursor = connection.execute(
            """
            INSERT INTO users(name , regno , email , password_hash ,department, year)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name , regno, email ,password_hash, department ,year)
        )

        connection.commit()

        user_id = cursor.lastrowid
        return user_id
    
    except sqlite3.Error:
        connection.rollback()
        raise
    finally:
        connection.close()

def get_users():
    connection = get_connection()
    try:

        cursor = connection.execute(
            "SELECT * FROM users"
        )

        users = cursor.fetchall()
        return users

    finally:
        connection.close()

#===================    MARKETPLACE    ========================
def create_item(seller_id ,title ,description ,category ,listing_type ,
                price , image_path = None , condition = None):

    connection = get_connection()
    try:

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
        return item_id

    except sqlite3.Error:
        connection.rollback()
        raise
    finally:
        connection.close()

def get_items():
    connection = get_connection()
    try:

        cursor = connection.execute(
            """
            SELECT * 
            FROM items 
            WHERE status = 'available'
            ORDER BY created_at DESC
            """
        )

        items = cursor.fetchall()
        return items
    
    finally:
        connection.close()

def get_item(item_id):
    connection = get_connection()
    try:

        cursor = connection.execute(
            """
            SELECT *
            FROM items
            WHERE id = ?
            """,
            (item_id,)
        )

        item = cursor.fetchone()
        return item

    finally:
        connection.close()

def get_item_with_seller(item_id):
    connection = get_connection()
    try:

        cursor = connection.execute(
            """
            SELECT 
                items.* ,
                users.name AS seller_name,
                users.regno AS seller_regno,
                users.department AS seller_department,
                users.email AS seller_email
            FROM items
            JOIN users
                ON items.seller_id = users.id
            WHERE items.id = ?
            """,
            (item_id,)
        )

        item = cursor.fetchone()
        return item

    finally:
        connection.close()


def search_items(
        query=None,
        category=None,
        listing_type=None,
        min_price=None,
        max_price=None,
        condition=None
):
    connection = get_connection()
    try:

        sql =   """
                SELECT * 
                FROM items
                WHERE status = 'available'
                """
        parameters = []

        if query:
            sql += """
                AND (
                    title LIKE ?
                    OR description LIKE ?
                    OR category LIKE ?
                    )
                
            """
            search_query = f"%{query}%"

            parameters.extend([
                search_query,
                search_query,
                search_query
            ])

        if category:
            sql += " AND category = ?"
            parameters.append(category)

        if listing_type:
            sql += " AND listing_type = ?"
            parameters.append(listing_type)

        if min_price is not None:
            sql += " AND price >= ?"
            parameters.append(min_price)

        if max_price is not None:
            sql += " AND price <= ?"
            parameters.append(max_price)

        if condition:
            sql += " AND condition = ?"
            parameters.append(condition)

        sql += "ORDER BY created_at DESC"

        cursor = connection.execute(sql ,parameters)

        items = cursor.fetchall()
        return items

    finally:
        connection.close()

def update_item_status(item_id, status):
    connection = get_connection()
    try:

        connection.execute(
            """
            UPDATE items
            SET status = ?
            WHERE id = ?
            """,
            (status, item_id)
        )

        connection.commit()
        
    except sqlite3.Error:
        connection.rollback()
        raise
    finally:
        connection.close()

def get_items_by_seller(seller_id):
    connection = get_connection()
    try:

        cursor = connection.execute(
            """
            SELECT *
            FROM items
            WHERE seller_id = ?
            ORDER BY created_at DESC
            """,
            (seller_id,)
        )

        items = cursor.fetchall()
        return items

    finally:
        connection.close()

def get_categories():
    connection = get_connection()
    try:

        cursor = connection.execute(
                """
                SELECT DISTINCT category 
                FROM items
                WHERE status = 'available'
                ORDER BY LOWER(category)
                """
        )
        categories = cursor.fetchall()

        return categories

    finally:
        connection.close()


#================   LOST & FOUND ============================
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
    try:
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
        return report_id
    
    except sqlite3.Error:
        connection.rollback()
        raise
    finally:
        connection.close()

    

def get_lost_found_reports(report_type=None):
    connection = get_connection()
    try:

        sql = """
            SELECT
                lost_found.*,
                users.name AS user_name
            FROM lost_found
            JOIN users
                ON lost_found.user_id = users.id
            WHERE lost_found.status = 'active'
        """

        parameters = []

        if report_type:
            sql += " AND lost_found.report_type = ?"
            parameters.append(report_type)

        sql += " ORDER BY lost_found.reported_at DESC"

        cursor = connection.execute(sql, parameters)

        reports = cursor.fetchall()
        return reports
    
    finally:
        connection.close()

def update_lost_found_status(report_id , status):
    connection = get_connection()
    try:
        connection.execute(
            """
            UPDATE lost_found
            SET status = ?
            WHERE id = ?
            """,
            (status , report_id)
        )
        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        raise
    finally:
        connection.close()

def get_lost_found_report(report_id):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            SELECT
                lost_found.*,
                users.name AS user_name
            FROM lost_found
            JOIN users
                ON lost_found.user_id = users.id
            WHERE lost_found.id = ?
              AND lost_found.status = 'active'
            """,
            (report_id,)
        )

        report = cursor.fetchone()

        return report

    finally:
        connection.close()

#====================   ANALYTICS   ================================
def log_search(user_id, query, category=None):
    connection = get_connection()
    try:
        connection.execute(
            """
            INSERT INTO searches
            (user_id, query, category)
            VALUES (?, ?, ?)
            """,
            (user_id, query, category)
        )
        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        raise
    finally:
        connection.close()

def log_interaction(user_id, item_id, action):
    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO interactions
            (user_id, item_id, action)
            VALUES (?, ?, ?)
            """,
            (user_id, item_id, action)
        )
        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        raise
    finally:
        connection.close()


def get_search_demand():
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            SELECT
                query,
                COUNT(*) AS search_count
            FROM searches
            GROUP BY query
            ORDER BY search_count DESC
            """
        )
        results = cursor.fetchall()
        return results
    
    finally:
        connection.close()
    

def get_category_demand():

    connection = get_connection()
    try:
        cursor = connection.execute(
            """
            SELECT 
                category ,
                count(*) AS search_count
            FROM searches
            WHERE category is NOT NULL
            GROUP BY category
            ORDER BY search_count DESC
            """
        )
        results = cursor.fetchall()
        return results

    finally:
        connection.close()


def get_category_supply():
    connection = get_connection()
    try:

        cursor = connection.execute(
            """
            SELECT
                category,
                COUNT(*) AS available_items
            FROM items
            WHERE status = 'available'
            GROUP BY category
            ORDER BY available_items DESC
            """
        )

        results = cursor.fetchall()
        return results
        
    finally:
        connection.close()

def get_item_interaction_stats(item_id):
    connection = get_connection()
    try:
        cursor = connection.execute(
            """
            SELECT
                action,
                COUNT(*) AS count
            FROM interactions
            WHERE item_id = ?
            GROUP BY action
            """,
            (item_id,)
        )

        stats = cursor.fetchall()
        return stats

    finally:
        connection.close()

if __name__ == "__main__":
    initialize_database()
    print("Database Initialized Successfully.")