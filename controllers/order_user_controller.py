from flask import session, request, redirect, url_for, flash, render_template
from models.order_user_model import get_cart_items_details_db, create_order_transaction_db


def cart_page_controller():
    if "user_id" not in session:
        flash("⚠️ Vui lòng đăng nhập để xem giỏ hàng!")
        return redirect("/auth")

    cart = session.get("cart", {})
    items = get_cart_items_details_db(cart)
    total_goods_price = sum(item["thanhTien"] for item in items)
    return render_template("cart.html", items=items, total_goods_price=total_goods_price)


def add_to_cart_controller(p_id):
    # Kiểm tra đăng nhập trước khi cho phép thêm
    if "user_id" not in session:
        flash("⚠️ Vui lòng đăng nhập để thêm sản phẩm vào giỏ!")
        return redirect("/auth")

    cart = session.get("cart", {})
    p_id_str = str(p_id)
    cart[p_id_str] = cart.get(p_id_str, 0) + 1
    session["cart"] = cart

    flash("Đã thêm vào giỏ hàng! ✨")
    return redirect(request.referrer or "/products")


def buy_now_controller(p_id):
    if "user_id" not in session:
        flash("⚠️ Vui lòng đăng nhập để mua hàng!")
        return redirect("/auth")

    cart = session.get("cart", {})
    p_id_str = str(p_id)
    cart[p_id_str] = cart.get(p_id_str, 0) + 1
    session["cart"] = cart

    return redirect(url_for('cart_page'))


def update_cart_controller(p_id):
    if "user_id" not in session: return redirect("/auth")

    cart = session.get("cart", {})
    action = request.form.get("action")
    p_id_str = str(p_id)

    if p_id_str in cart:
        if action == "increase":
            cart[p_id_str] += 1
        elif action == "decrease":
            cart[p_id_str] -= 1
        if cart[p_id_str] <= 0: cart.pop(p_id_str, None)

    session["cart"] = cart
    return redirect(url_for('cart_page'))


def delete_cart_item_controller(p_id):
    if "user_id" not in session: return redirect("/auth")
    cart = session.get("cart", {})
    cart.pop(str(p_id), None)
    session["cart"] = cart
    flash("Đã xóa sản phẩm.")
    return redirect(url_for('cart_page'))


def checkout_process_controller():
    if "user_id" not in session:
        flash("Vui lòng đăng nhập để thanh toán!")
        return redirect("/auth")

    cart = session.get("cart", {})
    if not cart:
        flash("Giỏ hàng trống!")
        return redirect(url_for('cart_page'))

    checkout_data = {
        "diaChi": request.form.get("diaChi"),
        "vanChuyen": request.form.get("vanChuyen"),
        "thanhToan": request.form.get("thanhToan")
    }

    try:
        order_id = create_order_transaction_db(session["user_id"], cart, checkout_data)
        session.pop("cart", None)  # Xóa giỏ hàng chỉ khi đặt đơn thành công
        flash(f"🎉 Đặt hàng thành công! Đơn hàng: #{order_id}")
        return redirect("/")
    except Exception:
        flash("Lỗi đặt hàng, vui lòng thử lại!")
        return redirect(url_for('cart_page'))

