from flask import session, render_template, redirect, url_for, flash, request
from models.order_user_model import get_orders_by_user_db, get_order_details_db, cancel_order_db

from flask import session, render_template, redirect, url_for, flash, request
from models.order_user_model import (
    get_orders_by_user_db,
    get_order_details_db,
    cancel_order_db,
    create_order_db
)
from models.cart_model import get_cart_items_details_db


# ===============================================================================
# XỬ LÝ THANH TOÁN (CHECKOUT)
# ===============================================================================
def checkout_controller():
    if "user_id" not in session:
        return redirect("/login")

    # 1. Lấy dữ liệu từ form thanh toán
    dia_chi_id = request.form.get("diaChiId")
    dia_chi_moi = request.form.get("diaChiMoi")
    thanh_toan_id = request.form.get("thanhToanId")

    # 2. Xử lý địa chỉ
    dia_chi = dia_chi_moi if dia_chi_id == "0" else dia_chi_id

    # 3. Lấy sản phẩm từ giỏ hàng trong session
    cart_session = session.get("cart", {})
    if not cart_session:
        flash("Giỏ hàng của bạn đang trống!")
        return redirect("/cart")

    try:
        # Lấy chi tiết sản phẩm từ Database thông qua cart_model
        items = get_cart_items_details_db(cart_session)

        # Tính tổng tiền từ danh sách items (đảm bảo chính xác từ DB)
        tong_tien = sum(item['thanhTien'] for item in items)

        # Gọi Model để lưu đơn hàng và trừ kho
        order_id = create_order_db(
            session["user_id"],
            items,
            tong_tien,
            dia_chi,
            thanh_toan_id
        )

        # 4. Xóa giỏ hàng sau khi đặt thành công
        session.pop("cart", None)
        flash(f"🎉 Đặt hàng thành công! Mã đơn hàng: #{order_id}")
        return redirect("/my-orders")

    except Exception as e:
        flash(f"❌ Lỗi đặt hàng: {str(e)}")
        return redirect("/cart")

# 1. Hiển thị danh sách đơn hàng
def my_orders_controller():
    if "user_id" not in session:
        return redirect("/login")

    orders = get_orders_by_user_db(session["user_id"])
    return render_template("my_orders.html", orders=orders)


# 2. Xem chi tiết đơn hàng
def order_detail_controller(order_id):
    if "user_id" not in session:
        return redirect("/login")

    details = get_order_details_db(order_id)
    if not details:
        flash("Không tìm thấy thông tin đơn hàng này!")
        return redirect(url_for('my_orders'))

    return render_template("order_detail.html", details=details, order_id=order_id)


# 3. Hủy đơn hàng
def cancel_order_controller(order_id):
    if "user_id" not in session:
        return redirect("/login")

    try:
        cancel_order_db(order_id, session["user_id"])
        flash(f"✅ Đơn hàng #{order_id} đã được hủy thành công và hoàn lại kho.")
    except Exception as e:
        flash(f"❌ Lỗi: {str(e)}")

    return redirect(url_for('my_orders'))