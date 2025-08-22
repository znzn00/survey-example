CREATE TABLE IF NOT EXISTS USER (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER,
    role INTEGER NOT NULL,
    name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO USER(role, name, username, password)
VALUES (
        0,
        'System Admin',
        'sysadmin',
        '48a365b4ce1e322a55ae9017f3daf0c0'
    )