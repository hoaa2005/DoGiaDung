import sqlite3

DB_PATH = "database/database.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_suppliers():
    conn = get_db_connection()
    suppliers = conn.execute("SELECT * FROM nha_cung_cap ORDER BY id DESC").fetchall()
    conn.close()
    return suppliers

def add_supplier(data):
    conn = get_db_connection()
    sql = "INSERT INTO nha_cung_cap (ten_ncc, nguoi_lien_he, so_dien_thoai, email, dia_chi, danh_muc_cung_cap) VALUES (?,?,?,?,?,?)"
    conn.execute(sql, (data['ten'], data['nguoi_lh'], data['sdt'], data['email'], data['dia_chi'], data['danh_muc']))
    conn.commit()
    conn.close()

def delete_supplier(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM nha_cung_cap WHERE id = ?", (id,))
    conn.commit()
    conn.close()