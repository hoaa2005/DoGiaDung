import sqlite3
import os

# ==============================
# ĐƯỜNG DẪN DATABASE (QUAN TRỌNG)
# ==============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "database.db")


# ==============================
# KẾT NỐI DB
# ==============================
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ==============================
# LẤY USER THEO EMAIL
# ==============================
def get_user_by_email(email):
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM nguoi_dung WHERE email = ?",
        (email,)
    ).fetchone()
    conn.close()
    return user


# ==============================
# LẤY USER THEO USERNAME
# ==============================
def get_user_by_username(tenDangNhap):
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM nguoi_dung WHERE tenDangNhap = ?",
        (tenDangNhap,)
    ).fetchone()
    conn.close()
    return user


# ==============================
# TẠO USER
# ==============================
def create_user(tenDangNhap, matKhau, hoTen, email, soDienThoai):
    conn = get_connection()
    conn.execute("""
        INSERT INTO nguoi_dung
        (tenDangNhap, matKhau, hoTen, email, soDienThoai, vaiTro, trangThai, ngayTao)
        VALUES (?, ?, ?, ?, ?, 3, 1, datetime('now'))
    """, (tenDangNhap, matKhau, hoTen, email, soDienThoai))
    conn.commit()
    conn.close()


# ==============================
# DEBUG (kiểm tra DB đang dùng)
# ==============================
def check_db_path():
    print("📂 DB PATH:", DB_PATH)