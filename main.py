from flask import Flask, render_template, session, redirect, request, flash
import sqlite3

# Import các bộ điều khiển (Controllers)
from controllers.auth_controller import login, register
from controllers.account_controller import *
from controllers.product_controller import *
from controllers.orders_controller import *
from controllers.supplier_controller import list_suppliers, create_supplier
from controllers.warehouse_controller import warehouse_page, warehouse_update_action

# Import các mô hình dữ liệu (Models)
from models.dashboard_model import *
from models.user_model import *
# Trong file main.py:

app = Flask(__name__)
app.secret_key = "abc123"

DB_PATH = "database/database.db"


# ===============================================================================
# AUTHENTICATION ROUTES
# ===============================================================================
@app.route("/auth")
def auth():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_route():
    return login()


@app.route("/register", methods=["POST"])
def register_route():
    return register()


# --- ROUTE ĐĂNG XUẤT (Quan trọng: Phải gọi hàm logout đã sửa) ---
@app.route("/logout")
def logout():
    return auth_ctrl.logout()
# ===============================================================================
# USER CLIENT ROUTES
# ===============================================================================

@app.route("/")
def home():
    # Nếu đã đăng nhập admin thì chuyển hướng sang trang quản trị
    if "user_id" in session and session["vaiTro"] == 1:
        return redirect("/admin")

    # KẾT NỐI DB: Lấy sản phẩm và ép buộc lấy HÌNH ẢNH MỚI NHẤT (ID lớn nhất) của sản phẩm đó
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    query = """
        SELECT 
            sp.*, 
            dm.tenDanhMuc, 
            ha.duongDanAnh
        FROM san_pham sp
        LEFT JOIN danh_muc dm ON sp.danhMucId = dm.id
        LEFT JOIN (
            /* Đoạn subquery này giúp lấy chính xác ảnh có ID lớn nhất (ảnh mới cập nhật) của từng sản phẩm */
            SELECT sanPhamId, duongDanAnh 
            FROM hinh_anh_san_pham 
            WHERE id IN (SELECT MAX(id) FROM hinh_anh_san_pham GROUP BY sanPhamId)
        ) ha ON sp.id = ha.sanPhamId
        WHERE sp.trangThai = 1
        ORDER BY sp.id DESC
    """

    products_list = conn.execute(query).fetchall()
    conn.close()

    # Truyền dữ liệu chuẩn ra trang chủ
    return render_template("home.html", products=products_list)


#==========================user
# --- Đảm bảo đã import đầy đủ ---
import controllers.order_user_controller as user_cart_ctrl
import controllers.auth_controller as auth_ctrl



# --- ROUTE GIỎ HÀNG & THANH TOÁN ---

# Trang giỏ hàng
@app.route("/cart", endpoint="cart_page")
def cart_page():
    return user_cart_ctrl.cart_page_controller()

# Thêm vào giỏ (Nút "Giỏ hàng" ở trang chủ/sản phẩm)
@app.route("/cart/add/<int:p_id>", methods=["GET"])
def add_to_cart(p_id):
    return user_cart_ctrl.add_to_cart_controller(p_id)

# Mua ngay (Nút "Mua ngay" ở trang chủ/sản phẩm)
@app.route("/cart/buy-now/<int:p_id>", methods=["GET"])
def buy_now(p_id):
    return user_cart_ctrl.buy_now_controller(p_id)

# Tăng giảm số lượng (Nút + - trong giỏ)
@app.route("/cart/update/<int:p_id>", methods=["POST"])
def update_cart(p_id):
    return user_cart_ctrl.update_cart_controller(p_id)

# Xóa sản phẩm khỏi giỏ
@app.route("/cart/delete/<int:p_id>")
def delete_item(p_id):
    return user_cart_ctrl.delete_cart_item_controller(p_id)

# Xác nhận đặt hàng
@app.route("/cart/checkout", methods=["POST"])
def checkout():
    return user_cart_ctrl.checkout_process_controller()


import controllers.promotion_controller as promo_ctrl

# --- ROUTE TRANG KHUYẾN MÃI ---
@app.route("/promotions")
def promotions():
    return promo_ctrl.promotion_page_controller()

# --- ROUTE LƯU MÃ GIẢM GIÁ ---
@app.route("/promotion/save/<string:maCode>", methods=["POST"])
def save_voucher(maCode):
    return promo_ctrl.save_voucher_controller(maCode)

