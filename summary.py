import re
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
from nltk import sent_tokenize
from collections import defaultdict


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
from nltk import sent_tokenize
from collections import defaultdict
class Summarizer:
    def __init__(self, model_path: str = r"D:\Text-Summary-main\Model"):
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path).to(device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model.eval()
        
        # Cấu hình độ dài tóm tắt
        self.length_settings = {
            "short": {
                "max_sentences": 3,
                "max_tokens": 100,
                "min_tokens": 50,
                "target_length": "3-4 câu"
            },
            "medium": {
                "max_sentences": 5,
                "max_tokens": 150,
                "min_tokens": 80,
                "target_length": "5-6 câu"
            },
            "long": {
                "max_sentences": 7,
                "max_tokens": 200,
                "min_tokens": 120,
                "target_length": "7-8 câu"
            }
        }
        self.meta_pattern = re.compile(
            r'\b(số\s*liệu|văn\s*phong|tóm\s*tắt|yêu\s*cầu|quan\s*trọng|câu|lưu\s*ý|độ\s*dài|tập\s*trung|giữ\s*lại|thông\s*tin|phong\s*cách|hãy|bài\s*viết|khóa\s*chính)\b|[\d-]+\s*câu',
            re.IGNORECASE
        )

    def summarize(self, clean_text, length_option = "medium"):
        """Tóm tắt văn bản với cơ chế lọc meta-content mạnh mẽ"""
      
        # Bước 1: Phân tích ngữ cảnh
        context = self._analyze_context(clean_text)
        
        # Bước 2: Tạo prompt an toàn
        prompt = self._build_safe_prompt(clean_text, context, length_option)
        
        # Bước 3: Tạo tóm tắt
        summary = self._generate_summary(prompt, length_option)
        final_summary = self._post_process_summary(summary, clean_text)
        return final_summary

    def _analyze_context(self, text):
        """Phân tích văn bản để xác định thông tin quan trọng"""
        sentences = sent_tokenize(text)
        
        context = {
            'key_phrases': [],
            'proper_nouns': set(),
            'numbers': set(),
            'topic_shifts': [],
            'important_keywords': self._extract_keywords(sentences),
            'key_sentences': self._find_key_sentences(sentences)
        }
        
        for sent in sentences:
            # Phát hiện tên riêng (viết hoa chữ cái đầu)
            context['proper_nouns'].update(re.findall(r'\b[A-Z][a-zà-ỹ]+\b', sent))
            
            # Phát hiện số liệu
            context['numbers'].update(re.findall(r'\b\d+[\.,]?\d*\b', sent))
            
            # Trích xuất cụm từ quan trọng
            if len(sent.split()) > 5:
                keywords = [w for w in sent.split() 
                          if w.lower() not in self._get_stopwords()]
                context['key_phrases'].extend(keywords[:3])
        
        # Phát hiện chuyển đổi chủ đề
        for i in range(1, len(sentences)):
            prev_words = set(sentences[i-1].lower().split())
            curr_words = set(sentences[i].lower().split())
            if len(prev_words & curr_words) <= 2 and len(sentences[i].split()) > 5:
                context['topic_shifts'].append(i)
        
        return context

    def _build_safe_prompt(self, text, context, length_option):
        """Xây dựng prompt an toàn không chứa meta-instructions"""
        config = self.length_settings[length_option]
        
        # Chuẩn bị thông tin quan trọng
        keywords = ", ".join(context['important_keywords'][:3]) if context['important_keywords'] else ""
        entities = ", ".join(list(context['proper_nouns'])[:2]) if context['proper_nouns'] else ""
        numbers = ", ".join(list(context['numbers'])[:2]) if context['numbers'] else ""

        return f"""
        {text[:2000]} </s>
        Tóm tắt văn bản trên với độ dài {config['target_length']}. Ưu tiên giữ các thông tin liên quan đến: {keywords}, {entities}, {numbers}. Có đủ mở đầu và kết thúc rõ ràng.
"""


    def _generate_summary(self, prompt, length_option):
        """Tạo tóm tắt với cơ chế bảo vệ"""
        config = self.length_settings[length_option]
        
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=1024,
            truncation=True
        ).to(device)
        
        outputs = self.model.generate(
            inputs.input_ids,
            max_length=config["max_tokens"],
            min_length=config["min_tokens"],
            num_beams=5,
            length_penalty=1.5,
            no_repeat_ngram_size=3,
            early_stopping=True,
            do_sample=True,
            top_p=0.9
        )
        
        raw_summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Lọc các câu chứa từ khóa meta
        clean_sentences = [
            sent for sent in sent_tokenize(raw_summary)
            if not self.meta_pattern.search(sent)
        ]
        
        return ' '.join(clean_sentences)

    def _extract_keywords(self, sentences):
        """Trích xuất từ khóa quan trọng"""
        word_freq = defaultdict(int)
        for sent in sentences:
            for word in sent.split():
                w = word.lower()
                if len(w) > 2 and w not in self._get_stopwords():
                    word_freq[w] += 1
        return [w for w, _ in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]]

    def _find_key_sentences(self, sentences):
        """Xác định câu quan trọng nhất"""
        if not sentences:
            return []
        
        scored_sentences = []
        for sent in sentences:
            score = len(sent.split())  # Độ dài câu
            score += len(re.findall(r'\b[A-Z][a-zà-ỹ]+\b', sent))  # Tên riêng
            score += len(re.findall(r'\b\d+[\.,]?\d*\b', sent))  # Số liệu
            scored_sentences.append((sent, score))
        
        # Sắp xếp theo điểm và lấy top 3
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        return [sent for sent, _ in scored_sentences[:3]]

    def _get_stopwords(self):
        """Danh sách stopwords tiếng Việt mở rộng"""
        return {
            'và', 'là', 'của', 'trong', 'để', 'với', 'theo', 'các', 'này', 'đó',
            'từ', 'có', 'cho', 'không', 'được', 'tại', 'bởi', 'vì', 'nếu', 'nên',
            'đã', 'sẽ', 'đang', 'mà', 'như', 'nhưng', 'hay', 'vào', 'ra', 'lên',
            'xuống', 'bằng', 'về', 'khi', 'sau', 'trước', 'thì', 'cũng', 'những',
            'đến', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín',
            'mười', 'trên', 'dưới', 'nhiều', 'ít', 'rất', 'thật', 'làm', 'qua',
            'lại', 'được', 'phải', 'nếu', 'thế', 'vậy', 'tôi', 'bạn', 'hắn', 'chúng',
            'chúng tôi', 'chúng ta', 'họ', 'ông', 'bà', 'anh', 'chị', 'em', 'ai',
            'văn', 'bản', 'tóm tắt', 'yêu cầu', 'lưu ý', 'số', 'liệu', 'quan', 'trọng',
            'văn', 'phong', 'tự', 'nhiên', 'độ', 'dài', 'câu'
        }
    def _normalize_structure(self, text: str) -> str:
        """Chuẩn hóa cấu trúc văn bản đầu ra"""
        sentences = []
        seen = set()
        for sent in sent_tokenize(text):
            sent = sent.strip()
            if not sent:
                continue
            # Đảm bảo câu kết thúc bằng dấu câu
            if not sent[-1] in '.!?':
                sent += '.'
            # Viết hoa chữ cái đầu
            sent = sent[0].upper() + sent[1:]
            if sent not in seen:
                seen.add(sent)
                sentences.append(sent)
        return ' '.join(sentences)
        
    def _post_process_summary(self, summary, original):
        """Xử lý hậu kỳ để đảm bảo chất lượng"""
        # Lọc câu dựa trên sự tồn tại trong văn bản gốc
        original_words = set(original.lower().split())
        valid_sentences = []
        
        for sent in sent_tokenize(summary):
            sent_words = set(sent.lower().split())
            if len(sent_words & original_words) >= 2:  # Ít nhất 2 từ trùng khớp
                valid_sentences.append(sent)
        
        # Chuẩn hóa cấu trúc nếu có câu hợp lệ
        if valid_sentences:
            return self._normalize_structure(' '.join(valid_sentences))
        return self._normalize_structure(summary)  # Fallback nếu không có câu nào hợp lệ

