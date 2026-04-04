import pandas as pd
import numpy as np

def get_top_words(model, vectorizer, n_top_words=10):
    """Отримання топ-слів для кожної теми"""
    feature_names = vectorizer.get_feature_names_out()
    topics = {}
    for topic_idx, topic in enumerate(model.components_):
        top_features_ind = topic.argsort()[:-n_top_words - 1:-1]
        top_features = [feature_names[i] for i in top_features_ind]
        topics[f"Topic {topic_idx}"] = top_features
    return topics

def get_top_documents(doc_topic_matrix, corpus, n_top_docs=2):
    """Отримання топ-документів для кожної теми"""
    top_docs = {}
    for topic_idx in range(doc_topic_matrix.shape[1]):
        # Сортуємо документи за вагою поточної теми
        top_doc_indices = np.argsort(doc_topic_matrix[:, topic_idx])[::-1][:n_top_docs]
        top_docs[f"Topic {topic_idx}"] = [corpus.iloc[i] for i in top_doc_indices]
    return top_docs