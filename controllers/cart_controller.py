from flask import session, redirect, url_for, render_template, request, flash
from models.cart_model import get_cart_items_details_db, get_user_vouchers_db, get_addresses_db
import sqlite3


# Hàm chính hiển thị trang giỏ hàng
def cart_page_controller():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    cart = session.get("cart", {})

    # Lấy dữ liệu từ Model
    items = get_cart_items_details_db(cart)
    vouchers = get_user_vouchers_db(user_id)
    addresses = get_addresses_db(user_id)

    # Tính tổng tiền hàng
    total_goods_price = sum(item['thanhTien'] for item in items)

    return render_template("cart.html",
                           items=items,
                           total_goods_price=total_goods_price,
                           vouchers=vouchers,
                           addresses=addresses)


# Hàm cập nhật số lượng (+ / -)
def update_cart_controller(product_id):
    cart = session.get("cart", {})
    action = request.form.get("action")
    p_id = str(product_id)

    if p_id in cart:
        if action == "increase":
            cart[p_id] += 1
        elif action == "decrease":
            cart[p_id] -= 1
            if cart[p_id] <= 0:
                cart.pop(p_id)

    session["cart"] = cart
    return redirect(url_for('cart'))


# Hàm xóa sản phẩm khỏi giỏ
def delete_cart_item_controller(product_id):
    cart = session.get("cart", {})
    cart.pop(str(product_id), None)
    session["cart"] = cart
    return redirect(url_for('cart'))