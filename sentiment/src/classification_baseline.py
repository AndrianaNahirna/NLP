import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, f1_score

def build_and_train_pipeline(X_train, y_train):
    """
    Створює та навчає пайплайн для класифікації текстів.
    
    Параметри:
    X_train (pd.Series): Текстові дані для навчання (бажано лематизовані).
    y_train (pd.Series): Мітки класів.
    
    Повертає:
    Pipeline: Навчена модель.
    """
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(analyzer="word", ngram_range=(1, 2), sublinear_tf=True)),
        ('logreg', LogisticRegression(max_iter=500, class_weight='balanced', random_state=42))
    ])
    
    pipeline.fit(X_train, y_train)
    return pipeline

def evaluate_model(pipeline, X_test, y_test):
    """
    Оцінює навчену модель та виводить базові метрики.
    """
    y_pred = pipeline.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average='macro')
    
    print(f"Accuracy: {acc:.4f}")
    print(f"Macro-F1: {macro_f1:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    return y_pred

if __name__ == "__main__":
    print("Ініціалізація модуля classification_baseline.py...")
    print("Використовуйте функції build_and_train_pipeline() та evaluate_model() для роботи з даними.")