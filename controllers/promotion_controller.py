from flask import session, flash, redirect, request, render_template
from models.promotion_model import (
    get_all_system_vouchers,
    get_user_vouchers,
    save_voucher_to_user,
    get_voucher_by_code
)


# 1. Hiển thị trang khuyến mãi
def promotion_page_controller():
    if "user_id" not in session:
        return redirect("/auth")

    user_id = session["user_id"]

    # Lấy danh sách mã hệ thống và mã người dùng đã lưu
    system_vouchers = get_all_system_vouchers()
    my_vouchers = get_user_vouchers(user_id)

    return render_template("promotions.html",
                           system_vouchers=system_vouchers,
                           my_vouchers=my_vouchers)


# 2. Lưu mã vào "Ví của tôi"
def save_voucher_controller(giam_gia_id):
    if "user_id" not in session:
        return redirect("/auth")

    user_id = session["user_id"]
    success, message = save_voucher_to_user(user_id, giam_gia_id)

    flash(message)
    return redirect("/promotions")


# 3. Áp dụng mã vào giỏ hàng (Sửa lại từ code của bạn)
def apply_voucher_controller():
    ma_input = request.form.get("maCode")
    if not ma_input:
        flash("Vui lòng nhập mã!")
        return redirect("/cart")

    # Kiểm tra xem người dùng đã "lưu" mã này trong ví chưa (Nâng cao bảo mật)
    # Tạm thời chỉ kiểm tra mã tồn tại trong hệ thống
    voucher = get_voucher_by_code(ma_input)

    if voucher:
        session["applied_voucher"] = {
            "code": voucher["maCode"],
            "phanTram": voucher["phanTram"]
        }
        flash(f"Đã áp dụng mã: {voucher['maCode']} (Giảm {voucher['phanTram']}%)")
    else:
        flash("Mã giảm giá không tồn tại hoặc đã hết hạn!")

    return redirect("/cart")