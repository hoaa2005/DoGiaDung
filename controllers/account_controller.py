from flask import render_template, request, redirect, flash
from models.account_model import *
import re

# =========================
# HIỂN THỊ
# =========================
def account_page():

    users = get_all_users()

    return render_template(
        "admin/account.html",
        users=users
    )

# =========================
# XOÁ USER
# =========================
def delete_account(id):

    delete_user(id)

    flash("Xóa tài khoản thành công")

    return redirect("/admin/accounts")

# =========================
# UPDATE USER
# =========================
def edit_account(id):

    hoTen = request.form.get("hoTen", "").strip()
    email = request.form.get("email", "").strip()
    vaiTro = request.form.get("vaiTro")
    trangThai = request.form.get("trangThai")

    # VALIDATE
    if not hoTen or not email:
        flash("Không được để trống")
        return redirect("/admin/accounts")

    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        flash("Email không hợp lệ")
        return redirect("/admin/accounts")

    update_user(id, hoTen, email, vaiTro, trangThai)

    flash("Cập nhật thành công")

    return redirect("/admin/accounts")