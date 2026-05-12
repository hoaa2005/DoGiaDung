import sqlite3

DB_PATH = "database/database.db"


# =========================
# TỔNG DOANH THU
# =========================
def tong_doanh_thu():

    conn = sqlite3.connect(DB_PATH)

    result = conn.execute("""
        SELECT IFNULL(SUM(tongTien),0)
        FROM don_hang
    """).fetchone()[0]

    conn.close()

    return result


# =========================
# TỔNG ĐƠN
# =========================
def tong_don_hang():

    conn = sqlite3.connect(DB_PATH)

    result = conn.execute("""
        SELECT COUNT(*)
        FROM don_hang
    """).fetchone()[0]

    conn.close()

    return result


# =========================
# TỔNG USER
# =========================
def tong_user():

    conn = sqlite3.connect(DB_PATH)

    result = conn.execute("""
        SELECT COUNT(*)
        FROM nguoi_dung
    """).fetchone()[0]

    conn.close()

    return result


# =========================
# DOANH THU 7 NGÀY
# =========================
def doanh_thu_7_ngay():

    conn = sqlite3.connect(DB_PATH)

    rows = conn.execute("""
        SELECT DATE(ngayTao), IFNULL(SUM(tongTien),0)
        FROM don_hang
        GROUP BY DATE(ngayTao)
        ORDER BY DATE(ngayTao)
        LIMIT 7
    """).fetchall()

    conn.close()

    labels = []
    data = []

    for row in rows:
        labels.append(row[0])
        data.append(row[1])

    return labels, data


# =========================
# TOP SẢN PHẨM
# =========================
def top_san_pham():

    conn = sqlite3.connect(DB_PATH)

    rows = conn.execute("""
        SELECT san_pham.tenSanPham,
               SUM(chi_tiet_don_hang.soLuong)
        FROM chi_tiet_don_hang
        JOIN san_pham
        ON san_pham.id = chi_tiet_don_hang.sanPhamId
        GROUP BY san_pham.id
        ORDER BY SUM(chi_tiet_don_hang.soLuong) DESC
        LIMIT 5
    """).fetchall()

    conn.close()

    labels = []
    data = []

    for row in rows:
        labels.append(row[0])
        data.append(row[1])

    return labels, data