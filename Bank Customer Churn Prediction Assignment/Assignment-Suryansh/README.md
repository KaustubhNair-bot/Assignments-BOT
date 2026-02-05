# Bank Customer Churn Prediction

## Problem Statement
Predict whether a customer will leave the bank (Churn) based on their demographic and activity data.  
This is a **binary classification** problem aimed at helping the bank identify risky customers early and take retention actions.

---

## Dataset
- Source: Kaggle – Bank Customer Churn Prediction  
- Target Variable: **Exited (1 = Churn, 0 = Stay)**
- Contains demographic, financial, and engagement related features.

---

## Project Workflow

### 1. Anti-Leakage Data Splitting
- Dataset was split **before any analysis** to avoid data leakage.
- Strategy: **Train (80%) – Test (20%)**
- Test set remained completely unseen until final evaluation.

---

### 2. Feature Engineering & Preprocessing

**Steps performed:**

- Dropped non-useful columns:  
  - RowNumber, CustomerId, Surname

- Categorical Encoding  
  - Gender → Binary encoding  
  - Geography → One-Hot encoding

- Scaling  
  - StandardScaler applied to numerical features

- Derived Features  
  - `Balance_per_Product` – financial load indicator  
  - `Inactive_HighBalance` – risk flag for inactive but rich customers

---

### 3. Models Trained

- Dummy Classifier (baseline)
- Decision Tree
- Random Forest
- XGBoost (Default)
- XGBoost (Tuned with GridSearchCV)

---

### 4. Evaluation Metrics

- Accuracy  
- Precision  
- Recall  
- F1-Score  
- ROC-AUC  
- Confusion Matrix

---

## Results Summary

### Performance Comparison

| Model | Accuracy | Recall (Churn) | Precision (Churn) | False Negatives |
|------|----------|----------------|--------------------|----------------|
| Decision Tree | 84% | 24% | ~70% | 310 |
| Random Forest | 86% | 46% | 76% | 220 |
| XGBoost (Default) | 86% | 47% | 78% | 216 |
| **XGBoost Tuned** | **87%** | **49%** | **80%** | **209** |

### ROC-AUC Scores

- Decision Tree → 0.795  
- Random Forest → 0.847  
- XGBoost Default → 0.863  
- **XGBoost Tuned → 0.866**

---

## Feature Importance Insights

Top factors influencing churn:

1. **NumOfProducts** – strongest driver  
2. **IsActiveMember** – inactivity increases risk  
3. **Age** – older customers churn more  
4. **Geography_Germany** – regional impact  
5. **Balance_per_Product** – engineered feature proved useful

---

## Business Insights

- Every **False Negative = lost customer & revenue**
- High-risk segments:
  - Older customers  
  - Inactive members  
  - Low product engagement  
  - High balance relative to products

Using the model, the bank can:

- Target retention offers to truly risky users  
- Reduce marketing waste  
- Prioritize campaigns by probability scores

---

## Final Conclusion

Tuned XGBoost emerged as the best model with:

- **87% accuracy**
- **80% precision**
- **49% recall**
- **ROC-AUC 0.866**

It outperformed the baseline and other models by reducing false negatives and providing reliable predictions.  
Therefore, **Tuned XGBoost is recommended for real-world deployment** in churn retention strategy.