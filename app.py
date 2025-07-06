from flask import Flask, request, jsonify
from summary import Summarizer
from werkzeug.utils import secure_filename
import os
import mimetypes
from text_processing import preprocess_text, extract_text_from_docx, extract_text_from_pdf
from eval import Evaluate


app = Flask(__name__, static_folder='frontend')

# Thư mục lưu trữ tạm thời các tệp được tải lên
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Đảm bảo thư mục tồn tại
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/summary', methods=['POST'])
def summarize():
    data = request.json
    text = data['text']
    length = data.get('length')

    text = preprocess_text(text)  # Xử lý văn bản trước khi tóm tắt
    summarizer = Summarizer()
    summary = summarizer.summarize(text, length)
    
    # Tạo đối tượng Evaluate và tính toán các chỉ số
    evaluator = Evaluate()
    content_based_score = evaluator.content_based(summary, text)
    content_based_score = round(content_based_score * 100, 2)
    
    # Thống kê văn bản gốc và văn bản tóm tắt
    original_word_count = len(text.split())
    summary_word_count = len(summary.split())
    original_char_count = len(text)
    summary_char_count = len(summary)
    reduction = ((original_word_count - summary_word_count) / original_word_count) * 100

    return jsonify({
        'summary': summary,
        'statistics': {
            'original_word_count': original_word_count,
            'summary_word_count': summary_word_count,
            'original_char_count': original_char_count,
            'summary_char_count': summary_char_count,
            'reduction': reduction,
            'content_based_score': content_based_score
        }
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Kiểm tra định dạng của tệp và trích xuất văn bản tương ứng
        mime_type, _ = mimetypes.guess_type(filepath)
        if mime_type == 'application/pdf':
            text = extract_text_from_pdf(filepath)
        elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            text = extract_text_from_docx(filepath)
        else:
            os.remove(filepath)
            return jsonify({'error': 'Unsupported file type'})
        
        text = preprocess_text(text)
        
        # Xóa tệp sau khi xử lý để giải phóng dung lượng
        os.remove(filepath)
        
        # Trả về văn bản từ tệp đã xử lý
        return jsonify({'text': text})

if __name__ == '__main__':
    app.run(debug=True, port=5500, host='127.0.0.1')