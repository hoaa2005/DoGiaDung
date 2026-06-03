import sqlite3

def get_db_connection():
    conn = sqlite3.connect("database/database.db")
    conn.row_factory = sqlite3.Row
    return conn


# 1. Lấy danh sách đơn hàng của người dùng
def get_orders_by_user_db(user_id):
    conn = get_db_connection()
    try:
        return conn.execute(
            "SELECT * FROM don_hang WHERE nguoiDungId = ? ORDER BY ngayTao DESC",
            (user_id,)
        ).fetchall()
    finally:
        conn.close()


# 2. Xem chi tiết đơn hàng (Sử dụng cho trang chi tiết)
def get_order_details_db(order_id):
    conn = get_db_connection()
    try:
        query = """
            SELECT sp.tenSanPham, ct.soLuong, ct.gia, (ct.soLuong * ct.gia) AS thanhTien
            FROM chi_tiet_don_hang ct
            JOIN san_pham sp ON ct.sanPhamId = sp.id
            WHERE ct.donHangId = ?
        """
        return conn.execute(query, (order_id,)).fetchall()
    finally:
        conn.close()


# 3. Hủy đơn hàng (Nghiệp vụ quan trọng: Hoàn lại tồn kho)
def cancel_order_db(order_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN TRANSACTION")

        # Kiểm tra đơn hàng thuộc về user và đang ở trạng thái 'Chờ xử lý'
        order = cursor.execute(
            "SELECT * FROM don_hang WHERE id = ? AND nguoiDungId = ? AND trangThai = 'Chờ xử lý'",
            (order_id, user_id)
        ).fetchone()

        if not order:
            raise Exception("Đơn hàng không tồn tại hoặc đã được xử lý, không thể hủy!")

        # Lấy danh sách sản phẩm trong đơn để hoàn kho
        items = cursor.execute("SELECT sanPhamId, soLuong FROM chi_tiet_don_hang WHERE donHangId = ?",
                               (order_id,)).fetchall()

        for item in items:
            cursor.execute("UPDATE ton_kho SET soLuong = soLuong + ? WHERE sanPhamId = ?",
                           (item["soLuong"], item["sanPhamId"]))

        # Cập nhật trạng thái đơn hàng
        cursor.execute("UPDATE don_hang SET trangThai = 'Đã hủy' WHERE id = ?", (order_id,))

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# --- BỔ SUNG VÀO CUỐI FILE models/order_user_model.py ---

def create_order_db(user_id, cart_items, tong_tien, dia_chi, thanh_toan_id):
    """
    cart_items: Danh sách các dict sản phẩm từ hàm get_cart_items_details_db
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Bắt đầu giao dịch để đảm bảo an toàn dữ liệu
        cursor.execute("BEGIN TRANSACTION")

        # 1. Thêm vào bảng don_hang
        # Đảm bảo tên các cột trong DB của bạn khớp với ('nguoiDungId', 'tongTien', 'diaChi', 'trangThai', 'thanhToanId', 'ngayTao')
        cursor.execute("""
            INSERT INTO don_hang (nguoiDungId, tongTien, diaChi, trangThai, thanhToanId, ngayTao)
            VALUES (?, ?, ?, 'Chờ xử lý', ?, datetime('now'))
        """, (user_id, tong_tien, dia_chi, thanh_toan_id))

        order_id = cursor.lastrowid

        # 2. Thêm vào chi_tiet_don_hang và Trừ kho
        for item in cart_items:
            # Lưu chi tiết đơn hàng
            cursor.execute("""
                INSERT INTO chi_tiet_don_hang (donHangId, sanPhamId, soLuong, gia)
                VALUES (?, ?, ?, ?)
            """, (order_id, item['id'], item['soLuong mua'], item['gia']))

            # Trừ tồn kho (Cập nhật bảng ton_kho)
            cursor.execute("UPDATE ton_kho SET soLuong = soLuong - ? WHERE sanPhamId = ?",
                           (item['soLuong mua'], item['id']))

        # Lưu thay đổi
        conn.commit()
        return order_id
    except Exception as e:
        conn.rollback()  # Hoàn tác nếu có lỗi
        raise e
    finally:
        conn.close()