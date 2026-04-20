import pandas as pd
from gensim.models import Word2Vec, FastText

def prepare_corpus(df):
    """Фільтрує датасет та токенізує леми"""
    # Видаляємо порожні та дуже короткі тексти
    df_filtered = df.dropna(subset=['lemma_text']).copy()
    df_filtered = df_filtered[df_filtered['lemma_text'].str.len() > 20]
    
    # Токенізація
    corpus_tokens = df_filtered['lemma_text'].astype(str).apply(lambda x: x.split()).tolist()
    return corpus_tokens, len(df), len(df_filtered)

def train_w2v(corpus_tokens, vector_size=100, window=5, min_count=3, sg=1):
    """Тренує та повертає модель Word2Vec"""
    model = Word2Vec(sentences=corpus_tokens, vector_size=vector_size, 
                     window=window, min_count=min_count, sg=sg, workers=4, seed=42)
    return model

def train_ft(corpus_tokens, vector_size=100, window=5, min_count=3, sg=1):
    """Тренує та повертає модель FastText"""
    model = FastText(sentences=corpus_tokens, vector_size=vector_size, 
                     window=window, min_count=min_count, sg=sg, workers=4, seed=42)
    return model