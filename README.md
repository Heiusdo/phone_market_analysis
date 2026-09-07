# Phân tích Thị trường Điện thoại Di động Việt Nam

Project phân tích dữ liệu end-to-end: crawl dữ liệu thật từ web, xử lý bằng Python, lưu trữ và truy vấn bằng MySQL, trực quan hóa bằng Power BI.

## Mục tiêu
Thu thập và phân tích dữ liệu giá, cấu hình, khuyến mãi của điện thoại di động đang bán tại thegioididong.com, nhằm tìm ra các insight về cơ cấu thị trường, định vị thương hiệu, và xu hướng giảm giá.

## Công nghệ sử dụng
- Python (requests, BeautifulSoup, pandas) — crawl và làm sạch dữ liệu
- MySQL — lưu trữ dữ liệu, viết truy vấn phân tích (GROUP BY, CASE WHEN, Window Function, Subquery)
- Power BI — xử lý dữ liệu (Power Query), xây dựng DAX measures, trực quan hóa dashboard

## Quy trình thực hiện
1. Thu thập dữ liệu: Crawl 107 sản phẩm điện thoại từ 8 hãng (Apple, Samsung, Xiaomi, OPPO, vivo, realme, Tecno, Nokia) — `crawl.py`
2. Làm sạch dữ liệu: Chuẩn hóa giá, tách RAM/dung lượng lưu trữ từ tên sản phẩm, xử lý missing data — `clean.py`
3. Lưu trữ và truy vấn: Tạo database MySQL, viết 8+ câu SQL phân tích — `create_database_and_queries.sql`
4. Trực quan hóa: Xây dựng 9 DAX measures và dashboard Power BI tương tác — `dax_measure.txt`, `phone_analysis_dashboard.pbix`

## Insight chính

- Cơ cấu phân khúc giá: Phân khúc 5-10 triệu chiếm tỷ trọng lớn nhất (32.71%), theo sau là 10-20 triệu (29.91%) — hai phân khúc tầm trung này chiếm tới 62.6% tổng thị trường.
- Định vị thương hiệu: Giá trung bình theo hãng phản ánh đúng định vị thị trường thực tế — Apple dẫn đầu về giá, trong khi Tecno và Nokia thuộc nhóm giá thấp nhất.
- Khuyến mãi: Trong số các sản phẩm đang giảm giá, tổng giá trị được giảm đạt 185.880.000đ (tổng giá gốc 1.451.860.000đ so với tổng giá bán 1.265.980.000đ). Xiaomi Redmi 17T Pro 5G là sản phẩm giảm sâu nhất được ghi nhận (23%, tương đương 5.680.000đ).

## Dashboard

## Dashboard

<p align="center">
  <img src="/images/phone_analysis_dashboard_page-0001.png" alt="Power BI Dashboard" width="80%">
</p>


## Cách chạy lại project
1. Chạy `crawl.py` để thu thập dữ liệu mới nhất
2. Chạy `clean.py` để làm sạch dữ liệu thô
3. Chạy các lệnh trong `create_database_and_queries.sql` để tạo database và import dữ liệu (nhớ sửa đường dẫn file CSV cho đúng máy bạn)
4. Mở `phone_analysis_dashboard.pbix` bằng Power BI Desktop, kết nối lại nguồn dữ liệu nếu cần

## Tác giả
Hieu — Data Analyst Portfolio Project
