import stanza

class LinguisticExtractor:
    def __init__(self, use_gpu=True):
        """
        Ініціалізує пайплайн Stanza для української мови.
        Завантажує модель, якщо її ще немає на диску.
        """
        # Завантажуємо тільки необхідні процесори для швидкості
        stanza.download('uk', processors='tokenize,pos,lemma')
        
        # Ініціалізуємо пайплайн (вимкнули зайві логи, щоб не спамити в консоль)
        self.nlp = stanza.Pipeline('uk', 
                                   processors='tokenize,pos,lemma', 
                                   use_gpu=use_gpu, 
                                   logging_level='WARN')

    def extract_features(self, text: str) -> dict:
        """
        Повертає словник з лемами та POS-тегами для заданого тексту.
        """
        if not text or not isinstance(text, str):
            return {
                "lemma_text": "",
                "pos_seq": "",
                "pos_text": ""
            }
        
        # Проганяємо текст через Stanza
        doc = self.nlp(text)
        
        lemmas = []
        upos_tags = []
        
        for sentence in doc.sentences:
            for word in sentence.words:
                # Беремо лему (якщо Stanza не змогла, беремо оригінальне слово)
                lemma = word.lemma if word.lemma else word.text
                lemmas.append(lemma.lower()) # Зводимо леми до нижнього регістру
                
                # Беремо Universal POS tag (UPOS)
                upos = word.upos if word.upos else "X"
                upos_tags.append(upos)
                
        return {
            "lemma_text": " ".join(lemmas),         # "lemma"
            "pos_seq": " ".join(upos_tags),         # "ADJ NOUN"
            "pos_text": "_".join(upos_tags)         # "ADJ_NOUN"
        }

    def filter_by_pos(self, text: str, allowed_pos: set = {"NOUN", "ADJ", "VERB"}) -> str:
        """
        Опційна функція (Фільтр): залишає в тексті тільки визначені частини мови.
        """
        if not text or not isinstance(text, str):
            return ""
            
        doc = self.nlp(text)
        filtered_lemmas = []
        
        for sentence in doc.sentences:
            for word in sentence.words:
                if word.upos in allowed_pos:
                    lemma = word.lemma if word.lemma else word.text
                    filtered_lemmas.append(lemma.lower())
                    
        return " ".join(filtered_lemmas)