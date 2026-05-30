from flask import render_template, request, redirect, flash
from models.supplier_model import get_all_suppliers_db, insert_supplier_db, update_supplier_db, delete_supplier_db


def list_suppliers():
    suppliers = get_all_suppliers_db()
    return render_template("admin/suppliers.html", suppliers=suppliers)


def create_supplier():
    ten = request.form.get("tenNhaCungCap")
    sdt = request.form.get("soDienThoai")
    email = request.form.get("email")
    diachi = request.form.get("diaChi")

    success, message = insert_supplier_db(ten, sdt, email, diachi)
    if success:
        flash("Thêm nhà cung cấp mới thành công! 🎉")
    else:
        # Nếu trùng tên/sđt/email, thông báo lỗi từ Model sẽ được truyền trực tiếp ra đây
        flash(message)

    return redirect("/admin/suppliers")


def edit_supplier_action(id):
    ten = request.form.get("tenNhaCungCap")
    sdt = request.form.get("soDienThoai")
    email = request.form.get("email")
    diachi = request.form.get("diaChi")

    success, message = update_supplier_db(id, ten, sdt, email, diachi)
    if success:
        flash("Cập nhật thông tin nhà cung cấp thành công! ✨")
    else:
        # Nếu sửa thông tin bị trùng với một ai đó khác, hệ thống cũng sẽ chặn lại công khai
        flash(message)

    return redirect("/admin/suppliers")


def delete_supplier_action(id):
    success, message = delete_supplier_db(id)
    if success:
        flash("Đã xóa nhà cung cấp ra khỏi hệ thống thành công! 🗑️")
    else:
        flash(f"Không thể xóa! {message}")

    return redirect("/admin/suppliers")