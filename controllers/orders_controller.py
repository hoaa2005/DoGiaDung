from flask import render_template, session, redirect, flash, request
from models.orders_model import get_all_orders_db, get_order_detail_db, update_order_status_db


# =========================
# TRANG ĐƠN HÀNG (QUẢN LÝ)
# =========================
def orders_manage():
    # Kiểm tra đăng nhập và quyền Admin (vaiTro == 1)
    if "user_id" not in session or session.get("vaiTro") != 1:
        return redirect("/auth")

    orders = get_all_orders_db()

    # Đảm bảo đường dẫn này khớp với file của bạn trong templates/admin/
    return render_template("admin/orders.html", orders=orders)


# =========================
# SIDEBAR CHI TIẾT (AJAX/FRAGMENT)
# =========================
def order_detail_fragment(order_id):
    # Kiểm tra quyền truy cập
    if "user_id" not in session or session.get("vaiTro") != 1:
        return "Unauthorized", 403

    data = get_order_detail_db(order_id)

    if not data:
        return "Không tìm thấy đơn hàng", 404

    return render_template(
        "admin/order_detail_sidebar.html",
        order=data["order"],
        customer=data["customer"],
        address=data["address"],
        items=data["items"],
        payment=data["payment"]
    )


# =========================
# CẬP NHẬT TRẠNG THÁI
# =========================
def update_order_status(order_id):
    # Kiểm tra quyền truy cập
    if "user_id" not in session or session.get("vaiTro") != 1:
        return redirect("/auth")

    status = request.form.get("trangThai")
    user_id = session.get("user_id")

    success, message = update_order_status_db(order_id, status, user_id)

    if success:
        flash(message, "success")
    else:
        flash(message, "danger")

    return redirect("/admin/orders")