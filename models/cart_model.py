import sqlite3


def get_db_connection():
    # Giả định cấu trúc thư mục của bạn là file này nằm trong thư mục /models/
    conn = sqlite3.connect("database/database.db")
    conn.row_factory = sqlite3.Row
    return conn


def get_cart_items_details_db(cart_session):
    """
    Input: cart_session = {'1': 2, '5': 1} (ID sản phẩm: Số lượng)
    Output: List các dict chi tiết sản phẩm
    """
    if not cart_session:
        return []

    conn = get_db_connection()
    try:
        product_ids = list(cart_session.keys())
        placeholders = ','.join(['?'] * len(product_ids))

        query = f"""
            SELECT p.id, p.tenSanPham, p.gia, t.soLuong as tonKho,
                   (SELECT duongDanAnh FROM hinh_anh_san_pham WHERE sanPhamId = p.id LIMIT 1) as duongDanAnh
            FROM san_pham p
            LEFT JOIN ton_kho t ON p.id = t.sanPhamId
            WHERE p.id IN ({placeholders})
        """

        rows = conn.execute(query, product_ids).fetchall()

        items = []
        for row in rows:
            p_id = str(row['id'])
            qty = cart_session.get(p_id, 0)
            items.append({
                'id': row['id'],
                'tenSanPham': row['tenSanPham'],
                'gia': row['gia'],
                'duongDanAnh': row['duongDanAnh'],
                'tonKho': row['tonKho'],
                'soLuongMua': qty,
                'thanhTien': row['gia'] * qty
            })
        return items
    finally:
        conn.close()


def get_user_vouchers_db(user_id):
    """Lấy các voucher còn hiệu lực của người dùng"""
    conn = get_db_connection()
    try:
        query = """
            SELECT v.id, v.maCode, v.phanTram
            FROM giam_gia v
            JOIN voucher_nguoi_dung vn ON v.id = vn.giamGiaId
            WHERE vn.nguoiDungId = ? AND vn.trangThai = 1
        """
        return conn.execute(query, (user_id,)).fetchall()
    finally:
        conn.close()


def get_addresses_db(user_id):
    """Lấy danh sách địa chỉ người dùng"""
    conn = get_db_connection()
    try:
        return conn.execute("SELECT * FROM dia_chi WHERE nguoiDungId = ?", (user_id,)).fetchall()
    finally:
        conn.close()