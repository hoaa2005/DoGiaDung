from flask import render_template, request, redirect, flash, session
from models.orders_model import (
    get_all_orders, get_order_by_id, get_order_items,
    get_order_history, update_order_status, get_order_kpi
)


# --- 1. TRANG QUẢN LÝ CHÍNH (Giao diện tổng hợp) ---
def list_orders():
    """Hiển thị giao diện gộp: Danh sách đơn hàng bên trái, khung trống bên phải"""
    orders = get_all_orders()
    stats = get_order_kpi()

    return render_template(
        "admin/orders.html",
        orders=orders,
        stats=stats
    )


# --- 2. CHI TIẾT ĐƠN HÀNG (Dùng cho AJAX - Gộp trang) ---
def order_detail_fragment(order_id):
    """
    Trả về chỉ phần nội dung chi tiết đơn hàng (HTML Fragment).
    Hàm này được gọi khi Admin click vào 1 đơn hàng ở danh sách bên trái.
    """
    order = get_order_by_id(order_id)
    if not order:
        return "<p style='padding:20px;'>Lỗi: Không tìm thấy đơn hàng!</p>"

    items = get_order_items(order_id)
    history = get_order_history(order_id)

    # Trả về một file HTML phụ (chỉ chứa phần nội dung chi tiết)
    return render_template(
        "admin/order_detail_sidebar.html",
        order=order,
        items=items,
        history=history
    )


# --- 3. CẬP NHẬT TRẠNG THÁI ---
def update_status():
    """Xử lý thay đổi trạng thái và quay lại trang danh sách"""
    order_id = request.form.get("order_id")
    new_status = request.form.get("new_status")

    # Lấy ID Admin đang đăng nhập từ session
    admin_id = session.get("user_id", 1)

    if order_id and new_status:
        # Gọi Model xử lý logic DB + Kho + Nhật ký
        success = update_order_status(order_id, new_status, admin_id)

        if success:
            flash(f"Đã cập nhật đơn hàng #{order_id} thành '{new_status}'", "success")
        else:
            flash("Cập nhật thất bại! Vui lòng kiểm tra lại tồn kho.", "danger")

    return redirect("/admin/orders")


# --- 4. XÁC NHẬN NHANH (QUICK SHIP) ---
def quick_ship(order_id):
    """Nút bấm nhanh để xác nhận đơn và trừ kho ngay lập tức"""
    admin_id = session.get("user_id", 1)

    # Chuyển thẳng sang Đang giao
    success = update_order_status(order_id, 'Đang giao', admin_id)

    if success:
        flash(f"Đơn #{order_id} đã được xác nhận và trừ kho thành công!", "success")
    else:
        flash("Lỗi xử lý xác nhận nhanh!", "danger")

    return redirect("/admin/orders")