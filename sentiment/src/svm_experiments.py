from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline

def build_svm_pipeline(X_train, y_train, analyzer="word", ngram_range=(1, 2), class_weight=None):
    """
    Створює та навчає пайплайн TF-IDF + LinearSVC.
    
    Параметри дозволяють легко перемикатися між word та char n-grams, 
    а також додавати балансування класів.
    """
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(analyzer=analyzer, ngram_range=ngram_range, sublinear_tf=True)),
        ('svm', LinearSVC(C=1.0, class_weight=class_weight, random_state=42, max_iter=2000))
    ])
    
    pipeline.fit(X_train, y_train)
    return pipeline