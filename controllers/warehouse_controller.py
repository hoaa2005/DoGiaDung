from flask import render_template, request, redirect, session, flash
from models.warehouse_model import get_inventory_status, update_stock_transaction


def warehouse_page():
    items = get_inventory_status()
    return render_template("admin/warehouse.html", items=items)


def warehouse_update_action():
    p_id = request.form.get("sanPhamId")
    qty = request.form.get("soLuong")
    note = request.form.get("ghiChu")
    user_id = session.get("user_id", 1)  # Mặc định admin nếu chưa có session

    if update_stock_transaction(p_id, qty, note, user_id):
        flash("Cập nhật kho thành công!", "success")
    else:
        flash("Có lỗi xảy ra khi cập nhật kho!", "danger")

    return redirect("/admin/warehouse")