import regex as re
import html

class TextPreprocessor:
    def __init__(self):
        self.ua_abbreviations = [
            'ім.', 'вул.', 'грн.', 'обл.', 'р.', 'див.', 'п.', 'с.', 'м.', 
            'т.д.', 'т.п.', 'напр.', 'важ.', 'кг.', 'шт.', 'гр.', 'кв.', 'стор.', 'п.с.'
        ]
        
        self.cyrillic_map = {
            'a': 'а', 'e': 'е', 'o': 'о', 'p': 'р', 'x': 'х', 'c': 'с', 'i': 'і', 'y': 'у',
            'A': 'А', 'E': 'Е', 'O': 'О', 'P': 'Р', 'X': 'Х', 'C': 'С', 'I': 'І', 'H': 'Н', 'M': 'М', 'T': 'Т'
        }

    def clean_basic(self, text: str) -> str:
        if not text: return ""
        text = html.unescape(text)
        # Видаляємо технічне сміття
        text = re.sub(r"(?i)\b(розгорнути|згорнути|читати далі|відповідь|розгорнутим)\b", " ", text)
        return text.strip()

    def normalize_content(self, text: str) -> str:
        """Крок 1: Обробка символів до того, як з'являться технічні теги."""
        # Уніфікація гомогліфів (важливо зробити ДО вставки <URL> чи <PHONE>)
        translation_table = str.maketrans(self.cyrillic_map)
        text = text.translate(translation_table)

        # Апострофи
        text = re.sub(r"[`'’‘]", "'", text)
        
        # Caps Lock: приводимо до нижнього регістру слова від 2-х літер
        # Але ігноруємо слова з цифрами (артикули типу QE55Q)
        def lower_caps(match):
            word = match.group(0)
            if any(char.isdigit() for char in word): return word
            return word.lower()
        
        text = re.sub(r"\b[А-ЯІЇЄҐA-Z]{2,}\b", lower_caps, text)

        # Пунктуація (залишаємо максимум 2 знаки для емоції)
        text = re.sub(r"!{2,}", "!!", text)
        text = re.sub(r"\?{2,}", "??", text)
        text = re.sub(r"\.{4,}", "...", text)

        # Пробіли після скорочень та перед валютами
        text = re.sub(r"\b(м|вул|кв|просп|бул)\.(?=[А-ЯІЇЄҐA-Z])", r"\1. ", text)
        text = re.sub(r"(\d+)\s*(грн|usd|eur|%|шт|тб|gb|tb|кг|₴|\$)\b", r"\1 \2", text, flags=re.I)

        return text

    def mask_pii(self, text: str) -> str:
        """Крок 2: Маскування даних з примусовими пробілами."""
        # URL
        url_pattern = r'https?://\S+|www\.\S+|\b[a-z0-9.-]+\.(?:com|ua|net|org|edu|gov|io)\b(?:\/\S*)?'
        text = re.sub(url_pattern, " <URL> ", text)

        # Email
        text = re.sub(r"\S+@\S+", " <EMAIL> ", text)

        # ID / Замовлення (маскуємо будь-які послідовності 5+ цифр, щоб захопити списки)
        text = re.sub(r"(?i)(?:№+|код|замовлення|номер)?\s*#?\d{5,15}", " <ID> ", text)
        
        # Телефони
        phone_pattern = r"(\+?38)?\s?\(?\d{3}\)?[\s\.-]?\d{3}[\s\.-]?\d{2}[\s\.-]?\d{2}"
        text = re.sub(phone_pattern, " <PHONE> ", text)
        
        # Видаляємо дублікати тегів (якщо було кілька номерів через кому)
        text = re.sub(r"(<ID>\s*)+", "<ID> ", text)
        
        # Чистимо зайві пробіли
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def sentence_split(self, text: str) -> list[str]:
        abbs_pattern = "|".join([re.escape(a.replace('.', '')) for a in self.ua_abbreviations])
        pattern = rf"(?<!\b(?:{abbs_pattern}))(?<=[.!?])\s+(?=[А-ЯІЇЄҐA-Z])"
        
        sentences = re.split(pattern, text)
        return [s.strip() for s in sentences if len(s.strip()) > 1]

    def preprocess(self, text: str) -> dict:
        # Зміна порядку: нормалізація ПЕРЕД маскуванням
        t = self.clean_basic(text)
        t = self.normalize_content(t) 
        t = self.mask_pii(t)
        
        sentences = self.sentence_split(t)
        
        return {
            "original": text,
            "clean_normalized": t,
            "sentences": sentences,
            "sentence_count": len(sentences)
        }