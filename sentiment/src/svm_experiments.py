from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline

def run_linear_svm(X_train, y_train, analyzer="word", ngram_range=(1, 2), class_weight=None, C=1.0, min_df=1):
    """
    Створює та навчає пайплайн TF-IDF + LinearSVC.
    """
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(analyzer=analyzer, ngram_range=ngram_range, sublinear_tf=True, min_df=min_df)),
        ('svm', LinearSVC(C=C, class_weight=class_weight, random_state=42, max_iter=2000))
    ])
    
    pipeline.fit(X_train, y_train)
    return pipeline