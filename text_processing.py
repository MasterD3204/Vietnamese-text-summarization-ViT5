import re
from docx import Document
import fitz
import pytesseract
from PIL import Image
import io

def extract_text_from_pdf(pdf_file: str) -> str:
    """
    Extract text from a PDF file.
    """
    with fitz.open(pdf_file) as pdf:
        pdf_text = ""
        for page in pdf:
            pdf_text += page.get_text()
            
            # Xử lý hình ảnh nếu có
            for img in page.get_images(full=True):
                xref = img[0]
                base_image = pdf.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(io.BytesIO(image_bytes))
                
                # Sử dụng Tesseract để trích xuất văn bản từ hình ảnh
                pdf_text += pytesseract.image_to_string(image, lang='vie')
                
    return pdf_text

def extract_text_from_docx(docx_file: str) -> str:
    """
    Extract text from a .docx file.
    """
    doc = Document(docx_file)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
        
    # Xử lý hình ảnh nếu có
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            image = rel.target_part.blob
            image = Image.open(io.BytesIO(image))
            full_text.append(pytesseract.image_to_string(image, lang='vie'))
            
    return '\n'.join(full_text)

def preprocess_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    
    # Thêm khoảng trắng vào các vị trí bị dính chữ
    text = re.sub(r'([a-zA-Z])([A-Z])', r'\1 \2', text)  # Thêm khoảng trắng trước chữ hoa nếu liền kề chữ thường
    text = re.sub(r'([a-z])([A-Z][a-z])', r'\1 \2', text)  # Thêm khoảng trắng giữa chữ thường và chữ hoa đầu câu
    text = re.sub(r'([0-9])([a-zA-Z])', r'\1 \2', text)  # Thêm khoảng trắng giữa số và chữ cái
    text = re.sub(r'([a-zA-Z])([0-9])', r'\1 \2', text)  # Thêm khoảng trắng giữa chữ cái và số
    text = re.sub(r'(\d)([.,?!])', r'\1 \2', text)  # Thêm khoảng trắng giữa số và dấu chấm câu
    text = re.sub(r'([.,?!])(\w)', r'\1 \2', text)  # Thêm khoảng trắng sau dấu chấm câu
    
    # Thêm khoảng trắng giữa các từ bị dính vào nhau
    text = re.sub(r'([a-zA-Z])([A-Z])', r'\1 \2', text)  # Ví dụ: trí tuệ nhân tạo -> trí tuệ nhân tạo
    text = re.sub(r'([a-z])([A-Z][a-z])', r'\1 \2', text)
    
    # Xử lý các trường hợp dính chữ đặc biệt trong tiếng Việt
    text = re.sub(r'([a-zA-Z])([đĐ])', r'\1 \2', text)  # Thêm khoảng trắng trước "đ" hoặc "Đ" nếu liền kề chữ cái
    text = re.sub(r'([đĐ])([A-Z])', r'\1 \2', text)  # Thêm khoảng trắng sau "đ" hoặc "Đ" nếu liền kề chữ hoa
    text = re.sub(r'([A-Z])([đĐ])', r'\1 \2', text)  # Thêm khoảng trắng trước "đ" hoặc "Đ" nếu liền kề chữ hoa

    # Loại bỏ các ký tự đặc biệt không cần thiết
    text = re.sub(r'[^\w\s,.!?-]', '', text)
    
    # Loại bỏ các dòng trống
    text = '\n'.join([line for line in text.split('\n') if line.strip() != ''])
    
    return text
