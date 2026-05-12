from flask import render_template, request, redirect, flash
from models.supplier_model import *

def list_suppliers():
    suppliers = get_all_suppliers()
    return render_template("admin/suppliers.html", suppliers=suppliers)

def create_supplier():
    if request.method == "POST":
        data = {
            'ten': request.form.get("ten_ncc"),
            'nguoi_lh': request.form.get("nguoi_lh"),
            'sdt': request.form.get("sdt"),
            'email': request.form.get("email"),
            'dia_chi': request.form.get("dia_chi"),
            'danh_muc': request.form.get("danh_muc")
        }
        add_supplier(data)
        flash("Thêm nhà cung cấp thành công!", "success")
    return redirect("/admin/suppliers")