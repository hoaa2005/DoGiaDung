from flask import *
from models.orders_model import *


# =========================
# TRANG ĐƠN HÀNG
# =========================
def orders_manage():

    if "user_id" not in session:
        return redirect("/auth")

    orders = get_all_orders_db()

    return render_template(
        "admin/orders.html",
        orders=orders
    )


# =========================
# SIDEBAR CHI TIẾT
# =========================
def order_detail_fragment(order_id):

    if "user_id" not in session:
        return "Unauthorized"

    data = get_order_detail_db(order_id)

    if not data:
        return "Không tìm thấy đơn hàng"

    return render_template(
        "admin/order_detail_sidebar.html",

        order=data["order"],
        customer=data["customer"],
        address=data["address"],
        items=data["items"],
        payment=data["payment"]
    )


# =========================
# UPDATE TRẠNG THÁI
# =========================
def update_order_status(order_id):

    if "user_id" not in session:
        return redirect("/auth")

    status = request.form.get("trangThai")

    success, message = update_order_status_db(
        order_id,
        status,
        session["user_id"]
    )

    flash(message)

    return redirect("/admin/orders")