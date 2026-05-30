from flask import session, flash, redirect, request
import sqlite3

def apply_voucher():
    ma_input = request.form.get("maCode")
    conn = sqlite3.connect("database/database.db")
    # Lấy mã từ bảng giam_gia
    voucher = conn.execute("SELECT * FROM giam_gia WHERE maCode = ?", (ma_input,)).fetchone()
    conn.close()

    if voucher:
        # Lưu vào session để khi thanh toán sẽ gọi ra
        session["voucher_code"] = voucher["maCode"]
        session["voucher_phan_tram"] = voucher["phanTram"]
        flash(f"Đã áp dụng mã giảm giá: {voucher['maCode']}")
    else:
        flash("Mã giảm giá không tồn tại!")
    return redirect("/cart")