# --- ROUTE HỦY MÃ (Nếu muốn hủy mã đã chọn) ---
@app.route("/remove-voucher")
def remove_voucher():
    session.pop("applied_voucher", None)
    flash("Đã hủy mã giảm giá.")
    return redirect("/cart")
# ===============================================================================
# ADMIN: DASHBOARD
# ===============================================================================
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


# ===============================================================================
# ADMIN: TÀI KHOẢN & NGƯỜI DÙNG (ACCOUNTS)
# ===============================================================================
@app.route("/admin/users")
def admin_users():
    if "user_id" not in session:
        return redirect("/auth")
    if session["vaiTro"] != 1:
        return redirect("/")

    users = get_all_users()
    return render_template("admin/account.html", users=users)


@app.route("/admin/account")
def admin_account():
    if "user_id" not in session:
        return redirect("/auth")
    if session["vaiTro"] != 1:
        return redirect("/")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    users = conn.execute("SELECT * FROM nguoi_dung ORDER BY id DESC").fetchall()
    conn.close()

    return render_template("admin/account.html", users=users)


@app.route("/admin/user/add", methods=["POST"])
def admin_add_user():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO nguoi_dung (tenDangNhap, matKhau, hoTen, email, vaiTro, trangThai)
        VALUES (?, ?, ?, ?, ?, 1)
    """, (
        request.form["tenDangNhap"],
        request.form["matKhau"],
        request.form["hoTen"],
        request.form["email"],
        request.form["vaiTro"]
    ))
    conn.commit()
    conn.close()
    flash("Thêm tài khoản thành công")
    return redirect("/admin/users")


@app.route("/admin/user/edit/<int:id>", methods=["POST"])
def admin_edit_user(id):
    hoTen = request.form.get("hoTen")
    email = request.form.get("email")
    tenDangNhap = request.form.get("tenDangNhap")
    vaiTro = request.form.get("vaiTro")
    matKhau = request.form.get("matKhau")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if matKhau != "":
        cursor.execute("""
            UPDATE nguoi_dung 
            SET hoTen = ?, email = ?, tenDangNhap = ?, vaiTro = ?, matKhau = ? 
            WHERE id = ?
        """, (hoTen, email, tenDangNhap, vaiTro, matKhau, id))
    else:
        cursor.execute("""
            UPDATE nguoi_dung 
            SET hoTen = ?, email = ?, tenDangNhap = ?, vaiTro = ? 
            WHERE id = ?
        """, (hoTen, email, tenDangNhap, vaiTro, id))

    conn.commit()
    conn.close()
    flash("Cập nhật tài khoản thành công")
    return redirect("/admin/users")


@app.route("/admin/user/delete/<int:user_id>")
def admin_delete_user(user_id):
    if "user_id" not in session: return redirect("/auth")
    if session["vaiTro"] != 1: return redirect("/")
    if user_id == session["user_id"]:
        flash("Không thể xóa chính mình")
        return redirect("/admin/users")

    delete_user(user_id)
    flash("Xóa tài khoản thành công")
    return redirect("/admin/users")


@app.route("/admin/user/lock/<int:user_id>")
def admin_lock_user(user_id):
    if "user_id" not in session: return redirect("/auth")
    if session["vaiTro"] != 1: return redirect("/")
    if user_id == session["user_id"]:
        flash("Không thể khóa chính mình")
        return redirect("/admin/users")

    lock_user(user_id)
    flash("Đã khóa tài khoản")
    return redirect("/admin/users")


@app.route("/admin/user/unlock/<int:user_id>")
def admin_unlock_user(user_id):
    if "user_id" not in session: return redirect("/auth")
    if session["vaiTro"] != 1: return redirect("/")

    unlock_user(user_id)
    flash("Đã mở khóa tài khoản")
    return redirect("/admin/users")


# ===============================================================================
# ADMIN: SẢN PHẨM (PRODUCTS)
# ===============================================================================
# ===============================================================================
# IMPORT CÁC HÀM XỬ LÝ TỪ CONTROLLER CHUNG
# ===============================================================================
# ===============================================================================
# [ROUTE] TRANG SẢN PHẨM PHÍA KHÁCH HÀNG (USER CLIENT)
# ===============================================================================
@app.route("/products", endpoint="route_user_products")
def route_user_products():
    return user_products_index()


# ===============================================================================
# [ROUTE] PHỤC VỤ TRANG QUẢN TRỊ (ADMIN) - ĐÃ ĐỒNG BỘ NÚT BẤM
# ===============================================================================

# 1. Trang danh sách quản lý sản phẩm (Giao diện chính Admin)
@app.route("/admin/products", endpoint="route_admin_products")
def route_admin_products_manage():
    return product_manage()

# 2. Xử lý hành động thêm sản phẩm mới
@app.route("/admin/products/add", methods=["POST"], endpoint="route_add_product")
def route_admin_products_add():
    return product_add_action()

# 3. Xử lý hành động chỉnh sửa sản phẩm (Nhận p_id)
@app.route("/admin/products/edit/<int:p_id>", methods=["POST"], endpoint="route_edit_product")
def route_admin_products_edit(p_id):
    return product_edit_action(p_id)

# 4. Xử lý hành động xóa sản phẩm (Nhận p_id)
@app.route("/admin/products/delete/<int:p_id>", methods=["POST", "GET"], endpoint="route_delete_product")
def route_admin_products_delete(p_id):
    return product_delete_action(p_id)

# 5. Xử lý hành động Ẩn/Hiện nhanh sản phẩm (Nhận p_id và status)
@app.route("/admin/products/toggle/<int:p_id>/<int:status>", methods=["POST", "GET"], endpoint="route_toggle_product")
def route_admin_products_toggle(p_id, status):
    return product_toggle_action(p_id, status)

# 6. Xem lịch sử thay đổi của sản phẩm (Nhận p_id)
@app.route("/admin/products/history/<int:p_id>", endpoint="route_history_product")
def route_admin_products_history(p_id):
    return product_history_view(p_id)
# ===============================================================================
# ADMIN: ĐƠN HÀNG (ORDERS) - Đã đồng bộ với Sidebar chi tiết mới
# ===============================================================================
@app.route('/admin/orders')
def route_admin_orders():
    return orders_manage()


@app.route('/admin/order/detail-fragment/<int:order_id>')
def route_order_detail_fragment(order_id):
    return order_detail_fragment(order_id)


@app.route('/admin/order/update-status/<int:order_id>', methods=['POST'])
def route_update_order_status(order_id):
    status = request.form.get("trangThai")
    user_id = session.get("user_id")

    # Gọi hàm từ orders_model.py của bạn
    success, message = update_order_status_db(order_id, status, user_id)

    if success:
        flash("Cập nhật trạng thái đơn hàng thành công! ✨")
    else:
        flash(f"Thất bại: {message}")

    return redirect('/admin/orders')
# ===============================================================================
# ADMIN: NHÀ CUNG CẤP & KHO HÀNG (SUPPLIERS & WAREHOUSE)
# ===============================================================================
# Import đầy đủ 4 hàm điều hướng nghiệp vụ từ Controller
from controllers.supplier_controller import (
    list_suppliers,
    create_supplier,
    edit_supplier_action,
    delete_supplier_action
)

# 1. Route hiển thị danh sách toàn bộ đối tác Nhà cung cấp
@app.route("/admin/suppliers")
def route_suppliers():
    return list_suppliers()

# 2. Route tiếp nhận Form thêm mới đối tác (Phương thức POST)
@app.route("/admin/supplier/add", methods=["POST"])
def route_add_supplier():
    return create_supplier()

# 3. Route tiếp nhận Form chỉnh sửa thông tin đối tác (Phương thức POST)
@app.route("/admin/supplier/edit/<int:id>", methods=["POST"])
def route_edit_supplier(id):
    return edit_supplier_action(id)

# 4. Route thực thi hành động xóa đối tác ra khỏi hệ thống (Phương thức GET)
@app.route("/admin/supplier/delete/<int:id>")
def route_delete_supplier(id):
    return delete_supplier_action(id)
#==============================================

@app.route("/admin/warehouse")
def route_warehouse():
    return warehouse_page()


@app.route("/admin/warehouse/update", methods=["POST"])
def route_update_warehouse():
    return warehouse_update_action()


# ===============================================================================
# RUN APPLICATION
# ===============================================================================
if __name__ == "__main__":
    app.run(debug=True)