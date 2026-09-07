"""
Script làm sạch dữ liệu điện thoại (dienthoai_raw.csv -> dienthoai_clean.csv)
------------------------------------------------------------------------------
Cách chạy:
    python clean_dienthoai.py

Yêu cầu: file dienthoai_raw.csv nằm cùng thư mục với script này.
"""

import pandas as pd
import re

INPUT_FILE = "dienthoai_raw.csv"
OUTPUT_FILE = "dienthoai_clean.csv"


def clean_price(value):
    """Chuyển giá dạng số (có thể là chuỗi '34590000.0') thành số nguyên VNĐ."""
    if pd.isna(value):
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def clean_old_price(text):
    """Chuyển '37.990.000₫' thành số nguyên 37990000."""
    if pd.isna(text):
        return None
    digits = re.sub(r"[^\d]", "", str(text))  # bỏ hết ký tự không phải số
    return int(digits) if digits else None


def clean_discount_percent(text):
    """Chuyển '-8%' thành số 8 (giá trị dương, đơn vị %)."""
    if pd.isna(text):
        return 0
    digits = re.sub(r"[^\d]", "", str(text))
    return int(digits) if digits else 0


def extract_ram_storage_gb(name):
    """Tách RAM và dung lượng lưu trữ (ROM) từ tên sản phẩm.

    Xử lý 2 trường hợp:
    - Chỉ có 1 số kèm GB/TB (VD: 'iPhone 17 Pro Max 256GB')
      -> đây là dung lượng lưu trữ, RAM = None (Apple không công bố RAM).
    - Có 2 số kèm GB/TB (VD: 'Samsung Galaxy A16 8GB/128GB')
      -> số đầu là RAM, số sau là dung lượng lưu trữ.
    - Không có số nào (VD: điện thoại phổ thông không công bố)
      -> cả 2 đều None, đây là missing data hợp lệ (không phải lỗi).

    Trả về tuple (ram_gb, storage_gb).
    """
    if pd.isna(name):
        return None, None

    matches = re.findall(r"(\d+)\s*(GB|TB)", name, re.IGNORECASE)
    if not matches:
        return None, None

    # Quy đổi TB -> GB để đồng nhất đơn vị
    values = [int(num) * 1024 if unit.upper() == "TB" else int(num) for num, unit in matches]

    if len(values) >= 2:
        return values[0], values[1]   # RAM, storage
    else:
        return None, values[0]        # chỉ có storage


def clean_product_name(name):
    """Bỏ dung lượng khỏi tên để có 'tên dòng máy' gọn hơn, dùng để nhóm sản phẩm.
    VD: 'iPhone 17 Pro Max 256GB' -> 'iPhone 17 Pro Max'
        'Samsung Galaxy A07 4GB/64GB' -> 'Samsung Galaxy A07'
    """
    if pd.isna(name):
        return name
    # Xóa cụm "<số>GB" hoặc "<số>TB", kèm theo dấu "/" ngay sau nếu có
    # (dấu / dùng để ngăn cách RAM/ROM, VD "4GB/64GB")
    cleaned = re.sub(r"\s*\d+\s*(?:GB|TB)/?", "", name, flags=re.IGNORECASE)
    # Dọn thêm khoảng trắng/dấu "/" còn sót lại ở đầu hoặc cuối chuỗi
    return cleaned.strip(" /")


def main():
    df = pd.read_csv(INPUT_FILE)
    print(f"Đọc {len(df)} dòng từ {INPUT_FILE}")

    # 1. Loại bỏ dòng trùng lặp hoàn toàn (nếu có)
    before = len(df)
    df = df.drop_duplicates(subset=["product_id"])
    print(f"Loại {before - len(df)} dòng trùng product_id")

    # 2. Loại bỏ dòng thiếu tên hoặc giá (dữ liệu không dùng được)
    before = len(df)
    df = df.dropna(subset=["product_name", "price"])
    print(f"Loại {before - len(df)} dòng thiếu tên hoặc giá")

    # 3. Chuẩn hóa các cột số
    df["price"] = df["price"].apply(clean_price)
    df["old_price"] = df["old_price_text"].apply(clean_old_price)
    df["discount_percent"] = df["discount_percent"].apply(clean_discount_percent)

    # Nếu không có giá cũ (không giảm giá), giá cũ = giá hiện tại
    df["old_price"] = df["old_price"].fillna(df["price"])

    # 4. Tách RAM và dung lượng lưu trữ từ tên sản phẩm
    ram_storage = df["product_name"].apply(extract_ram_storage_gb)
    df["ram_gb"] = ram_storage.apply(lambda x: x[0])
    df["storage_gb"] = ram_storage.apply(lambda x: x[1])

    # Ép sang kiểu Int64 (chữ I hoa) của pandas thay vì int/float thường.
    # Đây là kiểu "nullable integer" - vẫn giữ số nguyên (4, không phải 4.0)
    # NGAY CẢ KHI cột có chứa giá trị thiếu (NaN) ở dòng khác.
    df["ram_gb"] = df["ram_gb"].astype("Int64")
    df["storage_gb"] = df["storage_gb"].astype("Int64")

    # 5. Tạo cột "tên dòng máy" gọn hơn (bỏ dung lượng), hữu ích để nhóm/so sánh
    df["model_name"] = df["product_name"].apply(clean_product_name)

    # 6. Sắp xếp lại thứ tự cột cho gọn gàng
    df = df[[
        "product_id", "brand", "model_name", "product_name",
        "ram_gb", "storage_gb", "color", "category",
        "price", "old_price", "discount_percent",
    ]]

    # 7. Sắp xếp theo hãng rồi theo giá
    df = df.sort_values(by=["brand", "price"]).reset_index(drop=True)

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print(f"\nĐã lưu {len(df)} dòng dữ liệu sạch vào: {OUTPUT_FILE}")
    print("\n5 dòng đầu tiên:")
    print(df.head())


if __name__ == "__main__":
    main()