import sqlite3

DB_PATH = "database/database.db"


# =========================
# KẾT NỐI DATABASE
# =========================
def get_db_connection():

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    return conn


# =========================
# LẤY DANH SÁCH ĐƠN HÀNG
# =========================
def get_all_orders_db():

    conn = get_db_connection()

    sql = """
        SELECT
            d.*,
            n.hoTen,
            n.soDienThoai

        FROM don_hang d

        LEFT JOIN nguoi_dung n
            ON d.nguoiDungId = n.id

        ORDER BY d.id DESC
    """

    data = conn.execute(sql).fetchall()

    conn.close()

    return data


# =========================
# CHI TIẾT ĐƠN HÀNG
# =========================
def get_order_detail_db(order_id):

    conn = get_db_connection()

    # =====================
    # THÔNG TIN ĐƠN HÀNG
    # =====================
    order = conn.execute("""
        SELECT *
        FROM don_hang
        WHERE id = ?
    """, (order_id,)).fetchone()

    if not order:

        conn.close()

        return None

    # =====================
    # KHÁCH HÀNG
    # =====================
    customer = conn.execute("""
        SELECT *
        FROM nguoi_dung
        WHERE id = ?
    """, (order["nguoiDungId"],)).fetchone()

    # =====================
    # ĐỊA CHỈ
    # =====================
    address = conn.execute("""
        SELECT *
        FROM dia_chi
        WHERE id = ?
    """, (order["diaChiId"],)).fetchone()

    # =====================
    # CHI TIẾT SẢN PHẨM
    # =====================
    items = conn.execute("""
        SELECT
            c.*,
            s.tenSanPham

        FROM chi_tiet_don_hang c

        LEFT JOIN san_pham s
            ON c.sanPhamId = s.id

        WHERE c.donHangId = ?
    """, (order_id,)).fetchall()

    # =====================
    # THANH TOÁN
    # =====================
    payment = conn.execute("""
        SELECT
            t.*,
            p.tenPhuongThuc

        FROM thanh_toan t

        LEFT JOIN phuong_thuc_thanh_toan p
            ON t.phuongThucId = p.id

        WHERE t.donHangId = ?

        ORDER BY t.id DESC
        LIMIT 1
    """, (order_id,)).fetchone()

    conn.close()

    return {
        "order": order,
        "customer": customer,
        "address": address,
        "items": items,
        "payment": payment
    }


# =========================
# CẬP NHẬT TRẠNG THÁI
# =========================
def update_order_status_db(order_id, status, user_id):

    conn = get_db_connection()

    try:

        # =====================
        # CHECK ĐƠN HÀNG
        # =====================
        order = conn.execute("""
            SELECT *
            FROM don_hang
            WHERE id = ?
        """, (order_id,)).fetchone()

        if not order:

            return False, "Đơn hàng không tồn tại"

        # =====================
        # UPDATE ĐƠN
        # =====================
        conn.execute("""
            UPDATE don_hang
            SET trangThai = ?
            WHERE id = ?
        """, (
            status,
            order_id
        ))

        # =====================
        # LỊCH SỬ TRẠNG THÁI
        # =====================
        conn.execute("""
            INSERT INTO lich_su_trang_thai
            (
                donHangId,
                trangThai,
                nguoiCapNhat
            )
            VALUES (?, ?, ?)
        """, (
            order_id,
            status,
            user_id
        ))

        # =====================
        # LOG HỆ THỐNG
        # =====================
        conn.execute("""
            INSERT INTO nhat_ky_he_thong
            (
                nguoiDungId,
                hanhDong,
                bang,
                banGhiId
            )
            VALUES (?, ?, ?, ?)
        """, (
            user_id,
            f"CẬP NHẬT ĐƠN HÀNG -> {status}",
            "don_hang",
            order_id
        ))

        conn.commit()

        return True, "Cập nhật trạng thái thành công"

    except Exception as e:

        conn.rollback()

        return False, str(e)

    finally:

        conn.close()