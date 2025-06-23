# Tiki Product Crawler

## Giới thiệu

Script `crawl_TIKI.py` giúp tự động thu thập thông tin chi tiết sản phẩm từ website Tiki.vn thông qua API, lưu dữ liệu thành từng batch dưới dạng file JSON, đồng thời quản lý trạng thái các sản phẩm đã crawl để tránh trùng lặp.

## Tính năng chính
- Đọc danh sách product_id từ file CSV (ví dụ: `ids_part1.csv`).
- Gửi request song song (đa luồng) tới API của Tiki để lấy thông tin sản phẩm.
- Lưu dữ liệu sản phẩm thành từng batch (mỗi batch 1000 sản phẩm) dưới dạng file JSON (`data_tiki_batch_X.json`).
- Ghi log quá trình crawl vào file `crawl_tiki.log`.
- Lưu trạng thái các product_id đã crawl vào file `crawled_ids.txt` (dùng pickle) để tránh crawl lại.
- Làm sạch dữ liệu mô tả sản phẩm (loại bỏ HTML).
- Tự động tiếp tục crawl từ batch tiếp theo nếu đã có dữ liệu trước đó.

## Yêu cầu
- Python 3.x
- Các thư viện: `requests`, `beautifulsoup4`,`time`,`logging`,`requests`,`HTTPError`,`json`,`re`,`os`,`pickle`,`ThreadPoolExecutor`

Cài đặt thư viện:
```bash
pip install -r requirements.txt
```

## Hướng dẫn sử dụng
1. Chuẩn bị file chứa danh sách product_id (mỗi dòng 1 id), ví dụ: `ids_part1.csv`.
2. Chạy script:
```bash
python crawl_TIKI.py
```
3. Dữ liệu sẽ được lưu thành các file `data_tiki_batch_X.json` (mỗi file chứa tối đa 1000 sản phẩm).
4. Log quá trình crawl xem tại file `crawl_tiki.log`.

## Cấu trúc file/dự án
- `crawl_TIKI.py`: Script chính để crawl dữ liệu.
- `ids_part1.csv`, ...: File chứa danh sách product_id.
- `data_tiki_batch_X.json`: File kết quả từng batch.
- `crawled_ids.txt`: File lưu trạng thái các id đã crawl (dạng pickle).
- `crawl_tiki.log`: File log quá trình crawl.

## Lưu ý
- Script hỗ trợ tiếp tục crawl nếu bị dừng giữa chừng (dựa vào `crawled_ids.txt`).
- Có thể chỉnh sửa số lượng sản phẩm mỗi batch bằng cách thay đổi biến `batch_size` trong code.