import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve, f1_score, classification_report

def plot_pr_curve(y_true, y_scores, pos_label='negative'):
    """
    Будує PR-криву та знаходить оптимальний поріг для максимізації F1-score.
    """
    y_true_binary = (y_true == pos_label).astype(int)
    
    precision, recall, thresholds = precision_recall_curve(y_true_binary, y_scores)
    
    fscore = (2 * precision * recall) / (precision + recall + 1e-10) 
    ix = np.argmax(fscore)
    best_thresh = thresholds[ix] if ix < len(thresholds) else thresholds[-1]
    
    plt.figure(figsize=(7, 5))
    plt.plot(recall, precision, marker='.', label='PR Curve')
    plt.scatter(recall[ix], precision[ix], marker='o', color='black', label=f'Best F1 Threshold={best_thresh:.3f}')
    
    plt.title(f'Precision-Recall Curve (Target Class: {pos_label})')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    return best_thresh

def evaluate_thresholds(y_true, y_scores, threshold, pos_label='negative'):
    """
    Оцінює результати з кастомним порогом.
    """
    y_true_binary = (y_true == pos_label).astype(int)
    y_pred_binary = (y_scores >= threshold).astype(int)
    
    neg_label = 'positive' if pos_label == 'negative' else 'negative'
    y_pred_labels = np.where(y_pred_binary == 1, pos_label, neg_label)
    
    print(f"Classification Report (Threshold = {threshold:.3f})")
    print(classification_report(y_true, y_pred_labels))
    return y_pred_labels