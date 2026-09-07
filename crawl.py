"""
Script crawl dữ liệu điện thoại từ thegioididong.com
------------------------------------------------------
Cách chạy:
    python crawl_dienthoai.py

Script này lấy dữ liệu trực tiếp từ các thuộc tính data-*
(data-name, data-price, data-brand...) gắn sẵn trên thẻ
<a class="main-contain"> của mỗi sản phẩm — đây là cách lấy
dữ liệu chuẩn xác nhất vì không cần suy luận/tách chuỗi text.

Lưu ý: trang chủ /dtdd chỉ hiển thị một số sản phẩm ban đầu,
phần còn lại tải thêm khi bấm nút "Xem thêm" (qua JavaScript/AJAX).
Bản này crawl các sản phẩm có sẵn trong HTML gốc; nếu muốn lấy
toàn bộ danh mục, ta sẽ cần thêm bước gọi API ẩn đằng sau nút
"Xem thêm" — sẽ hướng dẫn riêng nếu bạn cần.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Danh sách các trang danh mục theo hãng cần crawl.
# Bạn có thể vào thegioididong.com/dtdd, xem menu bên trái các hãng,
# rồi bấm vào từng hãng để lấy đúng URL và bổ sung/bớt vào danh sách này.
CATEGORY_URLS = [
    "https://www.thegioididong.com/dtdd-apple-iphone",
    "https://www.thegioididong.com/dtdd-samsung",
    "https://www.thegioididong.com/dtdd-xiaomi",
    "https://www.thegioididong.com/dtdd-oppo",
    "https://www.thegioididong.com/dtdd-vivo",
    "https://www.thegioididong.com/dtdd-realme",
    "https://www.thegioididong.com/dtdd-tecno",
    "https://www.thegioididong.com/dtdd-nokia",
]

# Header giả lập trình duyệt thật để tránh bị chặn
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def crawl_page(url):
    """Gửi request và trả về đối tượng BeautifulSoup của trang."""
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()  # báo lỗi nếu request thất bại
    return BeautifulSoup(response.text, "html.parser")


def parse_products(soup):
    """Tách dữ liệu từng sản phẩm ra khỏi trang HTML.

    Trang thegioididong.com gắn sẵn dữ liệu vào các thuộc tính
    data-* trên thẻ <a class="main-contain">, nên ta lấy trực tiếp
    từ đó thay vì phải mò text hiển thị (đáng tin cậy hơn nhiều).
    """
    products = []

    items = soup.select("a.main-contain")

    for item in items:
        try:
            product_id = item.get("data-id")
            name = item.get("data-name")
            price = item.get("data-price")       # dạng số, vd "34590000.0"
            brand = item.get("data-brand")
            category = item.get("data-cate")
            color = item.get("data-color")

            # Giá cũ (trước giảm giá) và % giảm, nếu có
            old_price_tag = item.select_one("p.price-old")
            old_price = old_price_tag.get_text(strip=True) if old_price_tag else None

            percent_tag = item.select_one("span.percent")
            discount_percent = percent_tag.get_text(strip=True) if percent_tag else None

            if name:  # chỉ lưu nếu lấy được tên sản phẩm
                products.append({
                    "product_id": product_id,
                    "product_name": name,
                    "price": price,
                    "old_price_text": old_price,
                    "discount_percent": discount_percent,
                    "brand": brand,
                    "category": category,
                    "color": color,
                })
        except Exception as e:
            print(f"Lỗi khi xử lý 1 sản phẩm: {e}")
            continue

    return products


def main():
    all_products = []
    seen_ids = set()  # để loại bỏ sản phẩm trùng (VD: 1 máy xuất hiện ở 2 trang)

    for url in CATEGORY_URLS:
        print(f"Đang tải trang: {url}")
        try:
            soup = crawl_page(url)
            products = parse_products(soup)

            new_count = 0
            for p in products:
                if p["product_id"] not in seen_ids:
                    seen_ids.add(p["product_id"])
                    all_products.append(p)
                    new_count += 1

            print(f"  -> Lấy được {len(products)} sản phẩm ({new_count} sản phẩm mới).")

        except Exception as e:
            print(f"  -> Lỗi khi crawl {url}: {e}")

        time.sleep(2)  # nghỉ 2 giây giữa các request để lịch sự với server

    print(f"\nTổng cộng crawl được {len(all_products)} sản phẩm (đã loại trùng).")

    # Lưu ra file CSV thô (chưa xử lý) để bước sau làm sạch
    df = pd.DataFrame(all_products)
    df.to_csv("dienthoai_raw.csv", index=False, encoding="utf-8-sig")
    print("Đã lưu vào file: dienthoai_raw.csv")


if __name__ == "__main__":
    main()