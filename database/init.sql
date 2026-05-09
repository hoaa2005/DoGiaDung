-- =============================
-- RESET DATABASE
-- =============================
DROP TABLE IF EXISTS don_hang_giam_gia;
DROP TABLE IF EXISTS giam_gia;
DROP TABLE IF EXISTS nhat_ky_he_thong;
DROP TABLE IF EXISTS thanh_toan;
DROP TABLE IF EXISTS phuong_thuc_thanh_toan;
DROP TABLE IF EXISTS lich_su_trang_thai;
DROP TABLE IF EXISTS chi_tiet_don_hang;
DROP TABLE IF EXISTS don_hang;
DROP TABLE IF EXISTS chi_tiet_gio_hang;
DROP TABLE IF EXISTS gio_hang;
DROP TABLE IF EXISTS lich_su_kho;
DROP TABLE IF EXISTS ton_kho;
DROP TABLE IF EXISTS hinh_anh_san_pham;
DROP TABLE IF EXISTS san_pham;
DROP TABLE IF EXISTS danh_muc;
DROP TABLE IF EXISTS nha_cung_cap;
DROP TABLE IF EXISTS dia_chi;
DROP TABLE IF EXISTS nguoi_dung;

-- =============================
-- NGƯỜI DÙNG
-- =============================
CREATE TABLE nguoi_dung (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenDangNhap TEXT UNIQUE,
    matKhau TEXT,
    hoTen TEXT,
    email TEXT,
    soDienThoai TEXT,
    vaiTro INTEGER,         -- 1:QL, 2:NV, 3:KH
    trangThai INTEGER,
    ngayTao DATETIME
);

-- =============================
-- ĐỊA CHỈ
-- =============================
CREATE TABLE dia_chi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nguoiDungId INTEGER,
    diaChiCuThe TEXT,
    phuongXa TEXT,
    quanHuyen TEXT,
    tinhThanh TEXT,
    macDinh INTEGER,
    FOREIGN KEY (nguoiDungId) REFERENCES nguoi_dung(id)
);

-- =============================
-- DANH MỤC
-- =============================
CREATE TABLE danh_muc (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenDanhMuc TEXT,
    danhMucChaId INTEGER,
    FOREIGN KEY (danhMucChaId) REFERENCES danh_muc(id)
);

-- =============================
-- NHÀ CUNG CẤP
-- =============================
CREATE TABLE nha_cung_cap (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenNhaCungCap TEXT,
    soDienThoai TEXT,
    email TEXT,
    diaChi TEXT
);

-- =============================
-- SẢN PHẨM
-- =============================
CREATE TABLE san_pham (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenSanPham TEXT,
    moTa TEXT,
    gia REAL,
    danhMucId INTEGER,
    nhaCungCapId INTEGER,
    trangThai INTEGER,
    ngayTao DATETIME,
    FOREIGN KEY (danhMucId) REFERENCES danh_muc(id),
    FOREIGN KEY (nhaCungCapId) REFERENCES nha_cung_cap(id)
);

-- =============================
-- HÌNH ẢNH SẢN PHẨM
-- =============================
CREATE TABLE hinh_anh_san_pham (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sanPhamId INTEGER,
    duongDanAnh TEXT,
    FOREIGN KEY (sanPhamId) REFERENCES san_pham(id)
);

-- =============================
-- TỒN KHO
-- =============================
CREATE TABLE ton_kho (
    sanPhamId INTEGER PRIMARY KEY,
    soLuong INTEGER,
    ngayCapNhat DATETIME,
    FOREIGN KEY (sanPhamId) REFERENCES san_pham(id)
);

-- =============================
-- LỊCH SỬ KHO
-- =============================
CREATE TABLE lich_su_kho (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sanPhamId INTEGER,
    loai TEXT,              -- Nhập/Xuất
    soLuong INTEGER,
    ghiChu TEXT,
    nguoiThucHien INTEGER,
    ngayTao DATETIME,
    FOREIGN KEY (sanPhamId) REFERENCES san_pham(id),
    FOREIGN KEY (nguoiThucHien) REFERENCES nguoi_dung(id)
);

