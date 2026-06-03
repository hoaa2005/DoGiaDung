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

DROP TABLE IF EXISTS nha_cung_cap;

DROP TABLE IF EXISTS danh_muc;

DROP TABLE IF EXISTS dia_chi;

DROP TABLE IF EXISTS nguoi_dung;



-- =============================

-- NGƯỜI DÙNG

-- =============================

CREATE TABLE nguoi_dung (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    tenDangNhap TEXT UNIQUE NOT NULL,

    matKhau TEXT NOT NULL,

    hoTen TEXT NOT NULL,

    email TEXT UNIQUE NOT NULL,

    soDienThoai TEXT UNIQUE,

    vaiTro INTEGER NOT NULL DEFAULT 3,

    trangThai INTEGER NOT NULL DEFAULT 1,

    ngayTao DATETIME DEFAULT CURRENT_TIMESTAMP

);



-- =============================

-- ĐỊA CHỈ

-- =============================

CREATE TABLE dia_chi (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    nguoiDungId INTEGER NOT NULL,

    diaChiCuThe TEXT NOT NULL,

    phuongXa TEXT,

    quanHuyen TEXT,

    tinhThanh TEXT,

    macDinh INTEGER DEFAULT 0,



    FOREIGN KEY (nguoiDungId)

        REFERENCES nguoi_dung(id)

);



-- =============================

-- DANH MỤC

-- =============================

CREATE TABLE danh_muc (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    tenDanhMuc TEXT NOT NULL,

    danhMucChaId INTEGER,



    FOREIGN KEY (danhMucChaId)

        REFERENCES danh_muc(id)

);



-- =============================

-- NHÀ CUNG CẤP

-- =============================

CREATE TABLE nha_cung_cap (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    tenNhaCungCap TEXT NOT NULL,

    soDienThoai TEXT,

    email TEXT,

    diaChi TEXT

);



-- =============================

-- SẢN PHẨM

-- =============================

CREATE TABLE san_pham (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    tenSanPham TEXT NOT NULL,

    moTa TEXT,

    gia REAL NOT NULL,

    danhMucId INTEGER NOT NULL,

    nhaCungCapId INTEGER NOT NULL,

    trangThai INTEGER DEFAULT 1,

    ngayTao DATETIME DEFAULT CURRENT_TIMESTAMP,



    FOREIGN KEY (danhMucId)

        REFERENCES danh_muc(id),



    FOREIGN KEY (nhaCungCapId)

        REFERENCES nha_cung_cap(id)

);



-- =============================

-- HÌNH ẢNH SẢN PHẨM

-- =============================

CREATE TABLE hinh_anh_san_pham (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    sanPhamId INTEGER NOT NULL,

    duongDanAnh TEXT NOT NULL,



    FOREIGN KEY (sanPhamId)

        REFERENCES san_pham(id)

);



-- =============================

-- TỒN KHO

-- =============================

CREATE TABLE ton_kho (

    sanPhamId INTEGER PRIMARY KEY,

    soLuong INTEGER DEFAULT 0,

    ngayCapNhat DATETIME DEFAULT CURRENT_TIMESTAMP,



    FOREIGN KEY (sanPhamId)

        REFERENCES san_pham(id)

);



-- =============================

-- LỊCH SỬ KHO

-- =============================

CREATE TABLE lich_su_kho (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    sanPhamId INTEGER NOT NULL,

    loai TEXT NOT NULL,

    soLuong INTEGER NOT NULL,

    ghiChu TEXT,

    nguoiThucHien INTEGER,

    ngayTao DATETIME DEFAULT CURRENT_TIMESTAMP,



    FOREIGN KEY (sanPhamId)

        REFERENCES san_pham(id),



    FOREIGN KEY (nguoiThucHien)

        REFERENCES nguoi_dung(id)

);



-- =============================

-- GIỎ HÀNG

-- =============================

CREATE TABLE gio_hang (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    nguoiDungId INTEGER NOT NULL,

    ngayTao DATETIME DEFAULT CURRENT_TIMESTAMP,



    FOREIGN KEY (nguoiDungId)

        REFERENCES nguoi_dung(id)

);



-- =============================

-- CHI TIẾT GIỎ HÀNG

-- =============================

CREATE TABLE chi_tiet_gio_hang (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    gioHangId INTEGER NOT NULL,

    sanPhamId INTEGER NOT NULL,

    soLuong INTEGER NOT NULL,



    FOREIGN KEY (gioHangId)

        REFERENCES gio_hang(id),



    FOREIGN KEY (sanPhamId)

        REFERENCES san_pham(id)

);



