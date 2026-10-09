import sqlite3

DATABASE = "rfid_system.db"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

cards = [
    ("825399598103", "Sharvin", "ACTIVE"),
    ("51239766798", "Test Card", "INACTIVE")
]

for uid, name, status in cards:
    cursor.execute("""
        INSERT OR IGNORE INTO registered_cards (uid, name, status)
        VALUES (?, ?, ?)
    """, (uid, name, status))

conn.commit()
conn.close()

print("RFID cards added successfully.")
