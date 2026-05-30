import os
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)
from datetime import datetime

# Import các hàm nghiệp vụ từ Model
from models.product_model import (
    get_all_products_db,
    get_low_stock_alerts,
    get_categories_with_count_db,
    get_filtered_products_db,
    get_all_logs_db,
    add_product_full,
    update_product_full,
    delete_product_db,
    toggle_status_db,
    get_product_history,
    get_db_connection
)

# Cấu hình thư mục lưu trữ ảnh sản phẩm
UPLOAD_FOLDER = "static/uploads/products"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# ===============================================================================
# [USER CLIENT] LOGIC TRANG SẢN PHẨM PHÍA KHÁCH HÀNG
# ===============================================================================
def user_products_index():
    category_id = request.args.get("category", "").strip()
    sort_option = request.args.get("sort", "newest").strip()
    search_query = request.args.get("search", "").strip()

    categories = get_categories_with_count_db()
    total_count = sum(cat["soLuongSp"] for cat in categories)

    products = get_filtered_products_db(
        category_id=category_id,
        sort_option=sort_option,
        search_query=search_query
    )

    return render_template(
        "products.html",
        categories=categories,
        products=products,
        total_count=total_count,
        current_cat=category_id,
        current_sort=sort_option,
        search_query=search_query
    )


# ===============================================================================
# [ADMIN] LOGIC TRANG QUẢN LÝ DANH SÁCH SẢN PHẨM
# ===============================================================================
def product_manage():
    if "user_id" not in session:
        return redirect("/auth")
    if session.get("vaiTro") != 1:
        return redirect("/")

    keyword = request.args.get("keyword", "").strip()
    category = request.args.get("category", "").strip()

    products = get_all_products_db(keyword, category)
    alerts = get_low_stock_alerts(5)
    categories = get_categories_with_count_db()
    all_logs = get_all_logs_db()

    return render_template(
        "admin/products.html",
        products=products,
        categories=categories,
        alerts=alerts,
        all_logs=all_logs
    )


# ===============================================================================
# [ADMIN] LOGIC XỬ LÝ HÀNH ĐỘNG THÊM SẢN PHẨM
# ===============================================================================
def product_add_action():
    if "user_id" not in session:
        return redirect("/auth")
    if session.get("vaiTro") != 1:
        return redirect("/")

    try:
        tenSanPham = request.form.get("tenSanPham", "").strip()
        gia = request.form.get("gia", "0").strip()
        danhMucId = request.form.get("danhMucId")
        moTa = request.form.get("moTa", "").strip()
        soLuong = request.form.get("soLuong", "0").strip()

        # Validate dữ liệu đầu vào cơ bản
        if tenSanPham == "":
            flash("Tên sản phẩm không được để trống")
            return redirect(url_for("route_admin_products"))

        try:
            gia = float(gia)
            if gia <= 0: raise ValueError
        except ValueError:
            flash("Giá sản phẩm phải là số và lớn hơn 0")
            return redirect(url_for("route_admin_products"))

        try:
            soLuong = int(soLuong)
            if soLuong < 0: raise ValueError
        except ValueError:
            flash("Số lượng hàng trong kho không được âm")
            return redirect(url_for("route_admin_products"))

        data = {
            "tenSanPham": tenSanPham,
            "gia": gia,
            "danhMucId": danhMucId,
            "moTa": moTa,
            "soLuong": soLuong
        }

        # Xử lý tệp hình ảnh tải lên
        image_filename = None
        if "hinhAnh" in request.files:
            file = request.files["hinhAnh"]
            if file.filename != "":
                if not allowed_file(file.filename):
                    flash("Ảnh không đúng định dạng cho phép (png, jpg, jpeg, webp)")
                    return redirect(url_for("route_admin_products"))

                ext = file.filename.rsplit(".", 1)[1].lower()
                image_filename = f"product_{int(datetime.now().timestamp())}.{ext}"
                file.save(os.path.join(UPLOAD_FOLDER, image_filename))

        # Gọi Model lưu dữ liệu
        success, message = add_product_full(data, image_filename, session["user_id"])
        flash(message)

    except Exception as e:
        flash(f"Lỗi hệ thống: {str(e)}")

    return redirect(url_for("route_admin_products"))


