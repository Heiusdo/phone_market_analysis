-- =========================================================
-- Import dữ liệu bằng LOAD DATA LOCAL INFILE
-- Cách này tránh được bug encoding UTF-8 của Table Data Import Wizard
-- ⚠️ SỬA đường dẫn bên dưới cho đúng với vị trí file trên máy bạn
-- Dùng dấu '/' xuôi, ví dụ: 'C:/Users/YourName/Desktop/dienthoai_clean.csv'
-- =========================================================

USE phone_analysis;

-- Xóa dữ liệu cũ trong bảng (nếu có, để tránh trùng lặp do import lỗi trước đó)
TRUNCATE TABLE phones;

LOAD DATA LOCAL INFILE 'C:/Users/Admin/Documents/NEW_JOURNEY/dienthoai_clean.csv'
INTO TABLE phones
CHARACTER SET utf8mb4          -- ép đúng bảng mã UTF-8, không để MySQL tự đoán
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'     -- một số ô có thể được bao trong dấu ngoặc kép
LINES TERMINATED BY '\n'
IGNORE 1 LINES                 -- bỏ qua dòng tiêu đề (header) của CSV
(
    product_id,
    brand,
    model_name,
    product_name,
    @ram_gb,                   -- dùng biến tạm vì cột này có thể rỗng
    @storage_gb,
    color,
    category,
    price,
    old_price,
    discount_percent
)
SET
    ram_gb     = NULLIF(@ram_gb, ''),      -- nếu ô rỗng, lưu NULL thay vì lỗi
    storage_gb = NULLIF(@storage_gb, '');

-- Kiểm tra kết quả
SELECT COUNT(*) AS total_rows FROM phones;
SELECT * FROM phones LIMIT 10;

SHOW VARIABLES LIKE 'local_infile';
SET GLOBAL local_infile = 1