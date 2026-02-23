import re
import html

class TextPreprocessor:
    def __init__(self):
        # Список скорочень для Sentence Splitter
        self.ua_abbreviations = [
            'ім.', 'вул.', 'грн.', 'обл.', 'р.', 'див.', 'п.', 'с.', 'м.', 
            'т.д.', 'т.п.', 'напр.', 'важ.', 'кг.', 'шт.', 'гр.'
        ]
        
        # Словник для нормалізації
        self.cyrillic_map = {
            # Маленькі
            'a': 'а', 'e': 'е', 'o': 'о', 'p': 'р', 'x': 'х', 'c': 'с', 'i': 'і', 'y': 'у',
            # Великі
            'A': 'А', 'E': 'Е', 'O': 'О', 'P': 'Р', 'X': 'Х', 'C': 'С', 'I': 'І', 'H': 'Н', 'M': 'М', 'T': 'Т'
        }

    def clean_text(self, text: str) -> str:
        """Базова очистка від технічного сміття."""
        if not text: return ""
        
        # Декодування HTML сутностей (&#39; -> ', &quot; -> " тощо)
        text = html.unescape(text)
        
        # Видалення специфічних фраз
        text = re.sub(r"(?i)розгорнутим|розгорнути|згорнути|читати далі|відповідь", " ", text)
        
        # Видалення невидимих символів та зайвих пробілів/переносів
        text = re.sub(r"\s+", " ", text)
        
        return text.strip()

    def normalize_text(self, text: str) -> str:
        # Уніфікація апострофів
        text = re.sub(r"[`'’‘]", "'", text)
        
        # Заміна символів
        translation_table = str.maketrans(self.cyrillic_map)
        text = text.translate(translation_table)
        
        return text

    def mask_pii(self, text: str) -> str:
        """Маскування конфіденційних даних."""
        # URL
        text = re.sub(r"https?://\S+|www\.\S+", "<URL>", text)

        # Email
        text = re.sub(r"\S+@\S+", "<EMAIL>", text)

        # Номери телефонів
        text = re.sub(r"(\+?38)?\s?\(?\d{3}\)?[\s\.-]?\d{3}[\s\.-]?\d{2}[\s\.-]?\d{2}", "<PHONE>", text)
        
        return text

    def sentence_split(self, text: str) -> list[str]:
        """Розбиття на речення з урахуванням скорочень."""
        if not text: return []
        
        # Знаходимо всі потенційні місця розриву (крапка + пробіл + Велика літера)
        def split_checker(match):
            full_match = match.group(0) # наприклад ". Т"
            part_before = text[:match.start()]
            
            # Перевіряємо, чи закінчується текст перед крапкою на якесь із скорочень
            if any(part_before.lower().endswith(abb.lower()[:-1]) for abb in self.ua_abbreviations):
                return full_match
            
            return full_match.replace(" ", "<SPLIT>")

        # Шукаємо крапку/знак оклику/питання, пробіл і Велику літеру (кириличну або латинську)
        pattern = r"[.!?]\s+(?=[А-ЯІЇЄҐA-Z])"
        temp_text = re.sub(pattern, split_checker, text)
        
        # Ріжемо по нашому тегу
        sentences = temp_text.split("<SPLIT>")
        
        return [s.strip() for s in sentences if s.strip()]

    def preprocess(self, text: str) -> dict:
        cleaned = self.clean_text(text)
        normalized = self.normalize_text(cleaned)
        masked = self.mask_pii(normalized)
        sentences = self.sentence_split(masked)
        
        return {
            "original": text,
            "clean_normalized": masked,
            "sentences": sentences,
            "sentence_count": len(sentences)
        }