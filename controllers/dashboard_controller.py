import sqlite3

DB_PATH = "database/database.db"

# =========================
# KẾT NỐI DB
# =========================
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# =========================
# TỔNG DOANH THU
# =========================
def tong_doanh_thu():
    conn = get_connection()

    result = conn.execute("""
        SELECT IFNULL(SUM(tongTien),0) as total
        FROM don_hang
    """).fetchone()

    conn.close()

    return result["total"]

# =========================
# TỔNG ĐƠN HÀNG
# =========================
def tong_don_hang():
    conn = get_connection()

    result = conn.execute("""
        SELECT COUNT(*) as total
        FROM don_hang
    """).fetchone()

    conn.close()

    return result["total"]

# =========================
# TỔNG USER
# =========================
def tong_user():
    conn = get_connection()

    result = conn.execute("""
        SELECT COUNT(*) as total
        FROM nguoi_dung
    """).fetchone()

    conn.close()

    return result["total"]

# =========================
# DOANH THU 7 NGÀY
# =========================
def doanh_thu_7_ngay():

    conn = get_connection()

    rows = conn.execute("""
        SELECT
            DATE(ngayTao) as ngay,
            SUM(tongTien) as doanhThu
        FROM don_hang
        GROUP BY DATE(ngayTao)
        ORDER BY DATE(ngayTao)
    """).fetchall()

    conn.close()

    labels = []
    data = []

    for row in rows:
        labels.append(row["ngay"])
        data.append(row["doanhThu"])

    return labels, data

# =========================
# TOP SẢN PHẨM
# =========================
def top_san_pham():

    conn = get_connection()

    rows = conn.execute("""
        SELECT
            san_pham.tenSanPham,
            SUM(chi_tiet_don_hang.soLuong) as total
        FROM chi_tiet_don_hang

        JOIN san_pham
        ON san_pham.id = chi_tiet_don_hang.sanPhamId

        GROUP BY san_pham.tenSanPham

        ORDER BY total DESC

        LIMIT 5
    """).fetchall()

    conn.close()

    labels = []
    data = []

    for row in rows:
        labels.append(row["tenSanPham"])
        data.append(row["total"])

    return labels, data