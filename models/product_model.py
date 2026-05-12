import sqlite3
from datetime import datetime

DB_PATH = "database/database.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# --- 1. HIỂN THỊ & TÌM KIẾM ---
def get_all_products_db(keyword='', category=''):
    conn = get_db_connection()
    # Sử dụng IFNULL để tránh lỗi NoneType khi sản phẩm chưa có dữ liệu tồn kho
    sql = """
        SELECT p.*, d.tenDanhMuc, IFNULL(t.soLuong, 0) as soLuong,
        (SELECT duongDanAnh FROM hinh_anh_san_pham WHERE sanPhamId = p.id LIMIT 1) as image
        FROM san_pham p
        LEFT JOIN danh_muc d ON p.danhMucId = d.id
        LEFT JOIN ton_kho t ON p.id = t.sanPhamId
        WHERE p.tenSanPham LIKE ?
    """
    params = [f'%{keyword}%']
    if category:
        sql += " AND p.danhMucId = ?"
        params.append(category)

    sql += " ORDER BY p.id DESC"
    data = conn.execute(sql, params).fetchall()
    conn.close()
    return data


# --- 2. CẢNH BÁO TỒN KHO (Sửa lỗi TypeError) ---
def get_low_stock_alerts(threshold=5):
    conn = get_db_connection()
    # IFNULL(t.soLuong, 0) đảm bảo so sánh giữa (int <= int), không phải (None <= int)
    sql = """
        SELECT p.tenSanPham, IFNULL(t.soLuong, 0) as soLuong 
        FROM san_pham p 
        LEFT JOIN ton_kho t ON p.id = t.sanPhamId 
        WHERE IFNULL(t.soLuong, 0) <= ? AND p.trangThai = 1
    """
    alerts = conn.execute(sql, (threshold,)).fetchall()
    conn.close()
    return alerts


# --- 3. THÊM SẢN PHẨM (Xử lý Ngoại lệ trùng lặp & Khởi tạo tồn kho) ---
def add_product_full(data, image_path, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Kiểm tra trùng tên
        existing = cursor.execute("SELECT id FROM san_pham WHERE tenSanPham = ?", (data['tenSanPham'],)).fetchone()
        if existing:
            return False, "Tên sản phẩm đã tồn tại!"

        # Thêm sản phẩm chính
        cursor.execute("""
            INSERT INTO san_pham (tenSanPham, gia, danhMucId, moTa, nhaCungCapId, trangThai)
            VALUES (?, ?, ?, ?, 1, 1)
        """, (data['tenSanPham'], data['gia'], data['danhMucId'], data['moTa']))

        new_id = cursor.lastrowid

        # Quan trọng: Luôn khởi tạo dòng tồn kho để tránh lỗi TypeError sau này
        cursor.execute("INSERT INTO ton_kho (sanPhamId, soLuong) VALUES (?, ?)",
                       (new_id, data.get('soLuong', 0)))

        # Thêm ảnh nếu có
        if image_path:
            cursor.execute("INSERT INTO hinh_anh_san_pham (sanPhamId, duongDanAnh) VALUES (?, ?)", (new_id, image_path))

        # Ghi log hệ thống
        cursor.execute("""
            INSERT INTO nhat_ky_he_thong (nguoiDungId, hanhDong, bang, banGhiId, thoiGian)
            VALUES (?, ?, 'san_pham', ?, ?)
        """, (user_id, f"THÊM MỚI: {data['tenSanPham']}", new_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        conn.commit()
        return True, "Thêm sản phẩm thành công!"
    except Exception as e:
        conn.rollback()
        return False, f"Lỗi: {str(e)}"
    finally:
        conn.close()


# --- 4. SỬA SẢN PHẨM ---
def update_product_full(p_id, data, image_path, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check trùng tên (trừ chính nó)
        existing = cursor.execute("SELECT id FROM san_pham WHERE tenSanPham = ? AND id != ?",
                                  (data['tenSanPham'], p_id)).fetchone()
        if existing:
            return False, "Tên sản phẩm bị trùng với mã khác!"

        cursor.execute("""
            UPDATE san_pham SET tenSanPham=?, gia=?, danhMucId=?, moTa=? WHERE id=?
        """, (data['tenSanPham'], data['gia'], data['danhMucId'], data['moTa'], p_id))

        if image_path:
            cursor.execute("DELETE FROM hinh_anh_san_pham WHERE sanPhamId = ?", (p_id,))
            cursor.execute("INSERT INTO hinh_anh_san_pham (sanPhamId, duongDanAnh) VALUES (?, ?)", (p_id, image_path))

        cursor.execute("""
            INSERT INTO nhat_ky_he_thong (nguoiDungId, hanhDong, bang, banGhiId, thoiGian)
            VALUES (?, ?, 'san_pham', ?, ?)
        """, (user_id, f"SỬA: {data['tenSanPham']}", p_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        conn.commit()
        return True, "Cập nhật thành công!"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


# --- 5. XÓA & ẨN/HIỆN ---
def delete_product_db(p_id, user_id):
    conn = get_db_connection()
    try:
        p = conn.execute("SELECT tenSanPham FROM san_pham WHERE id=?", (p_id,)).fetchone()
        # Xóa cascade thủ công nếu DB không cài đặt
        conn.execute("DELETE FROM ton_kho WHERE sanPhamId=?", (p_id,))
        conn.execute("DELETE FROM hinh_anh_san_pham WHERE sanPhamId=?", (p_id,))
        conn.execute("DELETE FROM san_pham WHERE id=?", (p_id,))

        conn.execute(
            "INSERT INTO nhat_ky_he_thong (nguoiDungId, hanhDong, bang, banGhiId, thoiGian) VALUES (?, ?, 'san_pham', ?, ?)",
            (user_id, f"XÓA: {p['tenSanPham']}", p_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        return True, "Đã xóa vĩnh viễn."
    except:
        return False, "Lỗi khi xóa."
    finally:
        conn.close()


def toggle_status_db(p_id, status, user_id):
    conn = get_db_connection()
    try:
        conn.execute("UPDATE san_pham SET trangThai=? WHERE id=?", (status, p_id))
        action = "HIỆN" if status == 1 else "ẨN"
        conn.execute(
            "INSERT INTO nhat_ky_he_thong (nguoiDungId, hanhDong, bang, banGhiId, thoiGian) VALUES (?, ?, 'san_pham', ?, ?)",
            (user_id, action, p_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


# --- 6. XEM LỊCH SỬ NHẬT KÝ ---
def get_product_history(p_id):
    conn = get_db_connection()
    sql = """
        SELECT n.*, u.hoTen 
        FROM nhat_ky_he_thong n
        JOIN nguoi_dung u ON n.nguoiDungId = u.id
        WHERE n.bang = 'san_pham' AND n.banGhiId = ?
        ORDER BY n.thoiGian DESC
    """
    logs = conn.execute(sql, (p_id,)).fetchall()
    conn.close()
    return logs
def get_all_logs_db():
    conn = get_db_connection()
    sql = """
        SELECT n.*, u.hoTen 
        FROM nhat_ky_he_thong n
        JOIN nguoi_dung u ON n.nguoiDungId = u.id
        ORDER BY n.thoiGian DESC LIMIT 50
    """
    data = conn.execute(sql).fetchall()
    conn.close()
    return data