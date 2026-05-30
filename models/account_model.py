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

        SELECT *
        FROM nguoi_dung
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
        WHERE id = ?

    """, (user_id,))

    conn.commit()

    conn.close()


# =========================
# UPDATE USER
# =========================
def update_user(
    id,
    hoTen,
    email,
    tenDangNhap,
    vaiTro,
    trangThai,
    matKhau=None
):

    conn = get_connection()

    # CÓ ĐỔI PASSWORD
    if matKhau and matKhau.strip() != "":

        conn.execute("""

            UPDATE nguoi_dung
            SET
                hoTen = ?,
                email = ?,
                tenDangNhap = ?,
                vaiTro = ?,
                trangThai = ?,
                matKhau = ?
            WHERE id = ?

        """, (

            hoTen,
            email,
            tenDangNhap,
            vaiTro,
            trangThai,
            matKhau,
            id

        ))

    # KHÔNG ĐỔI PASSWORD
    else:

        conn.execute("""

            UPDATE nguoi_dung
            SET
                hoTen = ?,
                email = ?,
                tenDangNhap = ?,
                vaiTro = ?,
                trangThai = ?
            WHERE id = ?

        """, (

            hoTen,
            email,
            tenDangNhap,
            vaiTro,
            trangThai,
            id

        ))

    conn.commit()

    conn.close()


# =========================
# KHÓA USER
# =========================
def lock_user(user_id):

    conn = get_connection()

    conn.execute("""

        UPDATE nguoi_dung
        SET trangThai = 0
        WHERE id = ?

    """, (user_id,))

    conn.commit()

    conn.close()


# =========================
# MỞ KHÓA USER
# =========================
def unlock_user(user_id):

    conn = get_connection()

    conn.execute("""

        UPDATE nguoi_dung
        SET trangThai = 1
        WHERE id = ?

    """, (user_id,))

    conn.commit()

    conn.close()


# =========================
# THÊM USER
# =========================
def add_user(
    tenDangNhap,
    matKhau,
    hoTen,
    email,
    soDienThoai,
    vaiTro
):

    conn = get_connection()

    conn.execute("""

        INSERT INTO nguoi_dung
        (
            tenDangNhap,
            matKhau,
            hoTen,
            email,
            soDienThoai,
            vaiTro,
            trangThai
        )

        VALUES (?, ?, ?, ?, ?, ?, 1)

    """, (

        tenDangNhap,
        matKhau,
        hoTen,
        email,
        soDienThoai,
        vaiTro

    ))

    conn.commit()

    conn.close()