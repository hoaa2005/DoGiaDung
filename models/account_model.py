import sqlite3

DB_PATH = "database/database.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# =========================
# LẤY TOÀN BỘ USER
# =========================
def get_all_users():

    conn = get_connection()

    users = conn.execute("""
        SELECT * FROM nguoi_dung
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return users

# =========================
# XOÁ USER
# =========================
def delete_user(user_id):

    conn = get_connection()

    conn.execute("""
        DELETE FROM nguoi_dung
        WHERE id=?
    """, (user_id,))

    conn.commit()

    conn.close()

# =========================
# UPDATE USER
# =========================
def update_user(id, hoTen, email, vaiTro, trangThai):

    conn = get_connection()

    conn.execute("""
        UPDATE nguoi_dung
        SET
            hoTen=?,
            email=?,
            vaiTro=?,
            trangThai=?
        WHERE id=?
    """, (hoTen, email, vaiTro, trangThai, id))

    conn.commit()

    conn.close()