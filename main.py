from flask import Flask, render_template, session, redirect
from controllers.auth_controller import login, register

from models.dashboard_model import *
from controllers.account_controller import *
from models.user_model import *
from controllers.orders_controller import *
from controllers.orders_controller import (
    list_orders,
    order_detail_fragment,
    update_status,
    quick_ship
)
app = Flask(__name__)
app.secret_key = "abc123"

# ... (Các import khác giữ nguyên)
from controllers.product_controller import *


# =========================
# AUTH
# =========================
@app.route("/auth")
def auth():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_route():
    return login()


@app.route("/register", methods=["POST"])
def register_route():
    return register()


# =========================
# HOME USER
# =========================
@app.route("/")
def home():

    if "user_id" not in session:
        return redirect("/auth")

    # ADMIN
    if session["vaiTro"] == 1:
        return redirect("/admin")

    return render_template("home.html")


# =========================
# ADMIN DASHBOARD
# =========================
@app.route("/admin")
def admin_dashboard():

    if "user_id" not in session:
        return redirect("/auth")

    if session["vaiTro"] != 1:
        return redirect("/")

    doanh_thu = tong_doanh_thu()
    don_hang = tong_don_hang()
    users = tong_user()

    labels_line, data_line = doanh_thu_7_ngay()

    labels_pie, data_pie = top_san_pham()

    return render_template(
        "admin/dashboard.html",

        doanh_thu=doanh_thu,
        don_hang=don_hang,
        users=users,

        labels_line=labels_line,
        data_line=data_line,

        labels_pie=labels_pie,
        data_pie=data_pie
    )
# =========================
# ACCOUNT PAGE
# =========================
@app.route("/admin/users")
def admin_users():

    if "user_id" not in session:
        return redirect("/auth")

    if session["vaiTro"] != 1:
        return redirect("/")

    users = get_all_users()

    return render_template(
        "admin/account.html",
        users=users
    )
# =========================
# DELETE USER
# =========================
@app.route("/admin/user/delete/<int:user_id>")
def admin_delete_user(user_id):

    if "user_id" not in session:
        return redirect("/auth")

    if session["vaiTro"] != 1:
        return redirect("/")

    if user_id == session["user_id"]:
        flash("Không thể xóa chính mình")
        return redirect("/admin/users")

    delete_user(user_id)

    flash("Xóa tài khoản thành công")

    return redirect("/admin/users")
# =========================
# LOCK USER
# =========================
@app.route("/admin/user/lock/<int:user_id>")
def admin_lock_user(user_id):

    if "user_id" not in session:
        return redirect("/auth")

    if session["vaiTro"] != 1:
        return redirect("/")

    if user_id == session["user_id"]:
        flash("Không thể khóa chính mình")
        return redirect("/admin/users")

    lock_user(user_id)

    flash("Đã khóa tài khoản")

    return redirect("/admin/users")
# =========================
# UNLOCK USER
# =========================
@app.route("/admin/user/unlock/<int:user_id>")
def admin_unlock_user(user_id):

    if "user_id" not in session:
        return redirect("/auth")

    if session["vaiTro"] != 1:
        return redirect("/")

    unlock_user(user_id)

    flash("Đã mở khóa tài khoản")

    return redirect("/admin/users")

@app.route("/admin/account")
def admin_account():

    if "user_id" not in session:
        return redirect("/auth")

    if session["vaiTro"] != 1:
        return redirect("/")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    users = conn.execute("""
        SELECT * FROM nguoi_dung
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "admin/account.html",
        users=users
    )
@app.route("/admin/user/edit/<int:id>", methods=["POST"])
def admin_edit_user(id):

    conn = sqlite3.connect("database.db")

    hoTen = request.form["hoTen"]
    email = request.form["email"]
    tenDangNhap = request.form["tenDangNhap"]
    vaiTro = request.form["vaiTro"]

    conn.execute("""
        UPDATE nguoi_dung
        SET hoTen=?,
            email=?,
            tenDangNhap=?,
            vaiTro=?
        WHERE id=?
    """, (
        hoTen,
        email,
        tenDangNhap,
        vaiTro,
        id
    ))

    conn.commit()
    conn.close()

    flash("Cập nhật thành công")

    return redirect("/admin/account")
from controllers.product_controller import *
# --- Trong file main.py ---

# 1. Trang danh sách sản phẩm
@app.route('/admin/products')
def route_admin_products():
    return product_manage() # Gọi hàm từ controller

# 2. Xử lý thêm sản phẩm
@app.route('/admin/product/add', methods=['POST'])
def route_add_product():
    return product_add_action()

# 3. Xử lý sửa sản phẩm
@app.route('/admin/product/edit/<int:p_id>', methods=['POST'])
def route_edit_product(p_id):
    return product_edit_action(p_id)

# 4. Ẩn/Hiện sản phẩm
@app.route('/admin/product/toggle/<int:p_id>/<int:status>')
def route_toggle_product(p_id, status):
    return product_toggle_action(p_id, status)

# 5. Xóa sản phẩm
@app.route('/admin/product/delete/<int:p_id>')
def route_delete_product(p_id):
    return product_delete_action(p_id)

# 6. Xem lịch sử
@app.route('/admin/product/history/<int:p_id>')
def route_product_history(p_id):
    return product_history_view(p_id)

@app.route("/admin/orders")
def route_admin_orders():
    if "user_id" not in session or session.get("vaiTro") != 1:
        return redirect("/auth")
    return list_orders()

# 2. Route phụ cho AJAX (Chỉ lấy phần chi tiết bên phải)
@app.route("/admin/order/detail-fragment/<int:order_id>")
def route_order_detail_fragment(order_id):
    if "user_id" not in session or session.get("vaiTro") != 1:
        return "Unauthorized", 401
    # Gọi hàm xử lý trả về HTML nhỏ từ Controller
    return order_detail_fragment(order_id)

# 3. Cập nhật trạng thái (Xử lý Form)
@app.route("/admin/order/update-status", methods=["POST"])
def route_update_status():
    if "user_id" not in session or session.get("vaiTro") != 1:
        return redirect("/auth")
    return update_status()

# 4. Xác nhận nhanh (Quick Ship)
@app.route("/admin/order/quick-ship/<int:order_id>")
def route_quick_ship(order_id):
    if "user_id" not in session or session.get("vaiTro") != 1:
        return redirect("/auth")
    return quick_ship(order_id)

from controllers.supplier_controller import list_suppliers, create_supplier

@app.route("/admin/suppliers")
def route_suppliers():
    return list_suppliers()

@app.route("/admin/supplier/add", methods=["POST"])
def route_add_supplier():
    return create_supplier()

from controllers.warehouse_controller import warehouse_page, warehouse_update_action

@app.route("/admin/warehouse")
def route_warehouse():
    return warehouse_page()

@app.route("/admin/warehouse/update", methods=["POST"])
def route_update_warehouse():
    return warehouse_update_action()
# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/auth")


if __name__ == "__main__":
    app.run(debug=True)