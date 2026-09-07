-- =========================================================
-- Bước 1: Tạo database riêng cho project
-- =========================================================
CREATE DATABASE IF NOT EXISTS phone_analysis
    CHARACTER SET utf8mb4      -- utf8mb4 để lưu đúng tiếng Việt có dấu
    COLLATE utf8mb4_unicode_ci;

USE phone_analysis;

-- =========================================================
-- Bước 2: Tạo bảng chứa dữ liệu điện thoại
-- Kiểu dữ liệu được chọn khớp với dữ liệu đã làm sạch ở bước trước
-- =========================================================
CREATE TABLE IF NOT EXISTS phones (
    product_id        INT PRIMARY KEY,        -- mã sản phẩm, không trùng -> làm khóa chính
    brand             VARCHAR(50)  NOT NULL,   -- tên hãng
    model_name        VARCHAR(150) NOT NULL,   -- tên dòng máy (đã bỏ dung lượng)
    product_name      VARCHAR(200) NOT NULL,   -- tên đầy đủ gốc
    ram_gb            INT NULL,                -- RAM (GB), NULL nếu không rõ
    storage_gb        INT NULL,                -- Dung lượng lưu trữ (GB), NULL nếu không rõ
    color             VARCHAR(50),
    category          VARCHAR(50),
    price             INT NOT NULL,            -- giá hiện tại (VNĐ)
    old_price         INT NOT NULL,            -- giá trước giảm (VNĐ)
    discount_percent  INT DEFAULT 0            -- % giảm giá
);

-- Kiểm tra bảng đã tạo đúng cấu trúc chưa
DESCRIBE phones;

-- ---------------------------------------------------------
-- Q1. Giá trung bình, thấp nhất, cao nhất theo từng hãng
-- Kỹ thuật: GROUP BY, hàm tổng hợp (AVG, MIN, MAX, COUNT)
-- ---------------------------------------------------------
SELECT
    brand,
    COUNT(*)                    AS so_luong_san_pham,
    ROUND(AVG(price), 0)        AS gia_trung_binh,
    MIN(price)                  AS gia_thap_nhat,
    MAX(price)                  AS gia_cao_nhat
FROM phones
GROUP BY brand
ORDER BY gia_trung_binh DESC;



-- ---------------------------------------------------------
-- Q2. Top 10 sản phẩm đang giảm giá sâu nhất
-- Kỹ thuật: ORDER BY, LIMIT
-- ---------------------------------------------------------
SELECT
    brand,
    product_name,
    price,
    old_price,
    discount_percent
FROM phones
WHERE discount_percent > 0
ORDER BY discount_percent DESC
LIMIT 10;

-- ---------------------------------------------------------
-- Q3. Phân khúc giá: đếm số lượng sản phẩm mỗi phân khúc
-- Kỹ thuật: CASE WHEN để tạo nhóm tùy chỉnh, GROUP BY theo nhóm đó
-- ---------------------------------------------------------
SELECT
    CASE
        WHEN price < 5000000                      THEN '1. Dưới 5 triệu'
        WHEN price BETWEEN 5000000 AND 10000000    THEN '2. 5-10 triệu'
        WHEN price BETWEEN 10000001 AND 20000000   THEN '3. 10-20 triệu'
        ELSE '4. Trên 20 triệu'
    END AS phan_khuc_gia,
    COUNT(*)                AS so_luong,
    ROUND(AVG(price), 0)    AS gia_trung_binh_phan_khuc
FROM phones
GROUP BY phan_khuc_gia
ORDER BY phan_khuc_gia;

-- ---------------------------------------------------------
-- Q4. Hãng nào tập trung nhiều máy cấu hình cao (RAM >= 8GB)?
-- Kỹ thuật: WHERE lọc trước, GROUP BY, HAVING lọc sau khi gộp nhóm
-- ---------------------------------------------------------
SELECT
    brand,
    COUNT(*) AS so_may_ram_cao
FROM phones
WHERE ram_gb >= 8
GROUP BY brand
HAVING COUNT(*) >= 2          -- chỉ hiện hãng có từ 2 máy trở lên
ORDER BY so_may_ram_cao DESC;

-- ---------------------------------------------------------
-- Q5. Xếp hạng sản phẩm theo giá TRONG TỪNG HÃNG
-- Kỹ thuật: Window function RANK() OVER (PARTITION BY ... ORDER BY ...)
-- Đây là kỹ thuật SQL nâng cao rất hay được hỏi khi phỏng vấn
-- ---------------------------------------------------------
SELECT
    brand,
    product_name,
    price,
    RANK() OVER (PARTITION BY brand ORDER BY price DESC) AS xep_hang_trong_hang
FROM phones
ORDER BY brand, xep_hang_trong_hang;

-- ---------------------------------------------------------
-- Q6. So sánh giá từng sản phẩm với giá trung bình CỦA CHÍNH HÃNG ĐÓ
-- Kỹ thuật: Window function AVG() OVER (PARTITION BY ...)
-- Giúp biết sản phẩm nào đắt/rẻ hơn mặt bằng chung của hãng
-- ---------------------------------------------------------
SELECT
    brand,
    product_name,
    price,
    ROUND(AVG(price) OVER (PARTITION BY brand), 0) AS gia_tb_cua_hang,
    price - ROUND(AVG(price) OVER (PARTITION BY brand), 0) AS chenh_lech
FROM phones
ORDER BY brand, chenh_lech DESC;

-- ---------------------------------------------------------
-- Q7. Những sản phẩm có giá cao hơn giá trung bình TOÀN BỘ dữ liệu
-- Kỹ thuật: Subquery (truy vấn con) trong mệnh đề WHERE
-- ---------------------------------------------------------
SELECT
    brand,
    product_name,
    price
FROM phones
WHERE price > (SELECT AVG(price) FROM phones)
ORDER BY brand, price DESC;

-- ---------------------------------------------------------
-- Q8. Dung lượng lưu trữ nào đang được bán phổ biến nhất?
-- Kỹ thuật: GROUP BY trên cột có thể NULL, xử lý NULL bằng COALESCE
-- ---------------------------------------------------------
SELECT
    COALESCE(CONCAT(storage_gb, 'GB'), 'Không rõ') AS dung_luong,
    COUNT(*) AS so_luong
FROM phones
GROUP BY storage_gb
ORDER BY so_luong DESC;