-- =============================

-- ĐƠN HÀNG

-- =============================

CREATE TABLE don_hang (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    nguoiDungId INTEGER NOT NULL,

    diaChiId INTEGER NOT NULL,

    tongTien REAL DEFAULT 0,

    trangThai TEXT,

    ngayTao DATETIME DEFAULT CURRENT_TIMESTAMP,



    FOREIGN KEY (nguoiDungId)

        REFERENCES nguoi_dung(id),



    FOREIGN KEY (diaChiId)

        REFERENCES dia_chi(id)

);



-- =============================

-- CHI TIẾT ĐƠN HÀNG

-- =============================

CREATE TABLE chi_tiet_don_hang (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    donHangId INTEGER NOT NULL,

    sanPhamId INTEGER NOT NULL,

    soLuong INTEGER NOT NULL,

    gia REAL NOT NULL,



    FOREIGN KEY (donHangId)

        REFERENCES don_hang(id),



    FOREIGN KEY (sanPhamId)

        REFERENCES san_pham(id)

);



-- =============================

-- LỊCH SỬ TRẠNG THÁI

-- =============================

CREATE TABLE lich_su_trang_thai (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    donHangId INTEGER NOT NULL,

    trangThai TEXT NOT NULL,

    nguoiCapNhat INTEGER,

    thoiGian DATETIME DEFAULT CURRENT_TIMESTAMP,



    FOREIGN KEY (donHangId)

        REFERENCES don_hang(id),



    FOREIGN KEY (nguoiCapNhat)

        REFERENCES nguoi_dung(id)

);



-- =============================

-- PHƯƠNG THỨC THANH TOÁN

-- =============================

CREATE TABLE phuong_thuc_thanh_toan (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    tenPhuongThuc TEXT NOT NULL

);



-- =============================

-- THANH TOÁN

-- =============================

CREATE TABLE thanh_toan (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    donHangId INTEGER NOT NULL,

    phuongThucId INTEGER NOT NULL,

    soTien REAL NOT NULL,

    trangThai TEXT,

    thoiGian DATETIME DEFAULT CURRENT_TIMESTAMP,



    FOREIGN KEY (donHangId)

        REFERENCES don_hang(id),



    FOREIGN KEY (phuongThucId)

        REFERENCES phuong_thuc_thanh_toan(id)

);



-- =============================

-- GIẢM GIÁ

-- =============================

CREATE TABLE giam_gia (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    maCode TEXT UNIQUE NOT NULL,

    phanTram REAL NOT NULL,

    ngayHetHan DATETIME

);



-- =============================

-- ĐƠN HÀNG GIẢM GIÁ

-- =============================

CREATE TABLE don_hang_giam_gia (

    donHangId INTEGER,

    giamGiaId INTEGER,



    PRIMARY KEY (donHangId, giamGiaId),



    FOREIGN KEY (donHangId)

        REFERENCES don_hang(id),



    FOREIGN KEY (giamGiaId)

        REFERENCES giam_gia(id)

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

    thoiGian DATETIME DEFAULT CURRENT_TIMESTAMP,



    FOREIGN KEY (nguoiDungId)

        REFERENCES nguoi_dung(id)

);

CREATE TABLE voucher_nguoi_dung (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    nguoiDungId INTEGER NOT NULL,

    giamGiaId INTEGER NOT NULL,

    ngayLuu DATETIME DEFAULT CURRENT_TIMESTAMP,

    trangThai INTEGER DEFAULT 1, -- 1: Đã lưu/Chưa dùng, 0: Đã dùng

    FOREIGN KEY (nguoiDungId) REFERENCES nguoi_dung(id),

    FOREIGN KEY (giamGiaId) REFERENCES giam_gia(id)

);

-- =============================

-- DỮ LIỆU MẪU

-- =============================



INSERT INTO danh_muc (tenDanhMuc)

VALUES ('Đồ gia dụng');



INSERT INTO nha_cung_cap

(tenNhaCungCap, soDienThoai, email, diaChi)

VALUES

('NCC A', '0988888888', 'ncca@gmail.com', 'Hà Nội');



INSERT INTO san_pham

(

    tenSanPham,

    moTa,

    gia,

    danhMucId,

    nhaCungCapId,

    trangThai

)

VALUES

(

    'Nồi cơm điện',

    'Nồi cơm điện cao cấp',

    500000,

    1,

    1,

    1

);



-- =========================================

-- DỮ LIỆU MẪU HOÀN CHỈNH

-- =========================================



-- =========================================

-- NGƯỜI DÙNG

