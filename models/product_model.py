import sqlite3
from datetime import datetime

DB_PATH = "database/database.db"


# ===============================================================================
# KẾT NỐI DATABASE
# ===============================================================================
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ===============================================================================
# [USER & ADMIN] LẤY SẢN PHẨM PHỤC VỤ TÌM KIẾM / QUẢN LÝ
# ===============================================================================
def get_all_products_db(keyword='', category=''):
    conn = get_db_connection()

    sql = """
        SELECT
            p.*,
            d.tenDanhMuc,
            ncc.tenNhaCungCap,
            IFNULL(t.soLuong, 0) AS soLuong,
            (
                SELECT duongDanAnh
                FROM hinh_anh_san_pham
                WHERE sanPhamId = p.id
                ORDER BY id DESC
                LIMIT 1
            ) AS duongDanAnh
        FROM san_pham p
        LEFT JOIN danh_muc d ON p.danhMucId = d.id
        LEFT JOIN nha_cung_cap ncc ON p.nhaCungCapId = ncc.id
        LEFT JOIN ton_kho t ON p.id = t.sanPhamId
        WHERE p.tenSanPham LIKE ?
    """
    params = [f"%{keyword}%"]

    if category:
        sql += " AND p.danhMucId = ? "
        params.append(category)

    sql += " ORDER BY p.id DESC "

    products = conn.execute(sql, params).fetchall()
    conn.close()
    return products


# ===============================================================================
# [USER] TRUY VẤN DANH MỤC KÈM SỐ LƯỢNG SẢN PHẨM ĐANG BÁN (SIDEBAR TRÁI)
# ===============================================================================
def get_categories_with_count_db():
    conn = get_db_connection()
    query = """
        SELECT dm.*, COUNT(sp.id) AS soLuongSp
        FROM danh_muc dm
        LEFT JOIN san_pham sp ON dm.id = sp.danhMucId AND sp.trangThai = 1
        GROUP BY dm.id
        ORDER BY dm.tenDanhMuc ASC
    """
    categories = conn.execute(query).fetchall()
    conn.close()
    return categories


# ===============================================================================
# [USER] BỘ LỌC, TÌM KIẾM VÀ SẮP XẾP SẢN PHẨM TRANG USER (BÊN PHẢI)
# ===============================================================================
def get_filtered_products_db(category_id=None, sort_option="newest", search_query=None):
    conn = get_db_connection()

    base_query = """
        SELECT sp.*, dm.tenDanhMuc, ha.duongDanAnh
        FROM san_pham sp
        LEFT JOIN danh_muc dm ON sp.danhMucId = dm.id
        LEFT JOIN (
            SELECT sanPhamId, duongDanAnh 
            FROM hinh_anh_san_pham 
            WHERE id IN (SELECT MAX(id) FROM hinh_anh_san_pham GROUP BY sanPhamId)
        ) ha ON sp.id = ha.sanPhamId
        WHERE sp.trangThai = 1
    """
    params = []

    # 1. Tìm kiếm theo từ khóa
    if search_query:
        base_query += " AND sp.tenSanPham LIKE ?"
        params.append(f"%{search_query}%")

    # 2. Lọc theo danh mục click ở Sidebar
    if category_id:
        base_query += " AND sp.danhMucId = ?"
        params.append(category_id)

    # 3. Sắp xếp nâng cao
    if sort_option == "price_asc":
        base_query += " ORDER BY sp.gia ASC"
    elif sort_option == "price_desc":
        base_query += " ORDER BY sp.gia DESC"
    else:
        base_query += " ORDER BY sp.id DESC"  # Mới nhất lên đầu

    products = conn.execute(base_query, params).fetchall()
    conn.close()
    return products


# ===============================================================================
# [ADMIN] CẢNH BÁO SẮP HẾT HÀNG
# ===============================================================================
def get_low_stock_alerts(threshold=5):
    conn = get_db_connection()
    sql = """
        SELECT
            p.id,
            p.tenSanPham,
            IFNULL(t.soLuong, 0) AS soLuong
        FROM san_pham p
        LEFT JOIN ton_kho t ON p.id = t.sanPhamId
        WHERE IFNULL(t.soLuong, 0) <= ? AND p.trangThai = 1
        ORDER BY soLuong ASC
    """
    alerts = conn.execute(sql, (threshold,)).fetchall()
    conn.close()
    return alerts


