import os
from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from datetime import datetime
from models.product_model import *

# Cấu hình thư mục lưu ảnh
UPLOAD_FOLDER = 'static/uploads/products'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Tạo thư mục nếu chưa tồn tại
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --- 1. HIỂN THỊ DANH SÁCH & CẢNH BÁO ---
def product_manage():
    if "user_id" not in session or session.get("vaiTro") != 1:
        return redirect("/auth")

    keyword = request.args.get('keyword', '')
    category = request.args.get('category', '')

    # Lấy dữ liệu từ Model
    products = get_all_products_db(keyword, category)
    # Lấy các sản phẩm dưới ngưỡng (ví dụ: 5)
    low_stock_alerts = get_low_stock_alerts(threshold=5)

    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM danh_muc").fetchall()
    conn.close()

    return render_template("admin/products.html",
                           products=products,
                           categories=categories,
                           alerts=low_stock_alerts)


# --- 2. XỬ LÝ THÊM SẢN PHẨM (ẢNH & NGOẠI LỆ) ---
def product_add_action():
    if "user_id" not in session: return redirect("/auth")

    try:
        # Nhận dữ liệu form
        data = {
            'tenSanPham': request.form.get('tenSanPham').strip(),
            'gia': float(request.form.get('gia', 0)),
            'danhMucId': request.form.get('danhMucId'),
            'moTa': request.form.get('moTa'),
            'soLuong': int(request.form.get('soLuong', 0))
        }

        # Xử lý Upload Ảnh
        image_filename = None
        if 'hinhAnh' in request.files:
            file = request.files['hinhAnh']
            if file and allowed_file(file.filename):
                # Tạo tên file duy nhất: p_timestamp_name.jpg
                ext = file.filename.rsplit('.', 1)[1].lower()
                image_filename = f"p_{int(datetime.now().timestamp())}.{ext}"
                file.save(os.path.join(UPLOAD_FOLDER, image_filename))

        # Gọi Model (Đã có logic kiểm tra trùng tên bên trong)
        success, message = add_product_full(data, image_filename, session['user_id'])

        if success:
            flash(f"✅ {message}", "success")
        else:
            flash(f"❌ {message}", "error")

    except ValueError:
        flash("❌ Lỗi: Giá và số lượng phải là con số!", "error")
    except Exception as e:
        flash(f"❌ Lỗi hệ thống: {str(e)}", "error")

    return redirect(url_for('route_admin_products'))


# --- 3. XỬ LÝ CẬP NHẬT (ẢNH & LOG) ---
def product_edit_action(p_id):
    if "user_id" not in session: return redirect("/auth")

    try:
        data = {
            'tenSanPham': request.form.get('tenSanPham').strip(),
            'gia': float(request.form.get('gia')),
            'danhMucId': request.form.get('danhMucId'),
            'moTa': request.form.get('moTa')
        }

        # Kiểm tra nếu có upload ảnh mới
        image_filename = None
        if 'hinhAnh' in request.files:
            file = request.files['hinhAnh']
            if file and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                image_filename = f"upd_{p_id}_{int(datetime.now().timestamp())}.{ext}"
                file.save(os.path.join(UPLOAD_FOLDER, image_filename))

        success, message = update_product_full(p_id, data, image_filename, session['user_id'])

        if success:
            flash(f"✅ {message}", "success")
        else:
            flash(f"❌ {message}", "error")

    except Exception as e:
        flash(f"❌ Lỗi: {str(e)}", "error")

    return redirect(url_for('route_admin_products'))


# --- 4. XÓA & ẨN HIỆN & LỊCH SỬ ---
def product_delete_action(p_id):
    success, message = delete_product_db(p_id, session['user_id'])
    flash(f"✅ {message}" if success else f"❌ {message}")
    return redirect(url_for('route_admin_products'))


def product_toggle_action(p_id, status):
    if toggle_status_db(p_id, status, session['user_id']):
        flash("✅ Thay đổi trạng thái hiển thị thành công!")
    else:
        flash("❌ Lỗi khi cập nhật trạng thái.")
    return redirect(url_for('route_admin_products'))


def product_history_view(p_id):
    if "user_id" not in session: return redirect("/auth")

    logs = get_product_history(p_id)
    # Lấy tên sản phẩm để hiển thị tiêu đề
    conn = get_db_connection()
    p = conn.execute("SELECT tenSanPham FROM san_pham WHERE id=?", (p_id,)).fetchone()
    conn.close()

    return render_template("admin/product_history.html", logs=logs, product_name=p['tenSanPham'])


def product_manage():
    if "user_id" not in session or session.get("vaiTro") != 1:
        return redirect("/auth")

    # 1. Lấy các tham số lọc từ URL
    keyword = request.args.get('keyword', '')
    category_id = request.args.get('category', '')

    # 2. Lấy dữ liệu sản phẩm (Hàm này bạn đã có trong model)
    products = get_all_products_db(keyword, category_id)

    # 3. Lấy danh sách danh mục để hiện trong thanh Lọc
    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM danh_muc").fetchall()

    # 4. Lấy cảnh báo hết hàng (Sản phẩm có tồn kho <= 5)
    # Đảm bảo hàm này đã có IFNULL trong Model như mình đã sửa ở bước trước
    alerts = get_low_stock_alerts(threshold=5)

    # 5. Lấy toàn bộ nhật ký chỉnh sửa để hiện ở Tab Lịch sử
    # Nếu bạn chưa có hàm này, hãy thêm vào Model (xem mục 2 bên dưới)
    all_logs = get_all_logs_db()

    conn.close()

    # 6. Trả dữ liệu ra giao diện
    return render_template("admin/products.html",
                           products=products,
                           categories=categories,
                           alerts=alerts,
                           all_logs=all_logs)

def get_all_logs_db():
    conn = get_db_connection()
    # Lấy 50 hoạt động mới nhất liên quan đến sản phẩm
    sql = """
        SELECT n.*, u.hoTen 
        FROM nhat_ky_he_thong n
        JOIN nguoi_dung u ON n.nguoiDungId = u.id
        WHERE n.bang = 'san_pham'
        ORDER BY n.thoiGian DESC 
        LIMIT 50
    """
    data = conn.execute(sql).fetchall()
    conn.close()
    return data
