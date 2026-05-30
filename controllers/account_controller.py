from flask import render_template, request, redirect, flash
from models.account_model import *
import re

# =========================
# HIỂN THỊ TRANG TÀI KHOẢN
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

    tenDangNhap = request.form.get("tenDangNhap", "").strip()

    vaiTro = request.form.get("vaiTro")

    matKhau = request.form.get("matKhau", "").strip()

    # GIỮ MẶC ĐỊNH HOẠT ĐỘNG
    trangThai = 1


    # =========================
    # VALIDATE RỖNG
    # =========================
    if not hoTen or not email or not tenDangNhap:

        flash("Không được để trống dữ liệu")

        return redirect("/admin/accounts")


    # =========================
    # VALIDATE EMAIL
    # =========================
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):

        flash("Email không hợp lệ")

        return redirect("/admin/accounts")


    # =========================
    # UPDATE DATABASE
    # =========================
    try:

        update_user(
            id=id,
            hoTen=hoTen,
            email=email,
            tenDangNhap=tenDangNhap,
            vaiTro=vaiTro,
            trangThai=trangThai,
            matKhau=matKhau
        )

        flash("Cập nhật tài khoản thành công")

    except Exception as e:

        flash(f"Lỗi cập nhật: {str(e)}")


    return redirect("/admin/accounts")