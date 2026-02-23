import re
import html

class TextPreprocessor:
    def __init__(self):
        self.ua_abbreviations = [
            'ім.', 'вул.', 'грн.', 'обл.', 'р.', 'див.', 'п.', 'с.', 'м.', 
            'т.д.', 'т.п.', 'напр.', 'важ.', 'кг.', 'шт.', 'гр.', 'кв.'
        ]
        
        # Гомогліфи (тільки ті, що візуально ідентичні)
        self.cyrillic_map = {
            'a': 'а', 'e': 'е', 'o': 'о', 'p': 'р', 'x': 'х', 'c': 'с', 'i': 'і', 'y': 'у',
            'A': 'А', 'E': 'Е', 'O': 'О', 'P': 'Р', 'X': 'Х', 'C': 'С', 'I': 'І', 'H': 'Н', 'M': 'М', 'T': 'Т'
        }

    def clean_basic(self, text: str) -> str:
        if not text: return ""
        text = html.unescape(text)
        # Прибираємо технічні маркери
        text = re.sub(r"(?i)\b(розгорнути|згорнути|читати далі|відповідь|розгорнутим)\b", " ", text)
        return text.strip()

    def normalize_content(self, text: str) -> str:
        # 1. СЕРЙОЗНА ПРАВКА: Спочатку гомогліфи, ПОКИ НЕМАЄ ТЕГІВ
        translation_table = str.maketrans(self.cyrillic_map)
        text = text.translate(translation_table)

        # 2. Уніфікація апострофів
        text = re.sub(r"[`'’‘]", "'", text)

        # 3. Caps Lock (тепер працює надійно)
        def lower_caps(match):
            word = match.group(0)
            # Якщо це артикул (суміш цифр і літер як QE55Q), не чіпаємо
            if any(char.isdigit() for char in word): return word
            return word.lower()
        
        # Замінюємо всі слова від 2-х літер в верхньому регістрі
        text = re.sub(r"\b[А-ЯІЇЄҐA-Z]{2,}\b", lower_caps, text)

        # 4. Пробіли навколо скорочень
        text = re.sub(r"\b(м|вул|кв)\.(?=[А-ЯІЇЄҐA-Z])", r"\1. ", text)
        text = re.sub(r"(\d+)\s*(грн|%|шт)", r"\1 \2", text, flags=re.I)

        return text

    def mask_pii(self, text: str) -> str:
        # Додаємо пробіли при заміні, щоб теги не злипалися
        url_pattern = r'https?://\S+|www\.\S+|\b[a-z0-9.-]+\.(?:com|ua|net|org)\b(?:\/\S*)?'
        text = re.sub(url_pattern, " <URL> ", text)

        # Маскуємо БУДЬ-ЯКІ довгі цифри (це зазвичай ID або замовлення)
        text = re.sub(r"\b\d{5,12}\b", " <ID> ", text)
        
        # Прибираємо дублікати тегів (якщо було кілька номерів підряд)
        text = re.sub(r"(<ID>\s*)+", "<ID> ", text)

        phone_pattern = r"(\+?38)?\s?\(?\d{3}\)?[\s\.-]?\d{3}[\s\.-]?\d{2}[\s\.-]?\d{2}"
        text = re.sub(phone_pattern, " <PHONE> ", text)
        
        return re.sub(r"\s+", " ", text).strip()

    def sentence_split(self, text: str) -> list[str]:
        # Використовуємо Negative Lookbehind для списку скорочень
        # Це запобігає розриву на "грн. ", "вул. " тощо.
        abbs = "|".join([re.escape(a.replace('.', '')) for a in self.ua_abbreviations])
        pattern = rf"(?<!\b(?:{abbs}))(?<=[.!?])\s+(?=[А-ЯІЇЄҐA-Z])"
        
        sentences = re.split(pattern, text)
        return [s.strip() for s in sentences if len(s.strip()) > 1]

    def preprocess(self, text: str) -> dict:
        t = self.clean_basic(text)      
        t = self.mask_pii(t)           
        t = self.normalize_content(t)  
        
        sentences = self.sentence_split(t)
        
        return {
            "original": text,
            "clean_normalized": t,
            "sentences": sentences,
            "sentence_count": len(sentences)
        }