-- =========================================

INSERT INTO nguoi_dung

(

    tenDangNhap,

    matKhau,

    hoTen,

    email,

    soDienThoai,

    vaiTro,

    trangThai

)

VALUES



('admin','Admin@123','Quản trị viên','admin@gmail.com','0123456789',1,1),



('nhanvien1','NhanVien@123','Nguyễn Văn A','nva@gmail.com','0988888881',2,1),



('nhanvien2','NhanVien@123','Trần Thị B','ttb@gmail.com','0988888882',2,1),



('khach1','Khach@123','Lê Minh C','lmc@gmail.com','0988888883',3,1),



('khach2','Khach@123','Phạm D','pd@gmail.com','0988888884',3,1);





-- =========================================

-- ĐỊA CHỈ

-- =========================================

INSERT INTO dia_chi

(

    nguoiDungId,

    diaChiCuThe,

    phuongXa,

    quanHuyen,

    tinhThanh,

    macDinh

)

VALUES



(4,'12 Nguyễn Trãi','P1','Q1','TP.HCM',1),



(5,'45 Lê Lợi','P2','Q3','TP.HCM',1);





-- =========================================

-- DANH MỤC

-- =========================================

INSERT INTO danh_muc

(tenDanhMuc)

VALUES



('Nồi cơm điện'),

('Chảo chống dính'),

('Dao nhà bếp'),

('Máy xay sinh tố'),

('Ấm siêu tốc'),

('Lò vi sóng'),

('Bếp điện'),

('Hộp bảo quản'),

('Ly cốc'),

('Dụng cụ làm bánh');





-- =========================================

-- NHÀ CUNG CẤP

-- =========================================

INSERT INTO nha_cung_cap

(

    tenNhaCungCap,

    soDienThoai,

    email,

    diaChi

)

VALUES



('Sunhouse','0900000001','sunhouse@gmail.com','Hà Nội'),



('Lock&Lock','0900000002','lock@gmail.com','TP.HCM'),



('Philips','0900000003','philips@gmail.com','Đà Nẵng'),



('Sharp','0900000004','sharp@gmail.com','Hải Phòng');





-- =========================================

-- SẢN PHẨM

-- =========================================

INSERT INTO san_pham

(

    tenSanPham,

    moTa,

    gia,

    danhMucId,

    nhaCungCapId,

    trangThai

)

VALUES



('Nồi cơm điện Sharp KS19','Nồi cơm điện cao cấp',890000,1,4,1),



('Chảo chống dính Lock&Lock','Chảo phủ đá hoa cương',450000,2,2,1),



('Dao bếp Nhật','Dao inox siêu bén',250000,3,2,1),



('Máy xay Philips','Máy xay đa năng',1200000,4,3,1),



('Ấm siêu tốc Sunhouse','Dung tích 2L',350000,5,1,1),



('Lò vi sóng Sharp','Lò vi sóng inverter',2400000,6,4,1),



('Bếp điện đôi','Bếp điện cảm ứng',3200000,7,1,1),



('Hộp thủy tinh','Hộp bảo quản thực phẩm',180000,8,2,1),



('Bộ ly thủy tinh','6 ly cao cấp',290000,9,2,1),



('Máy đánh trứng','Dụng cụ làm bánh',650000,10,3,1);





-- =========================================

-- HÌNH ẢNH SẢN PHẨM

-- =========================================

INSERT INTO hinh_anh_san_pham

(

    sanPhamId,

    duongDanAnh

)

VALUES



(1,'noicom.jpg'),

(2,'chao.jpg'),

(3,'dao.jpg'),

(4,'mayxay.jpg'),

(5,'amsieutoc.jpg'),

(6,'lovisong.jpg'),

(7,'bepdien.jpg'),

(8,'hopthuytinh.jpg'),

(9,'lythuytinh.jpg'),

(10,'maydanhtrung.jpg');





-- =========================================

-- TỒN KHO

-- =========================================

INSERT INTO ton_kho

(

    sanPhamId,

    soLuong

)

VALUES



(1,20),

(2,35),

(3,50),

(4,15),

(5,40),

(6,12),

(7,8),

(8,60),

(9,30),

(10,18);





-- =========================================

-- LỊCH SỬ KHO

-- =========================================

INSERT INTO lich_su_kho

(

    sanPhamId,

    loai,

    soLuong,

    ghiChu,

    nguoiThucHien

)

VALUES



(1,'Nhập',20,'Nhập kho đầu tháng',2),



(2,'Nhập',35,'Nhập kho đầu tháng',2),



