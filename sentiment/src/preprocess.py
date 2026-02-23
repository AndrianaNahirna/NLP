import re
import html

class TextPreprocessor:
    def __init__(self):
        self.ua_abbreviations = [
            'ім.', 'вул.', 'грн.', 'обл.', 'р.', 'див.', 'п.', 'с.', 'м.', 
            'т.д.', 'т.п.', 'напр.', 'важ.', 'кг.', 'шт.', 'гр.', 'кв.', 'стор.', 'п.с.'
        ]
        
        # Гомогліфи
        self.cyrillic_map = {
            'a': 'а', 'e': 'е', 'o': 'о', 'p': 'р', 'x': 'х', 'c': 'с', 'i': 'і', 'y': 'у',
            'A': 'А', 'E': 'Е', 'O': 'О', 'P': 'Р', 'X': 'Х', 'C': 'С', 'I': 'І', 'H': 'Н', 'M': 'М', 'T': 'Т'
        }

    def clean_basic(self, text: str) -> str:
        if not text: return ""
        text = html.unescape(text)
        # Видаляємо технічні маркери розгортання тексту
        text = re.sub(r"(?i)\b(розгорнути|згорнути|читати далі|відповідь|розгорнутим)\b", " ", text)
        return text.strip()

    def normalize_content(self, text: str) -> str:
        """Крок 1: Обробка тексту до вставки технічних тегів."""
        # Уніфікація гомогліфів (щоб не побити латиницю в майбутніх тегах)
        translation_table = str.maketrans(self.cyrillic_map)
        text = text.translate(translation_table)

        # Апострофи
        text = re.sub(r"[`'’‘]", "'", text)
        
        # Caps Lock: приводимо до нижнього регістру слова >= 2 літер
        # Виключаємо слова, що містять цифри (артикули як QE55Q)
        def lower_caps(match):
            word = match.group(0)
            if any(c.isdigit() for c in word): return word
            return word.lower()
        text = re.sub(r"\b[А-ЯІЇЄҐA-Z]{2,}\b", lower_caps, text)

        # Пунктуація: стискаємо до 2-3 знаків
        text = re.sub(r"!{2,}", "!!", text)
        text = re.sub(r"\?{2,}", "??", text)
        text = re.sub(r"\.{4,}", "...", text)

        # Пробіли після скорочень та перед одиницями
        text = re.sub(r"\b(м|вул|кв|просп|бул)\.(?=[А-ЯІЇЄҐA-Z])", r"\1. ", text)
        text = re.sub(r"(\d+)\s*(грн|usd|eur|%|шт|тб|gb|tb|кг|₴|\$)\b", r"\1 \2", text, flags=re.I)

        return text

    def mask_pii(self, text: str) -> str:
        """Крок 2: Маскування конфіденційних даних."""
        # URL
        url_pattern = r'https?://\S+|www\.\S+|\b[a-z0-9.-]+\.(?:com|ua|net|org|edu|gov|io)\b(?:\/\S*)?'
        text = re.sub(url_pattern, " <URL> ", text)

        # Email
        text = re.sub(r"\S+@\S+", " <EMAIL> ", text)

        # Номери замовлень (PII) - маскуємо будь-які послідовності 5+ цифр
        text = re.sub(r"(?i)(?:№+|код|замовлення|номер)?\s*#?\d{5,12}", " <ID> ", text)

        # Телефони
        phone_pattern = r"(\+?38)?\s?\(?\d{3}\)?[\s\.-]?\d{3}[\s\.-]?\d{2}[\s\.-]?\d{2}"
        text = re.sub(phone_pattern, " <PHONE> ", text)
        
        # Видаляємо дублікати тегів (якщо було кілька номерів підряд)
        text = re.sub(r"(<ID>\s*)+", "<ID> ", text)
        
        # Фінальне чищення пробілів
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def sentence_split(self, text: str) -> list[str]:
        # Використовуємо Negative Lookbehind, щоб не різати на скороченнях
        abbs_regex = "|".join([re.escape(a.replace('.', '')) for a in self.ua_abbreviations])
        pattern = rf"(?<!\b(?:{abbs_regex}))(?<=[.!?])\s+(?=[А-ЯІЇЄҐA-Z])"
        
        sentences = re.split(pattern, text)
        return [s.strip() for s in sentences if len(s.strip()) > 1]

    def preprocess(self, text: str) -> dict:
        t = self.clean_basic(text)
        t = self.normalize_content(t) # Спочатку нормалізуємо
        t = self.mask_pii(t)           # Потім маскуємо
        
        sentences = self.sentence_split(t)
        
        return {
            "original": text,
            "clean_normalized": t,
            "sentences": sentences,
            "sentence_count": len(sentences)
        }