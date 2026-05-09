import sqlite3
import os

# Lấy đường dẫn thư mục hiện tại (database/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Đường dẫn đúng
db_path = os.path.join(BASE_DIR, "database.db")
sql_path = os.path.join(BASE_DIR, "init.sql")

def init_db():
    try:
        conn = sqlite3.connect(db_path)

        with open(sql_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())

        conn.commit()
        conn.close()

        print("✅ Tạo database thành công!")

    except Exception as e:
        print("❌ Lỗi khi tạo DB:", e)


if __name__ == "__main__":
    init_db()