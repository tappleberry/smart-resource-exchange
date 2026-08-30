import database


# ==================================================
# Configuration
# ==================================================

DEMO_PREFIX = "[ML DEMO]"

# Each category gets:
# searches, views, favorites, listings
#
# Values are kept within the rough range of the
# current demand training dataset.

CATEGORY_ACTIVITY = {
    "Electronics": {
        "searches": 45,
        "views": 70,
        "favorites": 12,
        "listings": 3,
    },

    "Books": {
        "searches": 35,
        "views": 60,
        "favorites": 10,
        "listings": 3,
    },

    "Cycles": {
        "searches": 18,
        "views": 32,
        "favorites": 5,
        "listings": 3,
    },

    "Hostel Essentials": {
        "searches": 38,
        "views": 65,
        "favorites": 11,
        "listings": 3,
    },

    "Lab Equipment": {
        "searches": 24,
        "views": 42,
        "favorites": 7,
        "listings": 3,
    },

    "Furniture": {
        "searches": 15,
        "views": 28,
        "favorites": 4,
        "listings": 3,
    },

    "Clothing": {
        "searches": 30,
        "views": 50,
        "favorites": 9,
        "listings": 3,
    },

    "Sports Equipment": {
        "searches": 26,
        "views": 44,
        "favorites": 8,
        "listings": 3,
    },
}


# ==================================================
# Demo Item Templates
# ==================================================

ITEM_TEMPLATES = {
    "Electronics": [
        ("[ML DEMO] Scientific Calculator", 800),
        ("[ML DEMO] USB Keyboard", 450),
        ("[ML DEMO] Bluetooth Speaker", 900),
    ],

    "Books": [
        ("[ML DEMO] Data Structures Book", 350),
        ("[ML DEMO] Engineering Mathematics Book", 300),
        ("[ML DEMO] Operating Systems Book", 400),
    ],

    "Cycles": [
        ("[ML DEMO] Campus Bicycle", 4500),
        ("[ML DEMO] Mountain Bicycle", 6000),
        ("[ML DEMO] City Bicycle", 5000),
    ],

    "Hostel Essentials": [
        ("[ML DEMO] Study Lamp", 500),
        ("[ML DEMO] Electric Kettle", 900),
        ("[ML DEMO] Storage Box", 350),
    ],

    "Lab Equipment": [
        ("[ML DEMO] Digital Multimeter", 700),
        ("[ML DEMO] Breadboard Kit", 450),
        ("[ML DEMO] Soldering Kit", 850),
    ],

    "Furniture": [
        ("[ML DEMO] Study Chair", 1200),
        ("[ML DEMO] Study Table", 2500),
        ("[ML DEMO] Bookshelf", 1800),
    ],

    "Clothing": [
        ("[ML DEMO] Winter Jacket", 1200),
        ("[ML DEMO] College Hoodie", 900),
        ("[ML DEMO] Sports T-Shirt", 500),
    ],

    "Sports Equipment": [
        ("[ML DEMO] Cricket Bat", 1800),
        ("[ML DEMO] Football", 700),
        ("[ML DEMO] Badminton Racket", 1100),
    ],
}


# ==================================================
# Get Seed User
# ==================================================

def get_seed_user_id():
    """
    Use user ID 2 when available.
    Otherwise use the first available user.
    """

    users = database.get_users()

    if not users:
        raise RuntimeError(
            "No users found. Create a user first."
        )

    for user in users:

        if user["id"] == 2:
            return 2

    return users[0]["id"]


# ==================================================
# Create Demo Items
# ==================================================

