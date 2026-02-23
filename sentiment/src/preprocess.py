import re
import html

class TextPreprocessor:
    def __init__(self):
        self.ua_abbreviations = [
            'ім.', 'вул.', 'грн.', 'обл.', 'р.', 'див.', 'п.', 'с.', 'м.', 
            'т.д.', 'т.п.', 'напр.', 'важ.', 'кг.', 'шт.', 'гр.'
        ]
        
        # Гомогліфи
        self.cyrillic_map = {
            'a': 'а', 'e': 'е', 'o': 'о', 'p': 'р', 'x': 'х', 'c': 'с', 'i': 'і', 'y': 'у',
            'A': 'А', 'E': 'Е', 'O': 'О', 'P': 'Р', 'X': 'Х', 'C': 'С', 'I': 'І', 'H': 'Н', 'M': 'М', 'T': 'Т'
        }

    def clean_basic(self, text: str) -> str:
        """Початкова очистка."""
        if not text: return ""
        text = html.unescape(text)

        # Видалення технічних слів
        text = re.sub(r"(?i)\b(розгорнути|згорнути|читати далі|відповідь|розгорнутим)\b", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def mask_pii(self, text: str) -> str:
        """Маскування URL, Email, Телефонів та ID замовлень."""
        # URL
        url_pattern = r'https?://\S+|www\.\S+|\b[a-z0-9.-]+\.(?:com|ua|net|org|edu|gov)\b(?:\/\S*)?'
        text = re.sub(url_pattern, "<URL>", text)

        # Email
        text = re.sub(r"\S+@\S+", "<EMAIL>", text)

        # Номери замовлень (наприклад, № 123456 або замовлення 12345)
        text = re.sub(r"(?i)(?:№|замовлення|номер|код)\s*#?\d{5,}", "<ID>", text)

        # Телефони
        phone_pattern = r"(\+?38)?\s?\(?\d{3}\)?[\s\.-]?\d{3}[\s\.-]?\d{2}[\s\.-]?\d{2}"
        text = re.sub(phone_pattern, "<PHONE>", text)
        
        return text

    def normalize_content(self, text: str) -> str:
        """Робота з текстом: апострофи, пробіли, Caps Lock, гомогліфи."""
        # Уніфікація апострофів
        text = re.sub(r"[`'’‘]", "'", text)
        
        # Стиснення знаків оклику та крапок (!!! -> !!, ... -> ..)
        # Для тональності залишаємо 2 символи як сигнал посилення
        text = re.sub(r"!{2,}", "!!", text)
        text = re.sub(r"\?{2,}", "??", text)
        text = re.sub(r"\.{4,}", "...", text)

        # Додавання пробілів після скорочень та перед одиницями виміру
        text = re.sub(r"(?<=\d)(грн|usd|eur|%|шт)\b", r" \1", text, flags=re.I)
        text = re.sub(r"\b(м|вул|кв)\.(?=[А-ЯІЇЄҐ])", r"\1. ", text)

        # Виправлення гомогліфів
        translation_table = str.maketrans(self.cyrillic_map)
        text = text.translate(translation_table)

        # Робота з Caps Lock: якщо слово > 2 символів і повністю в верхньому регістрі
        def lower_caps(match):
            word = match.group(0)
            return word.lower() if len(word) > 2 else word
        
        text = re.sub(r"\b[А-ЯІЇЄҐA-Z]{3,}\b", lower_caps, text)

        return text

    def sentence_split(self, text: str) -> list[str]:
        """Спліттер."""
        # Паттерн: знак завершення + пробіл + Велика літера
        pattern = r"(?<!\bім)(?<!\bвул)(?<!\bгрн)(?<!\bобл)(?<!\bстор)(?<=[.!?])\s+(?=[А-ЯІЇЄҐA-Z])"
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