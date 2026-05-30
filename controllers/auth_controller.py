from flask import request, redirect, flash, session
from models.user_model import (
    get_user_by_email,
    get_user_by_username,
    create_user
)
import re


# =============================
# LOGIN (ĐÃ CẬP NHẬT HIỂN THỊ HỌ TÊN)
# =============================
def login():
    email = request.form.get("email", "").strip()
    matKhau = request.form.get("matKhau", "")

    if not email or not matKhau:
        flash("Vui lòng nhập đầy đủ email và mật khẩu")
        return redirect("/auth")

    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        flash("Email không đúng định dạng")
        return redirect("/auth")

    user = get_user_by_email(email)

    if not user:
        flash("Tài khoản không tồn tại")
        return redirect("/auth")

    if user["matKhau"] != matKhau:
        flash("Sai mật khẩu")
        return redirect("/auth")

    if user["trangThai"] == 0:
        flash("Tài khoản đã bị khóa")
        return redirect("/auth")

    # Gán các giá trị cốt lõi vào hệ thống Session
    session["user_id"] = user["id"]
    session["vaiTro"] = user["vaiTro"]

    # CẬP NHẬT QUAN TRỌNG: Lấy chính xác trường hoTen từ database để đẩy lên Header
    session["hoTen"] = user["hoTen"]

    flash("Đăng nhập thành công!")

    if user["vaiTro"] == 1:
        return redirect("/admin")
    elif user["vaiTro"] == 2:
        return redirect("/staff")
    else:
        return redirect("/")


# =============================
# REGISTER (GIỮ NGUYÊN)
# =============================
def register():
    tenDangNhap = request.form.get("tenDangNhap", "").strip()
    hoTen = request.form.get("hoTen", "").strip()
    email = request.form.get("email", "").strip()
    soDienThoai = request.form.get("soDienThoai", "").strip()
    matKhau = request.form.get("matKhau", "")
    terms = request.form.get("terms")

    # 1. CHECK RỖNG
    if not all([tenDangNhap, hoTen, email, soDienThoai, matKhau]):
        flash("Vui lòng nhập đầy đủ thông tin")
        return redirect("/auth?form=register")

    # 2. EMAIL
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        flash("Email không hợp lệ")
        return redirect("/auth?form=register")

    # 3. SĐT
    if not re.match(r"^0\d{9}$", soDienThoai):
        flash("Số điện thoại phải đủ 10 số và bắt đầu bằng 0")
        return redirect("/auth?form=register")

    # 4. PASSWORD
    if len(matKhau) < 8:
        flash("Mật khẩu phải >= 8 ký tự")
        return redirect("/auth?form=register")

    if not re.search(r"[A-Z]", matKhau):
        flash("Mật khẩu phải có ít nhất 1 chữ hoa")
        return redirect("/auth?form=register")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", matKhau):
        flash("Mật khẩu phải có ký tự đặc biệt")
        return redirect("/auth?form=register")

    # 5. TERMS
    if not terms:
        flash("Bạn phải đồng ý điều khoản")
        return redirect("/auth?form=register")

    # 6. CHECK USERNAME (DÙNG MODEL)
    if get_user_by_username(tenDangNhap):
        flash("Tên đăng nhập đã tồn tại")
        return redirect("/auth?form=register")

    # 7. CHECK EMAIL
    if get_user_by_email(email):
        flash("Email đã tồn tại")
        return redirect("/auth?form=register")

    # 8. INSERT
    create_user(tenDangNhap, matKhau, hoTen, email, soDienThoai)

    flash("Đăng ký thành công! Hãy đăng nhập")
    return redirect("/auth")


def logout():
    """Đăng xuất an toàn: Giữ lại session['cart'], chỉ xóa thông tin người dùng"""
    # Xóa thông tin đăng nhập
    session.pop("user_id", None)
    session.pop("vaiTro", None)
    session.pop("hoTen", None)

    flash("Đã đăng xuất thành công!")
    return redirect("/")