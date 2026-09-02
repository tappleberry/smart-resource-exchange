
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    regno INTEGER UNIQUE NOT NULL,

    email TEXT UNIQUE NOT NULL
        CHECK (email LIKE '%@mnnit.ac.in'),

    password_hash TEXT NOT NULL,

    department TEXT,

    year INTEGER
);

CREATE TABLE IF NOT EXISTS items(
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    seller_id INTEGER NOT NULL,

    title TEXT NOT NULL,
    description TEXT,

    category TEXT NOT NULL,
    listing_type TEXT NOT NULL,

    price REAL NOT NULL,

    image_path TEXT,

    condition TEXT,

    status TEXT DEFAULT 'available',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (seller_id) REFERENCES users(id) 
);

CREATE TABLE IF NOT EXISTS lost_found(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,

    report_type TEXT NOT NULL,

    title TEXT NOT NULL,
    description TEXT,

    category TEXT,

    image_path TEXT,

    location TEXT,

    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    status TEXT DEFAULT 'active',

    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS searches(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER ,

    query TEXT NOT NULL,

    category TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) 
);

CREATE TABLE IF NOT EXISTS interactions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER ,

    item_id INTEGER NOT NULL,

    action TEXT NOT NULL CHECK (action IN ('view','favourite')),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (item_id) REFERENCES items(id)
);
