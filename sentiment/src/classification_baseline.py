import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix, ConfusionMatrixDisplay

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

def plot_cm(y_true, y_pred, classes, title="Confusion Matrix"):
    """
    Будує та відображає матрицю плутанини.
    """
    cm = confusion_matrix(y_true, y_pred, labels=classes)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=classes)
    
    fig, ax = plt.subplots(figsize=(5, 4))
    disp.plot(cmap=plt.cm.Blues, ax=ax, values_format='d')
    plt.title(title)
    plt.show()

if __name__ == "__main__":
    print("Ініціалізація модуля classification_baseline.py...")
    print("Використовуйте функції build_and_train_pipeline() та evaluate_model() для роботи з даними.")