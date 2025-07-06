# UET Summarizer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Models-orange)](https://huggingface.co/models)

Một trang web giúp tóm tắt các đoạn văn bản tiếng Việt, được xây dựng dựa trên mô hình ngôn ngữ ViT5 đã được fine-tune trên dữ liệu tiếng Việt.

## Mục lục
1. [Giới thiệu](#giới-thiệu)
2. [Demo](#demo)
3. [Các tính năng chính](#các-tính-năng-chính)
4. [Công nghệ sử dụng](#công-nghệ-sử-dụng)
5. [Hướng dẫn cài đặt và sử dụng](#hướng-dẫn-cài-đặt-và-sử-dụng)
6. [Chi tiết về Mô hình](#chi-tiết-về-mô-hình-vit5-fine-tuned)
7. [Cấu trúc thư mục](#cấu-trúc-thư-mục)
8. [Hạn chế & Hướng phát triển](#hạn-chế--hướng-phát-triển)
9. [Đóng góp](#đóng-góp)
10. [Giấy phép](#giấy-phép)
11. [Liên hệ](#liên-hệ)

## Giới thiệu

**UET Summarizer** là một công cụ tóm tắt văn bản được thiết kế để giúp người dùng nhanh chóng nắm bắt những ý chính từ các tài liệu dài. Dự án sử dụng sức mạnh của mô hình Transformer **ViT5** (của VietAI) đã được fine-tune chuyên biệt cho nhiệm vụ tóm tắt văn bản tiếng Việt, mang lại kết quả cô đọng và có độ chính xác cao.

Mục tiêu của dự án là cung cấp một giao diện web thân thiện, cho phép bất kỳ ai cũng có thể dễ dàng tóm tắt văn bản mà không cần kiến thức kỹ thuật.

## Demo



## Các tính năng chính

*   **Tóm tắt văn bản:** Dán đoạn văn bản cần tóm tắt và nhận lại phiên bản rút gọn.
*   **Giao diện web trực quan:** Thiết kế đơn giản, tập trung vào trải nghiệm người dùng.
*   **Xử lý nhanh:** Cung cấp kết quả tóm tắt trong vài giây (tùy thuộc vào GPU).
*   **Tùy chỉnh độ dài:** Cho phép người dùng chọn độ dài mong muốn cho bản tóm tắt (ngắn, trung bình, dài).
*   **Tóm tắt từ file khác:** Có thể tải file pdf và word lên web, hệ thống sẽ tự động lấy nội dung để tóm tắt.
*   **Đánh giá:** kiểm tra xem văn bản tóm tắt giữ được bao nhiêu % nội dung gốc, độ dài đã giảm đi còn bao nhiêu

## Công nghệ sử dụng

Dự án được xây dựng với các công nghệ sau:

*   **Backend:**
    *   Ngôn ngữ: **Python 3.8+**
    *   Framework: **Flask**
*   **Frontend:**
    *   **HTML5, CSS3, JavaScript**
    *   Framework/Thư viện: **Vanilla JS**
*   **Mô hình AI/ML:**
    *   Mô hình nền: **ViT5** (`VietAI/vit5-base`)
    *   Thư viện: **Hugging Face Transformers**, **PyTorch**

## Hướng dẫn cài đặt và sử dụng

Để chạy dự án này trên máy của bạn, hãy làm theo các bước sau:

**1. Clone repository:**
```bash
git clone https://github.com/MasterD3204/Vietnamese-text-summarization-ViT5.git
```

**2. Cài đặt các thư viện cần thiết:**
```bash
pip install -r requirements.txt
```

**3. Chạy ứng dụng:**
```bash
python app.py

```
Sau đó vào file index.html và go live.

## Chi tiết về Mô hình (ViT5 Fine-tuned)

Đây là phần quan trọng nhất của dự án.

*   **Mô hình gốc (Base Model):** `[VietAI/vit5-base]`
*   **Dữ liệu Fine-tune:**
    *   **Tên bộ dữ liệu:** vietgpt/news_summarization_vi
    *   **Mô tả:** `Bộ dữ liệu này chứa các cặp bài báo và tóm tắt của chúng, được thu thập từ các trang tin tức uy tín tại Việt Nam.`
    *   **Link đến dữ liệu:** `https://huggingface.co/datasets/vietgpt/news_summarization_vi`
*   **Quá trình Huấn luyện:**
    *   **Framework:** PyTorch, Hugging Face Trainer
    *   **Hyperparameters:**
        *   Learning rate: `5e-5`
        *   Số epochs: `3`
        *   Batch size: `4`
        *   warmup_ratio: '0.05',
        *   weight_decay: '0.01',
*   **Đánh giá (Evaluation):**
    *   Mô hình được đánh giá trên tập test của bộ dữ liệu bằng chỉ số **ROUGE**.
    *   **ROUGE-1:** `76.19`
    *   **ROUGE-2:** `54.33`
    *   **ROUGE-L:** `56.18`

## Hạn chế & Hướng phát triển

### Hạn chế
*   Mô hình có thể hoạt động chưa tốt với các văn bản có lĩnh vực chuyên môn sâu (y tế, pháp luật) hoặc văn bản sáng tạo (thơ, truyện).
*   Giới hạn độ dài văn bản đầu vào để đảm bảo hiệu năng.
*   Chất lượng bản tóm tắt đôi khi có thể bị lặp từ, câu ở cuối có thể bị ngắt do giới hạn token.

### Hướng phát triển
*   Fine-tune mô hình trên một tập dữ liệu lớn và đa dạng hơn.
*   Cải thiện chất lượng và tốc độ đầu ra
*   Xây dựng API endpoint để các ứng dụng khác có thể sử dụng.
*   Cải thiện giao diện người dùng và thêm các tùy chọn nâng cao.


