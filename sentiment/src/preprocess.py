import re
import html

class TextPreprocessor:
    def __init__(self):
        self.ua_abbreviations = [
            'ім.', 'вул.', 'грн.', 'обл.', 'р.', 'див.', 'п.', 'с.', 'м.', 
            'т.д.', 'т.п.', 'напр.', 'важ.', 'кг.', 'шт.', 'гр.', 'кв.', 'стор.'
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
        """Нормалізація літер та пунктуації ДО маскування."""
        # 1. Гомогліфи (замінюємо всюди, поки немає тегів)
        translation_table = str.maketrans(self.cyrillic_map)
        text = text.translate(translation_table)

        # 2. Уніфікація апострофів
        text = re.sub(r"[`'’‘]", "'", text)
        
        # 3. Caps Lock (від 2-х літер)
        def lower_caps(match):
            word = match.group(0)
            # Не чіпаємо артикули (літери + цифри)
            if any(c.isdigit() for c in word): return word
            return word.lower()
        
        text = re.sub(r"\b[А-ЯІЇЄҐA-Z]{2,}\b", lower_caps, text)

        # 4. Пунктуація (!!! -> !! для збереження емоції)
        text = re.sub(r"!{2,}", "!!", text)
        text = re.sub(r"\?{2,}", "??", text)
        text = re.sub(r"\.{4,}", "...", text)

        # 5. Пробіли навколо одиниць виміру та скорочень
        text = re.sub(r"(\d+)\s*(грн|usd|eur|%|шт|тб|gb|tb|кг)\b", r"\1 \2", text, flags=re.I)
        text = re.sub(r"\b(м|вул|кв|просп|бул)\.(?=[А-ЯІЇЄҐA-Z])", r"\1. ", text)

        return text

    def mask_pii(self, text: str) -> str:
        """Маскування конфіденційних даних."""
        # URL (додаємо пробіли для запобігання злипанню)
        url_pattern = r'https?://\S+|www\.\S+|\b[a-z0-9.-]+\.(?:com|ua|net|org|edu|gov|io)\b(?:\/\S*)?'
        text = re.sub(url_pattern, " <URL> ", text)

        # Email
        text = re.sub(r"\S+@\S+", " <EMAIL> ", text)

        # Номери замовлень / ID (будь-які послідовності 5+ цифр)
        text = re.sub(r"(?i)(?:№+|код|замовлення|номер)?\s*#?\d{5,}", " <ID> ", text)

        # Телефони
        phone_pattern = r"(\+?38)?\s?\(?\d{3}\)?[\s\.-]?\d{3}[\s\.-]?\d{2}[\s\.-]?\d{2}"
        text = re.sub(phone_pattern, " <PHONE> ", text)
        
        # Видаляємо зайві пробіли, що могли виникнути після маскування
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def sentence_split(self, text: str) -> list[str]:
        # Покращений список скорочень для Negative Lookbehind
        abbs_pattern = "|".join([re.escape(a.replace('.', '')) for a in self.ua_abbreviations])
        pattern = rf"(?<!\b(?:{abbs_pattern}))(?<=[.!?])\s+(?=[А-ЯІЇЄҐA-Z])"
        
        sentences = re.split(pattern, text)
        return [s.strip() for s in sentences if len(s.strip()) > 1]

    def preprocess(self, text: str) -> dict:
        # Зміна порядку: спочатку текст стає "чистим", потім накладаються маски
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