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

    def mask_pii(self, text: str) -> str:
        """Крок 1: Маскування даних (виконується ПЕРЕД нормалізацією)"""
        
        # 1. EMAIL (ОБОВ'ЯЗКОВО ПЕРЕД URL, щоб не розривати домени)
        text = re.sub(r"\S+@\S+", " <EMAIL> ", text)

        # 2. URL
        url_pattern = r'https?://\S+|www\.\S+|\b[a-z0-9.-]+\.(?:com|ua|net|org|edu|gov|io)\b(?:\/\S*)?'
        text = re.sub(url_pattern, " <URL> ", text)

        # 3. ID / Замовлення
        # Спочатку ловимо контекст (№ 12345, замовлення 12345)
        text = re.sub(r"(?i)(?:№+|код|замовлення|номер)\s*#?[\d\s,]{4,}\d", " <ID> ", text)
        # Потім будь-які поодинокі довгі числа, АЛЕ ТІЛЬКИ ЯКЩО ЦЕ НЕ ГРОШІ/ШТУКИ
        text = re.sub(r"\b\d{5,15}\b(?!\s*(?:грн|usd|eur|₴|\$|%|шт))", " <ID> ", text, flags=re.I)
        
        # 4. Телефони
        phone_pattern = r"(\+?38)?\s?\(?\d{3}\)?[\s\.-]?\d{3}[\s\.-]?\d{2}[\s\.-]?\d{2}"
        text = re.sub(phone_pattern, " <PHONE> ", text)
        
        # Видаляємо дублікати тегів
        text = re.sub(r"(<ID>\s*[,/]*\s*)+", "<ID> ", text)
        
        # Чистимо зайві пробіли
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def normalize_content(self, text: str) -> str:
        """Крок 2: Нормалізація із ЗАХИСТОМ технічних тегів."""
        # Розбиваємо текст так, щоб теги <URL>, <EMAIL> тощо були окремими елементами
        parts = re.split(r"(<[A-Z]+>)", text)
        translation_table = str.maketrans(self.cyrillic_map)
        
        for i in range(len(parts)):
            # Якщо це НЕ тег, тоді нормалізуємо
            if not re.match(r"<[A-Z]+>", parts[i]):
                part = parts[i]
                
                # 1. Гомогліфи
                part = part.translate(translation_table)

                # 2. Апострофи
                part = re.sub(r"[`'’‘]", "'", part)
                
                # 3. Caps Lock
                def lower_caps(match):
                    word = match.group(0)
                    if any(char.isdigit() for char in word): return word
                    return word.lower()
                
                part = re.sub(r"\b[А-ЯІЇЄҐA-Z]{2,}\b", lower_caps, part)

                # 4. Пунктуація
                part = re.sub(r"!{2,}", "!!", part)
                part = re.sub(r"\?{2,}", "??", part)
                part = re.sub(r"\.{4,}", "...", part)

                # 5. Пробіли
                part = re.sub(r"\b(м|вул|кв|просп|бул)\.(?=[А-ЯІЇЄҐа-яіїєґA-Za-z])", r"\1. ", part)
                part = re.sub(r"(\d+)\s*(грн|usd|eur|%|шт|тб|gb|tb|кг|₴|\$)\b", r"\1 \2", part, flags=re.I)
                
                parts[i] = part
                
        # Збираємо текст назад
        return "".join(parts)

    def sentence_split(self, text: str) -> list[str]:
        # Тут бібліотека regex розкриває свою силу: Look-behind змінної довжини
        abbs_pattern = "|".join([re.escape(a.replace('.', '')) for a in self.ua_abbreviations])
        pattern = rf"(?<!\b(?:{abbs_pattern}))(?<=[.!?])\s+(?=[А-ЯІЇЄҐA-Z])"
        
        sentences = re.split(pattern, text)
        return [s.strip() for s in sentences if len(s.strip()) > 1]

    def preprocess(self, text: str) -> dict:
        t = self.clean_basic(text)
        
        # ПРАВИЛЬНИЙ ПОРЯДОК:
        t = self.mask_pii(t)           # Спочатку знаходимо URL/Email (поки англійська "чиста")
        t = self.normalize_content(t)  # Потім нормалізуємо решту, обходячи теги
        
        sentences = self.sentence_split(t)
        
        return {
            "original": text,
            "clean_normalized": t,
            "sentences": sentences,
            "sentence_count": len(sentences)
        }