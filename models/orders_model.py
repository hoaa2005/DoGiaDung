import sqlite3
from datetime import datetime

# Đường dẫn DB thống nhất
DB_PATH = "database/database.db"


def get_db_connection():
    """Tạo kết nối tới SQLite và trả về Row để truy xuất theo tên cột"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# --- NHÓM 1: TRUY VẤN DỮ LIỆU (READ) ---

def get_all_orders():
    """Lấy danh sách đơn hàng kèm thông tin khách hàng để hiển thị bên trái bảng"""
    conn = get_db_connection()
    sql = """
        SELECT dh.*, nd.hoTen, nd.soDienThoai 
        FROM don_hang dh
        JOIN nguoi_dung nd ON dh.nguoiDungId = nd.id
        ORDER BY dh.ngayTao DESC
    """
    orders = conn.execute(sql).fetchall()
    conn.close()
    return orders


def get_order_by_id(order_id):
    """Lấy thông tin chi tiết của 1 đơn hàng và địa chỉ giao hàng"""
    conn = get_db_connection()
    sql = """
        SELECT dh.*, nd.hoTen, nd.soDienThoai, dc.diaChiCuThe, dc.tinhThanh
        FROM don_hang dh
        JOIN nguoi_dung nd ON dh.nguoiDungId = nd.id
        JOIN dia_chi dc ON dh.diaChiId = dc.id
        WHERE dh.id = ?
    """
    order = conn.execute(sql, (order_id,)).fetchone()
    conn.close()
    return order


def get_order_items(order_id):
    """Lấy danh sách sản phẩm nằm trong đơn hàng"""
    conn = get_db_connection()
    sql = """
        SELECT ctdh.*, sp.tenSanPham 
        FROM chi_tiet_don_hang ctdh
        JOIN san_pham sp ON ctdh.sanPhamId = sp.id
        WHERE ctdh.donHangId = ?
    """
    items = conn.execute(sql, (order_id,)).fetchall()
    conn.close()
    return items


def get_order_history(order_id):
    """Lấy nhật ký hoạt động (lịch sử trạng thái) của đơn hàng"""
    conn = get_db_connection()
    sql = """
        SELECT * FROM lich_su_trang_thai 
        WHERE donHangId = ? 
        ORDER BY thoiGian DESC
    """
    history = conn.execute(sql, (order_id,)).fetchall()
    conn.close()
    return history


# --- NHÓM 2: CẬP NHẬT TRẠNG THÁI & LOGIC KHO (UPDATE) ---

def update_order_status(order_id, new_status, admin_id):
    """
    Hàm quan trọng nhất:
    1. Cập nhật trạng thái đơn hàng.
    2. Ghi nhật ký hoạt động vào DB.
    3. Tự động Trừ kho (khi giao) hoặc Hoàn kho (khi hủy).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Lấy trạng thái hiện tại để so sánh logic kho
        current = cursor.execute("SELECT trangThai FROM don_hang WHERE id = ?", (order_id,)).fetchone()
        if not current: return False
        old_status = current['trangThai']

        # 1. Cập nhật bảng don_hang
        cursor.execute("UPDATE don_hang SET trangThai = ? WHERE id = ?", (new_status, order_id))

        # 2. Lưu vào bảng lich_su_trang_thai
        cursor.execute("""
            INSERT INTO lich_su_trang_thai (donHangId, trangThai, nguoiCapNhat, thoiGian) 
            VALUES (?, ?, ?, ?)
        """, (order_id, new_status, admin_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        # 3. XỬ LÝ LOGIC TỒN KHO
        # Lấy danh sách sản phẩm và số lượng trong đơn
        items = cursor.execute("SELECT sanPhamId, soLuong FROM chi_tiet_don_hang WHERE donHangId = ?",
                               (order_id,)).fetchall()

        # TH1: Chốt đơn đi giao (Chờ xác nhận -> Đang giao) => TRỪ KHO
        if old_status == 'Chờ xác nhận' and new_status == 'Đang giao':
            for item in items:
                cursor.execute("UPDATE ton_kho SET soLuong = soLuong - ? WHERE sanPhamId = ?",
                               (item['soLuong'], item['sanPhamId']))

        # TH2: Đơn bị hủy khi đang giao (Đang giao -> Đã hủy) => HOÀN KHO
        elif old_status == 'Đang giao' and new_status == 'Đã hủy':
            for item in items:
                cursor.execute("UPDATE ton_kho SET soLuong = soLuong + ? WHERE sanPhamId = ?",
                               (item['soLuong'], item['sanPhamId']))

        conn.commit()
        return True
    except Exception as e:
        print(f"Lỗi Model: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# --- NHÓM 3: THỐNG KÊ (KPI) ---

def get_order_kpi():
    """Lấy số liệu cho các thẻ báo cáo nhanh"""
    conn = get_db_connection()
    stats = {}
    stats['pending'] = conn.execute("SELECT COUNT(*) FROM don_hang WHERE trangThai = 'Chờ xác nhận'").fetchone()[0]
    stats['shipping'] = conn.execute("SELECT COUNT(*) FROM don_hang WHERE trangThai = 'Đang giao'").fetchone()[0]

    rev = conn.execute("SELECT SUM(tongTien) FROM don_hang WHERE trangThai = 'Hoàn thành'").fetchone()[0]
    stats['revenue'] = rev if rev else 0

    conn.close()
    return stats