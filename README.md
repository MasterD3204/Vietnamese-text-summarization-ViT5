# Software Engineering Nhóm 32
## Thành viên
1. Đỗ Quang Dũng - 22022561
2. Đỗ Ngọc Anh - 22022577
3. Lê Trung Hiếu - 22022576
4. Nguyễn Lâm Tùng Bách - 22022640

## Đề tài: Xây dựng trang web tóm tắt văn bản
Report và demo sản phẩm: https://s.net.vn/UH7o

## Hướng dẫn cài đặt và sử dụng
### Cài đặt
- Cài đặt Tesseract (để trích xuất văn bản từ hình ảnh):

  - Link: https://github.com/tesseract-ocr/tesseract

  - Tải sau đó cài path tới Tesseract-OCR

  > (Tham khảo video hướng dẫn: https://www.youtube.com/watch?v=Tj-u1JDhpog - xem từ 1:00 -> 3:02)


  - Tải gói ngôn ngữ tiếng Việt để Tesseract đọc văn bản tiếng Việt từ hình ảnh tốt hơn:

    - Link: https://github.com/tesseract-ocr/tessdata/blob/main/vie.traineddata

    - Sau đó dán file mới tải vào Tesseract-OCR\tessdata


- Cài đặt các thư viện cần thiết trong file requirements.txt bằng câu lệnh:
  pip install -r requirements.txt

### Hướng dẫn sử dụng:
Đầu tiên chạy file app.py

Sau đó vào thư mục frontend, go live file index.html để sử dụng
