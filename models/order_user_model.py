import sqlite3

DB_PATH = "database/database.db"


def get_cart_items_details_db(cart_session_dict):
    """Lấy thông tin sản phẩm từ giỏ hàng Session"""
    if not cart_session_dict:
        return []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        placeholders = ",".join(["?"] * len(cart_session_dict))
        product_ids = [int(k) for k in cart_session_dict.keys()]

        query = f"""
            SELECT p.id, p.tenSanPham, p.gia, t.soLuong AS tonKho,
                   (SELECT duongDanAnh FROM hinh_anh_san_pham WHERE sanPhamId = p.id LIMIT 1) AS duongDanAnh
            FROM san_pham p
            LEFT JOIN ton_kho t ON p.id = t.sanPhamId
            WHERE p.id IN ({placeholders})
        """
        rows = conn.execute(query, product_ids).fetchall()

        cart_items = []
        for row in rows:
            p_id = str(row["id"])
            qty = int(cart_session_dict[p_id])
            cart_items.append({
                "id": row["id"],
                "tenSanPham": row["tenSanPham"],
                "gia": row["gia"],
                "duongDanAnh": row["duongDanAnh"],
                "tonKho": row["tonKho"],
                "soLuong mua": qty,
                "thanhTien": row["gia"] * qty
            })
        return cart_items
    finally:
        conn.close()


def create_order_transaction_db(user_id, cart_session_dict, checkout_data):
    """Lưu đơn hàng và trừ kho"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # 1. Tính tổng tiền
        tongTienHang = 0
        for p_id, qty in cart_session_dict.items():
            product = conn.execute("SELECT gia FROM san_pham WHERE id = ?", (p_id,)).fetchone()
            tongTienHang += product[0] * int(qty)

        phiShip = 30000 if checkout_data["vanChuyen"] == "Express" else 15000
        tongThanhToan = tongTienHang + phiShip

        # 2. Thêm đơn hàng
        cursor.execute("""
            INSERT INTO don_hang (nguoiDungId, ngayDat, tongTien, diaChiGiaoHang, phuongThucVatChuyen, phiVanChuyen, phuongThucThanhToan, trangThaiDonHang)
            VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, 'Chờ xử lý')
        """, (user_id, tongThanhToan, checkout_data["diaChi"], checkout_data["vanChuyen"], phiShip,
              checkout_data["thanhToan"]))

        order_id = cursor.lastrowid

        # 3. Thêm chi tiết và trừ kho
        for p_id, qty in cart_session_dict.items():
            product = conn.execute("SELECT gia FROM san_pham WHERE id = ?", (p_id,)).fetchone()
            cursor.execute("INSERT INTO chi_tiet_don_hang (donHangId, sanPhamId, soLuong, giaBan) VALUES (?, ?, ?, ?)",
                           (order_id, p_id, qty, product[0]))
            cursor.execute("UPDATE ton_kho SET soLuong = soLuong - ? WHERE sanPhamId = ?", (qty, p_id))

        conn.commit()
        return order_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
import sqlite3

def get_orders_by_user(user_id):
    conn = sqlite3.connect("database/database.db")
    conn.row_factory = sqlite3.Row
    orders = conn.execute("SELECT * FROM don_hang WHERE nguoiDungId = ? ORDER BY ngayTao DESC", (user_id,)).fetchall()
    conn.close()
    return orders

def get_order_details(order_id):
    conn = sqlite3.connect("database/database.db")
    conn.row_factory = sqlite3.Row
    # Lấy thông tin sản phẩm trong đơn hàng
    details = conn.execute("""
        SELECT sp.tenSanPham, ct.soLuong, ct.gia 
        FROM chi_tiet_don_hang ct
        JOIN san_pham sp ON ct.sanPhamId = sp.id
        WHERE ct.donHangId = ?
    """, (order_id,)).fetchall()
    conn.close()
    return details