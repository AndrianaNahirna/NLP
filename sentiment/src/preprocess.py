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

    def mask_pii(self, text: str) -> str:
        """Маскування конфіденційних даних з пробілами, щоб уникнути злипання."""
        # URL & Domains
        url_pattern = r'https?://\S+|www\.\S+|\b[a-z0-9.-]+\.(?:com|ua|net|org|edu|gov|io)\b(?:\/\S*)?'
        text = re.sub(url_pattern, " <URL> ", text)

        # Email
        text = re.sub(r"\S+@\S+", " <EMAIL> ", text)

        # Номери замовлень (ID) - шукаємо № або код і довгі послідовності цифр
        # Додано підтримку №№ та переліку номерів
        text = re.sub(r"(?i)(?:№+|код|замовлення|номер)\s*#?[\d\s,]{4,}\d", " <ID> ", text)

        # Телефони
        phone_pattern = r"(\+?38)?\s?\(?\d{3}\)?[\s\.-]?\d{3}[\s\.-]?\d{2}[\s\.-]?\d{2}"
        text = re.sub(phone_pattern, " <PHONE> ", text)
        
        return text

    def normalize_content(self, text: str) -> str:
        # 1. Уніфікація апострофів
        text = re.sub(r"[`'’‘]", "'", text)
        
        # 2. Стиснення пунктуації (залишаємо 2 для інтенсивності)
        text = re.sub(r"!{2,}", "!!", text)
        text = re.sub(r"\?{2,}", "??", text)
        text = re.sub(r"\.{4,}", "...", text)

        # 3. Пробіли: число + валюта/одиниця
        text = re.sub(r"(\d+)\s*(грн|usd|eur|%|шт|тб|gb|tb|кг)\b", r"\1 \2", text, flags=re.I)
        
        # 4. Пробіли після скорочень (м.Київ -> м. Київ)
        text = re.sub(r"\b(м|вул|кв|просп|бул)\.(?=[А-ЯІЇЄҐA-Z])", r"\1. ", text)

        # 5. Caps Lock: переводимо в нижній регістр слова довжиною > 2
        def lower_caps(match):
            word = match.group(0)
            # Не чіпаємо теги <URL>, <PHONE> тощо
            if word in ["URL", "PHONE", "EMAIL", "ID"]: return word
            return word.lower()
        
        text = re.sub(r"\b[А-ЯІЇЄҐA-Z]{3,}\b", lower_caps, text)

        # 6. Виправлення гомогліфів (ОБЕРЕЖНО: не чіпаємо латиницю в тегах)
        # Розбиваємо текст по тегах, нормалізуємо тільки "м'ясо" тексту
        parts = re.split(r"(<[A-Z]+>)", text)
        translation_table = str.maketrans(self.cyrillic_map)
        
        for i in range(len(parts)):
            if not re.match(r"<[A-Z]+>", parts[i]):
                parts[i] = parts[i].translate(translation_table)
        
        text = "".join(parts)
        
        # Фінальне чищення пробілів
        text = re.sub(r"\s+", " ", text)
        return text.strip()

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