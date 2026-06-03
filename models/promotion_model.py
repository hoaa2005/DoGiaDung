import sqlite3
from datetime import datetime

DB_PATH = "database/database.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# 1. Lấy tất cả mã giảm giá hệ thống (Chưa hết hạn)
def get_all_system_vouchers():
    conn = get_db_connection()
    vouchers = conn.execute(
        "SELECT * FROM giam_gia WHERE ngayHetHan >= ?",
        (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),)
    ).fetchall()
    conn.close()
    return vouchers


# 2. Lấy danh sách mã người dùng đã lưu
def get_user_vouchers(user_id):
    conn = get_db_connection()
    vouchers = conn.execute("""
        SELECT g.* FROM giam_gia g
        JOIN voucher_nguoi_dung v ON g.id = v.giamGiaId
        WHERE v.nguoiDungId = ? AND v.trangThai = 1
    """, (user_id,)).fetchall()
    conn.close()
    return vouchers


# 3. Lưu mã giảm giá vào "Ví của tôi"
def save_voucher_to_user(user_id, giam_gia_id):
    conn = get_db_connection()
    try:
        # Kiểm tra xem đã lưu chưa để tránh trùng lặp
        exists = conn.execute(
            "SELECT id FROM voucher_nguoi_dung WHERE nguoiDungId = ? AND giamGiaId = ?",
            (user_id, giam_gia_id)
        ).fetchone()

        if not exists:
            conn.execute(
                "INSERT INTO voucher_nguoi_dung (nguoiDungId, giamGiaId) VALUES (?, ?)",
                (user_id, giam_gia_id)
            )
            conn.commit()
            return True, "Lưu mã thành công!"
        return False, "Bạn đã lưu mã này rồi."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


# 4. Kiểm tra mã hợp lệ khi thanh toán
def get_voucher_by_code(maCode):
    conn = get_db_connection()
    voucher = conn.execute("SELECT * FROM giam_gia WHERE maCode = ?", (maCode,)).fetchone()
    conn.close()
    return voucher