(3,'Xuất',5,'Bán hàng',2);





-- =========================================

-- GIỎ HÀNG

-- =========================================

INSERT INTO gio_hang

(

    nguoiDungId

)

VALUES



(4),

(5);





-- =========================================

-- CHI TIẾT GIỎ HÀNG

-- =========================================

INSERT INTO chi_tiet_gio_hang

(

    gioHangId,

    sanPhamId,

    soLuong

)

VALUES



(1,1,1),



(1,2,2),



(2,4,1);





-- =========================================

-- ĐƠN HÀNG

-- =========================================

INSERT INTO don_hang

(

    nguoiDungId,

    diaChiId,

    tongTien,

    trangThai

)

VALUES



(4,1,1790000,'Đang giao'),



(5,2,1200000,'Hoàn thành');





-- =========================================

-- CHI TIẾT ĐƠN HÀNG

-- =========================================

INSERT INTO chi_tiet_don_hang

(

    donHangId,

    sanPhamId,

    soLuong,

    gia

)

VALUES



(1,1,1,890000),



(1,2,2,450000),



(2,4,1,1200000);





-- =========================================

-- LỊCH SỬ TRẠNG THÁI

-- =========================================

INSERT INTO lich_su_trang_thai

(

    donHangId,

    trangThai,

    nguoiCapNhat

)

VALUES



(1,'Đang giao',1),



(2,'Hoàn thành',1);





-- =========================================

-- PHƯƠNG THỨC THANH TOÁN

-- =========================================

INSERT INTO phuong_thuc_thanh_toan

(

    tenPhuongThuc

)

VALUES



('COD'),



('Chuyển khoản'),



('Ví Momo');





-- =========================================

-- THANH TOÁN

-- =========================================

INSERT INTO thanh_toan

(

    donHangId,

    phuongThucId,

    soTien,

    trangThai

)

VALUES



(1,1,1790000,'Chưa thanh toán'),



(2,2,1200000,'Đã thanh toán');





-- =========================================

-- GIẢM GIÁ

-- =========================================

INSERT INTO giam_gia

(

    maCode,

    phanTram,

    ngayHetHan

)

VALUES



('SALE10',10,'2026-12-31'),



('SALE20',20,'2026-12-31');





-- =========================================

-- ĐƠN HÀNG GIẢM GIÁ

-- =========================================

INSERT INTO don_hang_giam_gia

(

    donHangId,

    giamGiaId

)

VALUES



(1,1),



(2,2);





-- =========================================

-- NHẬT KÝ HỆ THỐNG

-- =========================================

INSERT INTO nhat_ky_he_thong

(

    nguoiDungId,

    hanhDong,

    bang,

    banGhiId

)

VALUES



(1,'THÊM','san_pham',1),



(1,'SỬA','don_hang',2),



(2,'XÓA','gio_hang',1);



-- =========================================

-- BỔ SUNG DỮ LIỆU MẪU MỞ RỘNG

-- =========================================



-- 1. THÊM NGƯỜI DÙNG (Khách hàng & Nhân viên mới)

INSERT INTO nguoi_dung (tenDangNhap, matKhau, hoTen, email, soDienThoai, vaiTro, trangThai)

VALUES

('nhanvien3', 'NhanVien@123', 'Lý Hoàng Nam', 'namlh@gmail.com', '0988888885', 2, 1),

('khach3', 'Khach@123', 'Đặng Thu Thảo', 'thao.dang@gmail.com', '0912345670', 3, 1),

('khach4', 'Khach@123', 'Hoàng Gia Bảo', 'baogia@gmail.com', '0912345671', 3, 1),

('khach5', 'Khach@123', 'Vũ Tuyết Mai', 'maivt@gmail.com', '0912345672', 3, 0); -- Tài khoản bị khóa



-- 2. THÊM ĐỊA CHỈ CHO KHÁCH HÀNG MỚI

INSERT INTO dia_chi (nguoiDungId, diaChiCuThe, phuongXa, quanHuyen, tinhThanh, macDinh)

VALUES

(6, '789 Đường 3/2', 'P10', 'Q10', 'TP.HCM', 1),

(7, '101 Cầu Giấy', 'P.Dịch Vọng', 'Q.Cầu Giấy', 'Hà Nội', 1),

(8, '22 Ngô Quyền', 'P.Thọ Quang', 'Q.Sơn Trà', 'Đà Nẵng', 1),

(9, '56 Trần Hưng Đạo', 'P.An Phú', 'Q.Ninh Kiều', 'Cần Thơ', 1);



-- 3. THÊM DANH MỤC CON (Danh mục cấp 2)