# ===============================================================================
# [ADMIN] LOGIC XỬ LÝ HÀNH ĐỘNG CẬP NHẬT/CHỈNH SỬA SẢN PHẨM
# ===============================================================================
def product_edit_action(p_id):
    if "user_id" not in session:
        return redirect("/auth")
    if session.get("vaiTro") != 1:
        return redirect("/")

    try:
        tenSanPham = request.form.get("tenSanPham", "").strip()
        gia = request.form.get("gia", "0").strip()
        danhMucId = request.form.get("danhMucId")
        moTa = request.form.get("moTa", "").strip()
        soLuong = request.form.get("soLuong", "0").strip()

        if tenSanPham == "":
            flash("Tên sản phẩm không được để trống")
            return redirect(url_for("route_admin_products"))

        try:
            gia = float(gia)
            if gia <= 0: raise ValueError
        except ValueError:
            flash("Giá sản phẩm phải lớn hơn 0")
            return redirect(url_for("route_admin_products"))

        try:
            soLuong = int(soLuong)
            if soLuong < 0: raise ValueError
        except ValueError:
            flash("Số lượng không được âm")
            return redirect(url_for("route_admin_products"))

        data = {
            "tenSanPham": tenSanPham,
            "gia": gia,
            "danhMucId": danhMucId,
            "moTa": moTa,
            "soLuong": soLuong
        }

        # Xử lý tệp hình ảnh khi chỉnh sửa
        image_filename = None
        if "hinhAnh" in request.files:
            file = request.files["hinhAnh"]
            if file.filename != "":
                if not allowed_file(file.filename):
                    flash("Ảnh cập nhật không đúng định dạng")
                    return redirect(url_for("route_admin_products"))

                ext = file.filename.rsplit(".", 1)[1].lower()
                image_filename = f"update_{p_id}_{int(datetime.now().timestamp())}.{ext}"
                file.save(os.path.join(UPLOAD_FOLDER, image_filename))

        # Lưu thông tin (Nếu image_filename=None, model tự động giữ nguyên ảnh cũ)
        success, message = update_product_full(p_id, data, image_filename, session["user_id"])
        flash(message)

    except Exception as e:
        flash(f"Lỗi hệ thống: {str(e)}")

    return redirect(url_for("route_admin_products"))


# ===============================================================================
# [ADMIN] LOGIC XỬ LÝ HÀNH ĐỘNG XÓA SẢN PHẨM
# ===============================================================================
def product_delete_action(p_id):
    if "user_id" not in session:
        return redirect("/auth")
    if session.get("vaiTro") != 1:
        return redirect("/")

    success, message = delete_product_db(p_id, session["user_id"])
    flash(message)
    return redirect(url_for("route_admin_products"))


# ===============================================================================
# [ADMIN] LOGIC XỬ LÝ HÀNH ĐỘNG ẨN / HIỆN SẢN PHẨM KHỎI WEBSITE
# ===============================================================================
def product_toggle_action(p_id, status):
    if "user_id" not in session:
        return redirect("/auth")
    if session.get("vaiTro") != 1:
        return redirect("/")

    try:
        success = toggle_status_db(p_id, status, session["user_id"])
        if success:
            flash("Đã hiển thị sản phẩm ra cửa hàng" if status == 1 else "Đã ẩn sản phẩm thành công")
        else:
            flash("Cập nhật trạng thái hiển thị thất bại")
    except Exception as e:
        flash(f"Lỗi hệ thống: {str(e)}")

    return redirect(url_for("route_admin_products"))


# ===============================================================================
# [ADMIN] LOGIC XEM LỊCH SỬ THAY ĐỔI
# ===============================================================================
def product_history_view(p_id):
    if "user_id" not in session:
        return redirect("/auth")
    if session.get("vaiTro") != 1:
        return redirect("/")

    logs = get_product_history(p_id)

    conn = get_db_connection()
    product = conn.execute("SELECT tenSanPham FROM san_pham WHERE id = ?", (p_id,)).fetchone()
    conn.close()

    if not product:
        flash("Sản phẩm này không tồn tại trên hệ thống")
        return redirect(url_for("route_admin_products"))

    return render_template(
        "admin/product_history.html",
        logs=logs,
        product_name=product["tenSanPham"]
    )