# ===============================================================================
# [ADMIN] THÊM SẢN PHẨM ĐẦY ĐỦ (TRANSACTION)
# ===============================================================================
def add_product_full(data, image_path, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        tenSanPham = data.get("tenSanPham", "").strip()
        gia = float(data.get("gia", 0))
        danhMucId = data.get("danhMucId")
        moTa = data.get("moTa", "").strip()
        soLuong = int(data.get("soLuong", 0))

        if not tenSanPham:
            return False, "Tên sản phẩm không được để trống"
        if gia <= 0:
            return False, "Giá sản phẩm phải lớn hơn 0"
        if soLuong < 0:
            return False, "Số lượng không hợp lệ"

        category = cursor.execute("SELECT id FROM danh_muc WHERE id = ?", (danhMucId,)).fetchone()
        if not category:
            return False, "Danh mục không tồn tại"

        existing = cursor.execute("SELECT id FROM san_pham WHERE LOWER(tenSanPham) = LOWER(?)",
                                  (tenSanPham,)).fetchone()
        if existing:
            return False, "Tên sản phẩm đã tồn tại"

        # Thêm sản phẩm (Mặc định nhà cung cấp ID = 1)
        cursor.execute("""
            INSERT INTO san_pham (tenSanPham, moTa, gia, danhMucId, nhaCungCapId, trangThai)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (tenSanPham, moTa, gia, danhMucId, 1, 1))

        product_id = cursor.lastrowid

        # Thêm số lượng kho
        cursor.execute("""
            INSERT INTO ton_kho (sanPhamId, soLuong, ngayCapNhat)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (product_id, soLuong))

        # Thêm ảnh đại diện
        if image_path:
            cursor.execute("""
                INSERT INTO hinh_anh_san_pham (sanPhamId, duongDanAnh)
                VALUES (?, ?)
            """, (product_id, image_path))

        # Ghi nhật ký hệ thống
        cursor.execute("""
            INSERT INTO nhat_ky_he_thong (nguoiDungId, hanhDong, bang, banGhiId, thoiGian)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, f"THÊM SẢN PHẨM: {tenSanPham}", "san_pham", product_id,
              datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        conn.commit()
        return True, "Thêm sản phẩm thành công"

    except Exception as e:
        conn.rollback()
        return False, f"Lỗi hệ thống: {str(e)}"
    finally:
        conn.close()


# ===============================================================================
# [ADMIN] CẬP NHẬT SẢN PHẨM NÂNG CAO (TRANSACTION)
# ===============================================================================
def update_product_full(p_id, data, image_path, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        tenSanPham = data.get("tenSanPham", "").strip()
        gia = float(data.get("gia", 0))
        danhMucId = data.get("danhMucId")
        moTa = data.get("moTa", "").strip()
        soLuong = int(data.get("soLuong", 0))

        product = cursor.execute("SELECT * FROM san_pham WHERE id = ?", (p_id,)).fetchone()
        if not product:
            return False, "Sản phẩm không tồn tại"

        if not tenSanPham:
            return False, "Tên sản phẩm không được để trống"
        if gia <= 0:
            return False, "Giá sản phẩm phải lớn hơn 0"
        if soLuong < 0:
            return False, "Số lượng không hợp lệ"

        category = cursor.execute("SELECT id FROM danh_muc WHERE id = ?", (danhMucId,)).fetchone()
        if not category:
            return False, "Danh mục không tồn tại"

        existing = cursor.execute("SELECT id FROM san_pham WHERE LOWER(tenSanPham) = LOWER(?) AND id != ?",
                                  (tenSanPham, p_id)).fetchone()
        if existing:
            return False, "Tên sản phẩm đã tồn tại"

        # Cập nhật thông tin cơ bản
        cursor.execute("""
            UPDATE san_pham SET tenSanPham = ?, moTa = ?, gia = ?, danhMucId = ? WHERE id = ?
        """, (tenSanPham, moTa, gia, danhMucId, p_id))

        # Cập nhật tồn kho
        stock = cursor.execute("SELECT sanPhamId FROM ton_kho WHERE sanPhamId = ?", (p_id,)).fetchone()
        if stock:
            cursor.execute("UPDATE ton_kho SET soLuong = ?, ngayCapNhat = CURRENT_TIMESTAMP WHERE sanPhamId = ?",
                           (soLuong, p_id))
        else:
            cursor.execute("INSERT INTO ton_kho (sanPhamId, soLuong, ngayCapNhat) VALUES (?, ?, CURRENT_TIMESTAMP)",
                           (p_id, soLuong))

        # ===============================================================================
        # SỬA LỖI MẤT ẢNH: Chỉ thực hiện xoá và thay đổi khi có ảnh mới được tải lên thực sự
        # ===============================================================================
        if image_path:
            cursor.execute("DELETE FROM hinh_anh_san_pham WHERE sanPhamId = ?", (p_id,))
            cursor.execute("INSERT INTO hinh_anh_san_pham (sanPhamId, duongDanAnh) VALUES (?, ?)", (p_id, image_path))

        # Ghi nhật ký hệ thống
        cursor.execute("""
            INSERT INTO nhat_ky_he_thong (nguoiDungId, hanhDong, bang, banGhiId, thoiGian)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, f"CẬP NHẬT SẢN PHẨM: {tenSanPham}", "san_pham", p_id,
              datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        conn.commit()
        return True, "Cập nhật sản phẩm thành công"

    except Exception as e:
        conn.rollback()
        return False, f"Lỗi hệ thống: {str(e)}"
    finally:
        conn.close()


# ===============================================================================
# [ADMIN] ẨN / HIỆN SẢN PHẨM
# ===============================================================================
def toggle_status_db(p_id, status, user_id):
    conn = get_db_connection()
    try:
        product = conn.execute("SELECT tenSanPham FROM san_pham WHERE id = ?", (p_id,)).fetchone()
        if not product:
            return False

        conn.execute("UPDATE san_pham SET trangThai = ? WHERE id = ?", (status, p_id))
        action = "HIỆN" if status == 1 else "ẨN"

        conn.execute("""
            INSERT INTO nhat_ky_he_thong (nguoiDungId, hanhDong, bang, banGhiId, thoiGian)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, f"{action} SẢN PHẨM: {product['tenSanPham']}", "san_pham", p_id,
              datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        conn.close()


# ===============================================================================
# [ADMIN] XOÁ SẢN PHẨM KHỎI HỆ THỐNG
# ===============================================================================
def delete_product_db(p_id, user_id):
    conn = get_db_connection()
    try:
        product = conn.execute("SELECT tenSanPham FROM san_pham WHERE id = ?", (p_id,)).fetchone()
        if not product:
            return False, "Sản phẩm không tồn tại"

        order_exist = conn.execute("SELECT id FROM chi_tiet_don_hang WHERE sanPhamId = ? LIMIT 1", (p_id,)).fetchone()
        if order_exist:
            return False, "Không thể xóa sản phẩm đã có trong đơn hàng"

        # Tiến hành xóa các bảng liên quan trước
        conn.execute("DELETE FROM hinh_anh_san_pham WHERE sanPhamId = ?", (p_id,))
        conn.execute("DELETE FROM ton_kho WHERE sanPhamId = ?", (p_id,))
        conn.execute("DELETE FROM lich_su_kho WHERE sanPhamId = ?", (p_id,))
        conn.execute("DELETE FROM san_pham WHERE id = ?", (p_id,))

        # Nhật ký hệ thống
        conn.execute("""
            INSERT INTO nhat_ky_he_thong (nguoiDungId, hanhDong, bang, banGhiId, thoiGian)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, f"XÓA SẢN PHẨM: {product['tenSanPham']}", "san_pham", p_id,
              datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        conn.commit()
        return True, "Đã xóa sản phẩm"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


# ===============================================================================
# [ADMIN] LỊCH SỬ THAY ĐỔI CỦA 1 SẢN PHẨM
# ===============================================================================
def get_product_history(p_id):
    conn = get_db_connection()
    logs = conn.execute("""
        SELECT n.*, u.hoTen
        FROM nhat_ky_he_thong n
        LEFT JOIN nguoi_dung u ON n.nguoiDungId = u.id
        WHERE n.bang = 'san_pham' AND n.banGhiId = ?
        ORDER BY n.id DESC
    """, (p_id,)).fetchall()
    conn.close()
    return logs


# ===============================================================================
# [ADMIN] TOÀN BỘ NHẬT KÝ HOẠT ĐỘNG
# ===============================================================================
def get_all_logs_db():
    conn = get_db_connection()
    logs = conn.execute("""
        SELECT n.*, u.hoTen
        FROM nhat_ky_he_thong n
        LEFT JOIN nguoi_dung u ON n.nguoiDungId = u.id
        WHERE n.bang = 'san_pham'
        ORDER BY n.id DESC
        LIMIT 50
    """).fetchall()
    conn.close()
    return logs