def create_demo_items(user_id):
    """
    Create three demo marketplace items per category.

    Existing [ML DEMO] items are reused to avoid
    creating duplicates on repeated runs.
    """

    connection = database.get_connection()

    try:

        demo_items = {}

        for category, templates in ITEM_TEMPLATES.items():

            existing_rows = connection.execute(
                """
                SELECT id, title
                FROM items
                WHERE category = ?
                  AND title LIKE ?
                  AND status = 'available'
                ORDER BY id
                """,
                (
                    category,
                    f"{DEMO_PREFIX}%"
                )
            ).fetchall()

            item_ids = [
                row["id"]
                for row in existing_rows
            ]

            # --------------------------------------
            # Create missing demo items
            # --------------------------------------

            while len(item_ids) < 3:

                index = len(item_ids)

                title, price = templates[index]

                cursor = connection.execute(
                    """
                    INSERT INTO items
                    (
                        seller_id,
                        title,
                        description,
                        category,
                        listing_type,
                        price,
                        image_path,
                        condition,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        title,
                        f"Demo marketplace item for ML "
                        f"demand testing - {category}.",
                        category,
                        "sale",
                        price,
                        None,
                        "Good",
                        "available"
                    )
                )

                item_ids.append(
                    cursor.lastrowid
                )

                connection.commit()

            demo_items[category] = item_ids[:3]

        return demo_items

    finally:

        connection.close()


# ==================================================
# Seed Search Activity
# ==================================================

def seed_searches(
    user_id,
    category,
    count
):
    """
    Add synthetic search records for a category.

    Existing demo searches are detected through the
    dedicated [ML DEMO] query prefix.
    """

    connection = database.get_connection()

    try:

        existing = connection.execute(
            """
            SELECT COUNT(*)
            FROM searches
            WHERE user_id = ?
              AND category = ?
              AND query LIKE ?
            """,
            (
                user_id,
                category,
                f"{DEMO_PREFIX}%"
            )
        ).fetchone()[0]

        remaining = max(
            0,
            count - existing
        )

        for index in range(
            remaining
        ):

            connection.execute(
                """
                INSERT INTO searches
                (
                    user_id,
                    query,
                    category
                )
                VALUES (?, ?, ?)
                """,
                (
                    user_id,
                    f"{DEMO_PREFIX} {category} search {index + 1}",
                    category
                )
            )

        connection.commit()

    finally:

        connection.close()


# ==================================================
# Seed Item Interactions
# ==================================================

def seed_interactions(
    user_id,
    item_ids,
    views,
    favorites
):
    """
    Add synthetic view/favorite activity.

    Existing demo interactions are counted first,
    so repeated execution does not keep increasing
    the totals.
    """

    connection = database.get_connection()

    try:

        # ------------------------------------------
        # Current demo interaction counts
        # ------------------------------------------

        placeholders = ",".join(
            "?"
            for _ in item_ids
        )

        existing_views = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM interactions
            WHERE user_id = ?
              AND action = 'view'
              AND item_id IN ({placeholders})
            """,
            (
                user_id,
                *item_ids
            )
        ).fetchone()[0]

        existing_favorites = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM interactions
            WHERE user_id = ?
              AND action = 'favorite'
              AND item_id IN ({placeholders})
            """,
            (
                user_id,
                *item_ids
            )
        ).fetchone()[0]

        remaining_views = max(
            0,
            views - existing_views
        )

        remaining_favorites = max(
            0,
            favorites - existing_favorites
        )

        # ------------------------------------------
        # Add views
        # ------------------------------------------

        for index in range(
            remaining_views
        ):

            item_id = item_ids[
                index % len(item_ids)
            ]

            connection.execute(
                """
                INSERT INTO interactions
                (
                    user_id,
                    item_id,
                    action
                )
                VALUES (?, ?, ?)
                """,
                (
                    user_id,
                    item_id,
                    "view"
                )
            )

        # ------------------------------------------
        # Add favorites
        # ------------------------------------------

        for index in range(
            remaining_favorites
        ):

            item_id = item_ids[
                index % len(item_ids)
            ]

            connection.execute(
                """
                INSERT INTO interactions
                (
                    user_id,
                    item_id,
                    action
                )
                VALUES (?, ?, ?)
                """,
                (
                    user_id,
                    item_id,
                    "favorite"
                )
            )

        connection.commit()

    finally:

        connection.close()


# ==================================================
# Main
# ==================================================

def main():

    user_id = get_seed_user_id()

    print(
        "Using seed user:",
        user_id
    )

    # ----------------------------------------------
    # Create demo listings
    # ----------------------------------------------

    demo_items = create_demo_items(
        user_id
    )

    # ----------------------------------------------
    # Seed activity category-wise
    # ----------------------------------------------

    for category, activity in CATEGORY_ACTIVITY.items():

        seed_searches(
            user_id=user_id,
            category=category,
            count=activity["searches"]
        )

        seed_interactions(
            user_id=user_id,
            item_ids=demo_items[category],
            views=activity["views"],
            favorites=activity["favorites"]
        )

        print(
            f"{category}: "
            f"searches={activity['searches']}, "
            f"views={activity['views']}, "
            f"favorites={activity['favorites']}, "
            f"listings={activity['listings']}"
        )

    print(
        "\nSynthetic ML demand activity seeded successfully!"
    )


if __name__ == "__main__":
    main()