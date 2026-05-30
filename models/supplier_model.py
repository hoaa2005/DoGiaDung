import sqlite3

DB_PATH = "database/database.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_suppliers_db():
    conn = get_db_connection()
    suppliers = conn.execute("SELECT * FROM nha_cung_cap ORDER BY id DESC").fetchall()
    conn.close()
    return suppliers


# ===============================================================================
# THÊM MỚI (CÓ KIỂM TRA TRÙNG LẶP)
# ===============================================================================
def insert_supplier_db(ten, sdt, email, diachi):
    conn = get_db_connection()
    try:
        # 1. Kiểm tra trùng Tên nhà cung cấp
        existing_name = conn.execute(
            "SELECT id FROM nha_cung_cap WHERE LOWER(tenNhaCungCap) = LOWER(?)", (ten,)
        ).fetchone()
        if existing_name:
            return False, "Tên nhà cung cấp này đã tồn tại trong hệ thống!"

        # 2. Kiểm tra trùng Số điện thoại (chỉ check nếu người dùng có nhập sdt)
        if sdt and sdt.strip():
            existing_sdt = conn.execute(
                "SELECT id FROM nha_cung_cap WHERE soDienThoai = ?", (sdt.strip(),)
            ).fetchone()
            if existing_sdt:
                return False, "Số điện thoại này đã được đăng ký cho một đối tác khác!"

        # 3. Kiểm tra trùng Email (chỉ check nếu người dùng có nhập email)
        if email and email.strip():
            existing_email = conn.execute(
                "SELECT id FROM nha_cung_cap WHERE LOWER(email) = LOWER(?)", (email.strip(),)
            ).fetchone()
            if existing_email:
                return False, "Địa chỉ Email này đã được đăng ký cho một đối tác khác!"

        # Nếu vượt qua tất cả các lớp check -> Tiến hành thêm mới
        conn.execute("""
            INSERT INTO nha_cung_cap (tenNhaCungCap, soDienThoai, email, diaChi)
            VALUES (?, ?, ?, ?)
        """, (ten.strip(), sdt.strip() if sdt else None, email.strip() if email else None,
              diachi.strip() if diachi else None))
        conn.commit()
        return True, "Thành công"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


# ===============================================================================
# CẬP NHẬT / SỬA (CÓ KIỂM TRA TRÙNG LẶP - LOẠI TRỪ ID HIỆN TẠI)
# ===============================================================================
def update_supplier_db(id, ten, sdt, email, diachi):
    conn = get_db_connection()
    try:
        # 1. Kiểm tra trùng Tên với các nhà cung cấp KHÁC (id != id hiện tại)
        existing_name = conn.execute(
            "SELECT id FROM nha_cung_cap WHERE LOWER(tenNhaCungCap) = LOWER(?) AND id != ?", (ten, id)
        ).fetchone()
        if existing_name:
            return False, "Tên nhà cung cấp này đã bị trùng với một đối tác khác!"

        # 2. Kiểm tra trùng Số điện thoại với nhà cung cấp KHÁC
        if sdt and sdt.strip():
            existing_sdt = conn.execute(
                "SELECT id FROM nha_cung_cap WHERE soDienThoai = ? AND id != ?", (sdt.strip(), id)
            ).fetchone()
            if existing_sdt:
                return False, "Số điện thoại này đã được đăng ký cho một đối tác khác!"

        # 3. Kiểm tra trùng Email với nhà cung cấp KHÁC
        if email and email.strip():
            existing_email = conn.execute(
                "SELECT id FROM nha_cung_cap WHERE LOWER(email) = LOWER(?) AND id != ?", (email.strip(), id)
            ).fetchone()
            if existing_email:
                return False, "Địa chỉ Email này đã được đăng ký cho một đối tác khác!"

        # Nếu hợp lệ -> Tiến hành cập nhật thay đổi
        conn.execute("""
            UPDATE nha_cung_cap
            SET tenNhaCungCap = ?, soDienThoai = ?, email = ?, diaChi = ?
            WHERE id = ?
        """, (ten.strip(), sdt.strip() if sdt else None, email.strip() if email else None,
              diachi.strip() if diachi else None, id))
        conn.commit()
        return True, "Thành công"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def delete_supplier_db(id):
    conn = get_db_connection()
    try:
        check = conn.execute("SELECT COUNT(*) as total FROM san_pham WHERE nhaCungCapId = ?", (id,)).fetchone()
        if check["total"] > 0:
            return False, f"Nhà cung cấp này đang liên kết với {check['total']} sản phẩm."

        conn.execute("DELETE FROM nha_cung_cap WHERE id = ?", (id,))
        conn.commit()
        return True, "Thành công"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()