if __name__ == "__main__":
    text = """
vietnews: Thủ tướng Nguyễn Xuân Phúc và Bộ trưởng Ngoại giao Nhật Bản Taro Kono - Ảnh: VGP/Quang Hiếu.
Tại buổi tiếp, Thủ tướng Nguyễn Xuân Phúc bày tỏ vui mừng trước sự phát triển nhanh chóng, thực chất và toàn diện của quan hệ Đối tác chiến lược sâu rộng Việt Nam - Nhật Bản; cho rằng việc hai nước đẩy mạnh trao đổi và tiếp xúc đoàn cấp cao thời gian qua đã giúp tăng cường sự tin cậy- điều kiện quan trọng để thúc đẩy quan hệ Việt Nam - Nhật Bản phát triển hơn nữa trên mọi lĩnh vực; mong muốn tăng cường hợp tác ASEAN - Nhật Bản và Mekong - Nhật Bản, nhất là khi Việt Nam đảm nhiệm vai trò Điều phối viên quan hệ ASEAN - Nhật Bản giai đoạn 2018 - 2021; đánh giá cao Nhật Bản đã cung cấp vốn hỗ trợ phát triển chính thức ODA cho Việt Nam thời gian qua, khẳng định Chính phủ Việt Nam coi trọng và nỗ lực thực hiện hiệu quả các dự án vốn vay ODA giữa hai nước.
Ảnh: VGP/Quang Hiếu.
Thủ tướng Nguyễn Xuân Phúc đề nghị Bộ trưởng Ngoại giao Nhật Bản quan tâm thúc đẩy liên kết kinh tế giữa 2 nước, đặc biệt là những lĩnh vực có nhiều tiềm năng như hợp tác thương mại, đầu tư, đào tạo nguồn nhân lực; tiếp tục cung cấp vốn vay ODA cho Việt Nam trong các lĩnh vực xây dựng cơ sở hạ tầng, đào tạo nguồn nhân lực, ứng phó với biến đổi khí hậu; thúc đẩy hợp tác trong lĩnh vực cải cách hành chính, hỗ trợ Việt Nam xây dựng chính phủ điện tử; phối hợp thực hiện Hiệp định Đối tác Toàn diện và Tiến bộ xuyên Thái Bình Dương (CPTPP) và trong đàm phán Hiệp định Đối tác kinh tế khu vực (RCEP); tăng cường tiếp nhận lao động Việt Nam, thúc đẩy giao lưu nhân dân và cùng phối hợp chặt chẽ trong các vấn đề quốc tế và khu vực thời gian tới. Thủ tướng Nguyễn Xuân Phúc cũng đánh giá cao các hoạt động kỷ niệm có ý nghĩa đang diễn ra tại hai nước nhân dịp kỷ niệm 45 năm thiết lập quan hệ ngoại giao Việt Nam - Nhật Bản, góp phần quan trọng vào tăng cường hiểu biết, thúc đẩy giao lưu nhân dân giữa hai nước.
Ảnh: VGP/Quang Hiếu.
Bộ trưởng Taro Kono bày tỏ vui mừng được quay lại Hà Nội sau 27 năm, đúng vào dịp kỷ niệm 45 năm thiết lập quan hệ ngoại giao và tham dự các hoạt động của Hội nghị WEF ASEAN tại Việt Nam; bày tỏ mong muốn đóng góp vào thành công của Hội nghị và thúc đẩy hơn nữa quan hệ hợp tác Việt Nam - Nhật Bản.
Bộ trưởng khẳng định Nhật Bản đánh giá cao vai trò ngày càng chủ động và đóng góp tích cực của Việt Nam trong các vấn đề quốc tế và khu vực; cảm ơn việc Thủ tướng sẽ dự Hội nghị Cấp cao Mekong - Nhật Bản thời gian tới theo lời mời của Chính phủ Nhật Bản, đề nghị hai bên phối hợp chặt chẽ vì thành công của Hội nghị.
Bộ trưởng Taro Kono khẳng định Nhật Bản sẽ hỗ trợ Việt Nam nâng cao năng suất lao động, chia sẻ kinh nghiệm trong xây dựng Chính phủ điện tử; ủng hộ quan điểm của Việt Nam và các nước ASEAN trong vấn đề Biển Đông khi Việt Nam đảm nhiệm vai trò Điều phối viên Quan hệ ASEAN - Nhật Bản từ năm 2018.
Đức Tuân. </s>
"""
    summarizer = Summarizer()
    summary = summarizer.summarize(text, length_option="medium")
    print(summary)

   


