from sklearn.decomposition import TruncatedSVD, LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

def run_lsa(corpus, custom_stop_words, n_components=5):
    """Навчання LSA"""
    tfidf_vectorizer = TfidfVectorizer(
        ngram_range=(1, 2), 
        min_df=5, 
        max_df=0.8,
        stop_words=custom_stop_words 
    )
    tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)
    lsa_model = TruncatedSVD(n_components=n_components, random_state=42)
    lsa_matrix = lsa_model.fit_transform(tfidf_matrix)
    return lsa_model, tfidf_vectorizer, lsa_matrix

def run_lda(corpus, custom_stop_words, n_components=5):
    """Навчання LDA з фільтрацією стоп-слів"""
    count_vectorizer = CountVectorizer(
        ngram_range=(1, 1), 
        min_df=5, 
        max_df=0.8,
        stop_words=custom_stop_words
    )
    count_matrix = count_vectorizer.fit_transform(corpus)
    lda_model = LatentDirichletAllocation(
        n_components=n_components, 
        random_state=42, 
        learning_method='online'
    )
    lda_matrix = lda_model.fit_transform(count_matrix)
    return lda_model, count_vectorizer, lda_matrix