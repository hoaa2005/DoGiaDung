import sqlite3

def get_db_connection():
    conn = sqlite3.connect("database/database.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_inventory_status():
    """Lấy danh sách tồn kho khớp với Schema của bạn"""
    conn = get_db_connection()
    # JOIN bảng san_pham với ton_kho và danh_muc
    sql = """
        SELECT 
            sp.id, 
            sp.tenSanPham, 
            dm.tenDanhMuc, 
            tk.soLuong, 
            tk.ngayCapNhat
        FROM san_pham sp
        JOIN ton_kho tk ON sp.id = tk.sanPhamId
        JOIN danh_muc dm ON sp.danhMucId = dm.id
        ORDER BY tk.soLuong ASC
    """
    items = conn.execute(sql).fetchall()
    conn.close()
    return items

def update_stock_transaction(product_id, amount, note, user_id):
    """Cập nhật kho và ghi vào bảng lich_su_kho"""
    conn = get_db_connection()
    try:
        # 1. Cập nhật bảng ton_kho
        conn.execute("""
            UPDATE ton_kho 
            SET soLuong = soLuong + ?, ngayCapNhat = CURRENT_TIMESTAMP 
            WHERE sanPhamId = ?
        """, (amount, product_id))

        # 2. Ghi vào bảng lich_su_kho (Khớp với Schema của bạn)
        # Loại: 'Nhập' nếu số dương, 'Xuất' nếu số âm
        loai_gd = 'Nhập' if int(amount) > 0 else 'Xuất'
        conn.execute("""
            INSERT INTO lich_su_kho (sanPhamId, loai, soLuong, ghiChu, nguoiThucHien)
            VALUES (?, ?, ?, ?, ?)
        """, (product_id, loai_gd, abs(int(amount)), note, user_id))

        conn.commit()
        return True
    except Exception as e:
        print(f"Lỗi kho: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()