-- =============================
-- GIỎ HÀNG
-- =============================
CREATE TABLE gio_hang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nguoiDungId INTEGER,
    ngayTao DATETIME,
    FOREIGN KEY (nguoiDungId) REFERENCES nguoi_dung(id)
);

CREATE TABLE chi_tiet_gio_hang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gioHangId INTEGER,
    sanPhamId INTEGER,
    soLuong INTEGER,
    FOREIGN KEY (gioHangId) REFERENCES gio_hang(id),
    FOREIGN KEY (sanPhamId) REFERENCES san_pham(id)
);

-- =============================
-- ĐƠN HÀNG
-- =============================
CREATE TABLE don_hang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nguoiDungId INTEGER,
    diaChiId INTEGER,
    tongTien REAL,
    trangThai TEXT,
    ngayTao DATETIME,
    FOREIGN KEY (nguoiDungId) REFERENCES nguoi_dung(id),
    FOREIGN KEY (diaChiId) REFERENCES dia_chi(id)
);

CREATE TABLE chi_tiet_don_hang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    donHangId INTEGER,
    sanPhamId INTEGER,
    soLuong INTEGER,
    gia REAL,
    FOREIGN KEY (donHangId) REFERENCES don_hang(id),
    FOREIGN KEY (sanPhamId) REFERENCES san_pham(id)
);

-- =============================
-- LỊCH SỬ TRẠNG THÁI
-- =============================
CREATE TABLE lich_su_trang_thai (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    donHangId INTEGER,
    trangThai TEXT,
    nguoiCapNhat INTEGER,
    thoiGian DATETIME,
    FOREIGN KEY (donHangId) REFERENCES don_hang(id),
    FOREIGN KEY (nguoiCapNhat) REFERENCES nguoi_dung(id)
);

-- =============================
-- PHƯƠNG THỨC THANH TOÁN
-- =============================
CREATE TABLE phuong_thuc_thanh_toan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenPhuongThuc TEXT
);

-- =============================
-- THANH TOÁN
-- =============================
CREATE TABLE thanh_toan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    donHangId INTEGER,
    phuongThucId INTEGER,
    soTien REAL,
    trangThai TEXT,
    thoiGian DATETIME,
    FOREIGN KEY (donHangId) REFERENCES don_hang(id),
    FOREIGN KEY (phuongThucId) REFERENCES phuong_thuc_thanh_toan(id)
);

-- =============================
-- GIẢM GIÁ
-- =============================
CREATE TABLE giam_gia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    maCode TEXT,
    phanTram REAL,
    ngayHetHan DATETIME
);

CREATE TABLE don_hang_giam_gia (
    donHangId INTEGER,
    giamGiaId INTEGER,
    PRIMARY KEY (donHangId, giamGiaId),
    FOREIGN KEY (donHangId) REFERENCES don_hang(id),
    FOREIGN KEY (giamGiaId) REFERENCES giam_gia(id)
);

-- =============================
-- NHẬT KÝ HỆ THỐNG
-- =============================
CREATE TABLE nhat_ky_he_thong (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nguoiDungId INTEGER,
    hanhDong TEXT,
    bang TEXT,
    banGhiId INTEGER,
    thoiGian DATETIME,
    FOREIGN KEY (nguoiDungId) REFERENCES nguoi_dung(id)
);

-- =============================
-- DỮ LIỆU MẪU
-- =============================
INSERT INTO nguoi_dung
(tenDangNhap, matKhau, hoTen, vaiTro, trangThai, ngayTao)
VALUES ('admin@gmail.com','123','Admin',1,1,datetime('now'));

INSERT INTO danh_muc (tenDanhMuc) VALUES ('Đồ gia dụng');

INSERT INTO nha_cung_cap (tenNhaCungCap) VALUES ('NCC A');

INSERT INTO san_pham
(tenSanPham, gia, danhMucId, nhaCungCapId, trangThai, ngayTao)
VALUES ('Nồi cơm điện',500000,1,1,1,datetime('now'));