INSERT INTO danh_muc (tenDanhMuc, danhMucChaId)

VALUES

('Nồi cơm điện tử', 1),

('Bếp từ đơn', 7),

('Bếp từ đôi', 7);



-- 4. THÊM SẢN PHẨM MỚI (Đa dạng mức giá và trạng thái)

INSERT INTO san_pham (tenSanPham, moTa, gia, danhMucId, nhaCungCapId, trangThai)

VALUES

('Nồi cơm Tiger JNP-1800', 'Nồi cơm điện Nhật Bản 1.8L', 3500000, 1, 4, 1),

('Chảo Tefal Excellence', 'Chảo chống dính 28cm', 950000, 2, 2, 1),

('Bộ dao 7 món Lock&Lock', 'Thép không gỉ cao cấp', 1550000, 3, 2, 1),

('Máy xay sinh tố cầm tay Braun', 'Công suất 1000W', 2100000, 4, 3, 1),

('Ấm siêu tốc Philips HD9306', 'Inox 304 bền bỉ', 680000, 5, 3, 1),

('Lò nướng Sanaky 50L', 'Điều khiển cơ, có quạt đối lưu', 1850000, 6, 1, 1),

('Bếp từ đơn Sunhouse SHD6149', 'Mặt kính chịu nhiệt', 750000, 12, 1, 1),

('Bộ 3 hộp thủy tinh chia ngăn', 'Dùng được lò vi sóng', 320000, 8, 2, 1),

('Máy vắt cam Sharp', 'Nhựa BPA Free', 450000, 4, 4, 1),

('Nồi áp suất điện Philips', 'Đa năng, dung tích 6L', 2800000, 1, 3, 1);



-- 5. THÊM TỒN KHO CHO SẢN PHẨM MỚI (Có vài mẫu sắp hết hàng)

INSERT INTO ton_kho (sanPhamId, soLuong)

VALUES

(11, 5),   -- Cảnh báo: Sắp hết hàng

(12, 25),

(13, 10),

(14, 0),   -- Cảnh báo: Hết hàng

(15, 30),

(16, 8),

(17, 15),

(18, 100),

(19, 12),

(20, 3);   -- Cảnh báo: Sắp hết hàng



-- 6. THÊM ĐƠN HÀNG MỚI (Nhiều trạng thái khác nhau)

INSERT INTO don_hang (nguoiDungId, diaChiId, tongTien, trangThai)

VALUES

(6, 3, 3500000, 'Chờ xác nhận'),

(7, 4, 1630000, 'Đã hủy'),

(8, 5, 320000, 'Hoàn thành'),

(4, 1, 2100000, 'Đang chuẩn bị');



-- 7. CHI TIẾT ĐƠN HÀNG MỚI

INSERT INTO chi_tiet_don_hang (donHangId, sanPhamId, soLuong, gia)

VALUES

(3, 11, 1, 3500000), -- Đơn 3

(4, 12, 1, 950000),  -- Đơn 4

(4, 15, 1, 680000),  -- Đơn 4

(5, 18, 1, 320000),  -- Đơn 5

(6, 14, 1, 2100000); -- Đơn 6



-- 8. CẬP NHẬT THANH TOÁN

INSERT INTO thanh_toan (donHangId, phuongThucId, soTien, trangThai)

VALUES

(3, 2, 3500000, 'Đã thanh toán'),

(4, 1, 1630000, 'Đã hoàn tiền'),

(5, 3, 320000, 'Đã thanh toán'),

(6, 2, 2100000, 'Đã thanh toán');



-- 9. NHẬT KÝ HỆ THỐNG (Mô phỏng thao tác của Admin và Nhân viên)

INSERT INTO nhat_ky_he_thong (nguoiDungId, hanhDong, bang, banGhiId)

VALUES

(1, 'SỬA', 'nguoi_dung', 9),

(2, 'THÊM', 'san_pham', 11),

(2, 'THÊM', 'san_pham', 12),

(3, 'CẬP NHẬT KHO', 'ton_kho', 11),

(1, 'XÓA', 'hinh_anh_san_pham', 5),

(2, 'DUYỆT ĐƠN', 'don_hang', 3),

(3, 'HỦY ĐƠN', 'don_hang', 4);



-- 10. MÃ GIẢM GIÁ MỚI

INSERT INTO giam_gia (maCode, phanTram, ngayHetHan)

VALUES

('HELLO2026', 15, '2026-02-01'),

('WOMENDAY', 8, '2026-03-10'),

('FREESHIP', 5, '2026-12-31');