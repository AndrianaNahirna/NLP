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
            'A': 'А', 'E': 'Е', 'O': 'О', 'P': 'Р', 'X': 'Х', 'C': 'С', 'I': 'І', 'H': 'Н', 'M': 'М', 'T': 'Т',
            'Y': 'У', 'B': 'В', 'K': 'К'
        }

    def clean_basic(self, text: str) -> str:
        if not text: return ""
        text = html.unescape(text)

        # Видаляємо технічні слова
        text = re.sub(r"(?i)\b(розгорнути|згорнути|читати далі|відповідь|розгорнутим)\b", " ", text)
        return text.strip()

    def mask_pii(self, text: str) -> str:
        """Маскування даних"""
        
        # EMAIL
        text = re.sub(r"\S+@\S+", " <EMAIL> ", text)

        # URL
        url_pattern = r'https?://\S+|www\.\S+|\b[a-z0-9.-]+\.(?:com|ua|net|org|edu|gov|io)\b(?:\/\S*)?'
        text = re.sub(url_pattern, " <URL> ", text)

        # ID
        text = re.sub(r"(?i)(?:№+|код|замовлення|номер)\s*#?[\d\s,]{4,}\d", " <ID> ", text)
        text = re.sub(r"\b\d{5,15}\b(?!\s*(?:грн|usd|eur|₴|\$|%|шт))", " <ID> ", text, flags=re.I)
        
        # PHONE
        phone_pattern = r"(\+?38)?\s?\(?\d{3}\)?[\s\.-]?\d{3}[\s\.-]?\d{2}[\s\.-]?\d{2}"
        text = re.sub(phone_pattern, " <PHONE> ", text)
        
        # Видалення дублікатів тегів
        text = re.sub(r"(<ID>\s*[,/]*\s*)+", "<ID> ", text)
        
        # Очищення зайвих пробілів
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def normalize_content(self, text: str) -> str:
        """Нормалізація."""
        
        parts = re.split(r"(<[A-Z]+>)", text)
        translation_table = str.maketrans(self.cyrillic_map)
        
        for i in range(len(parts)):
            # Якщо це НЕ тег, тоді нормалізуємо
            if not re.match(r"<[A-Z]+>", parts[i]):
                part = parts[i]
                
                # Гомогліфи
                part = part.translate(translation_table)

                # Апострофи
                part = re.sub(r"[`'’‘]", "'", part)
                
                # Caps Lock
                def lower_caps(match):
                    word = match.group(0)
                    if any(char.isdigit() for char in word): return word
                    return word.lower()
                
                part = re.sub(r"\b[А-ЯІЇЄҐA-Z]{2,}\b", lower_caps, part)

                # Пунктуація
                part = re.sub(r"\s+([.,!?])", r"\1", part)
                part = re.sub(r"!{2,}", "!!", part)
                part = re.sub(r"\?{2,}", "??", part)
                part = re.sub(r"\.{4,}", "...", part)

                # Пробіли
                part = re.sub(r"\b(м|вул|кв|просп|бул)\.(?=[А-ЯІЇЄҐа-яіїєґA-Za-z])", r"\1. ", part)
                part = re.sub(r"(\d+)\s*(грн|usd|eur|%|шт|тб|gb|tb|кг|₴|\$)\b", lambda m: f"{m.group(1)} {m.group(2).lower()}", part, flags=re.I)
                
                parts[i] = part
                
        return "".join(parts)

    def sentence_split(self, text: str) -> list[str]:
        abbs_pattern = "|".join([re.escape(a.replace('.', '')) for a in self.ua_abbreviations])
        pattern = rf"(?<!\b(?:{abbs_pattern}))(?<=[.!?])\s+(?=[А-ЯІЇЄҐA-Z])"
        
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