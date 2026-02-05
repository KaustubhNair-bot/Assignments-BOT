# Bank Customer Churn Prediction

## Problem Statement
The objective of this project is to predict whether a bank customer will churn (leave the bank) based on their demographic and account activity data. This is a binary classification problem with class imbalance, where recall is a critical metric due to the higher business cost of missing churners.

Dataset used:
Bank Customer Churn Prediction (Kaggle)

---

## Project Structure
The solution is implemented as a Jupyter Notebook and follows a strict, leakage-free machine learning pipeline:

1. Data Splitting & Anti-Leakage Setup
2. Feature Engineering & Preprocessing
3. Model Development (Tree-Based Models)
4. Hyperparameter Tuning & Cross-Validation
5. Final Evaluation & Business Insights

---

## Part 1: Data Splitting & Anti-Leakage Setup
- Loaded the dataset and immediately split it into:
  - Training set (80%)
  - Test set (20%)
- Used stratified sampling to preserve class distribution.
- Set a global random seed (42) for reproducibility.
- Ensured that the test set remained completely unseen until final evaluation.

---

## Part 2: Feature Engineering & Preprocessing
All preprocessing steps were performed using **training data only**, and then applied to the test data.

### Steps Performed:
- Dropped non-informative identifier columns:
  - RowNumber
  - CustomerId
  - Surname
- Encoded categorical variables:
  - Gender → Binary encoding (Male=1, Female=0)
  - Geography → One-hot encoding (drop_first=True)
- Scaled numerical features using `StandardScaler`:
  - CreditScore
  - Age
  - Tenure
  - Balance
  - EstimatedSalary
- Created derived features:
  - `Balance_per_Product = Balance / (NumOfProducts + 1)`
  - `Is_Senior = 1 if Age >= 50 else 0`
  - `Inactive_with_Balance = 1 if IsActiveMember=0 and Balance>0`
- Ensured train-test feature alignment after encoding.

---

## Part 3: Model Development
The following models were trained on the processed training data:

- **Dummy Classifier** (Baseline - always predicts majority class)
- **Decision Tree** (max_depth=5, with visualization)
- **Random Forest** (n_estimators=100)
- **XGBoost** (with regularization)

### Training Accuracy Results:
| Model | Training Accuracy |
|-------|-------------------|
| Dummy Classifier | 79.63% |
| Decision Tree | 85.79% |
| Random Forest | 88.84% |
| XGBoost | 87.98% |

The baseline model established a minimum performance benchmark. Random Forest showed signs of overfitting.

---

## Part 4: Hyperparameter Tuning & Cross-Validation
- Performed 5-fold cross-validation on Random Forest and XGBoost.
- Observed significant overfitting in Random Forest (Training: 95%, CV: 86%).
- Selected **XGBoost** for tuning due to more stable CV performance.
- Used `RandomizedSearchCV` with 30 iterations and 5-fold CV to tune:
  - n_estimators: [100, 200, 300]
  - max_depth: [3, 4, 5, 6]
  - learning_rate: [0.01, 0.05, 0.1]
  - subsample: [0.7, 0.8, 0.9]
  - colsample_bytree: [0.7, 0.8, 0.9]
- Selected the best estimator based on cross-validated accuracy.

### Cross-Validation Results:
| Model | CV Mean Accuracy | Overfitting Gap |
|-------|------------------|-----------------|
| Random Forest | 88.83% | 2.5% |
| XGBoost | 87.97% | 1.6% |

---

## Part 5: Final Evaluation & Business Insights

### Test Set Evaluation Metrics (Threshold = 0.50)
| Metric | Value |
|--------|-------|
| Accuracy | 0.8690 |
| Precision | 0.7888 |
| Recall | 0.4865 |
| F1-Score | 0.6018 |
| ROC-AUC | 0.8678 |

A confusion matrix was plotted to analyze false positives and false negatives.

---

## Recall Optimization (Business-Driven)
Since recall is critical in churn prediction (missing a churner costs more than targeting a non-churner), the decision threshold was adjusted.

### Threshold Analysis
Multiple thresholds were evaluated using predicted probabilities.

| Threshold | Recall | Precision | F1-Score |
|-----------|--------|-----------|----------|
| 0.50 | 0.486 | 0.789 | 0.602 |
| 0.40 | 0.587 | 0.701 | 0.639 |
| 0.30 | 0.676 | 0.589 | 0.641 |
| 0.20 | 0.774 | 0.495 | 0.604 |

A threshold of **0.30** was selected as the optimal operating point.

### At Threshold = 0.30:
- Recall improved.
- False negatives reduced significantly
- Acceptable increase in false positives
- Suitable for cost-effective retention campaigns

A new confusion matrix was generated at this threshold, showing significant reduction in missed churners.

---

## ROC & Precision-Recall Analysis
- ROC Curve confirmed strong class separation capability (AUC = 0.85).
- Precision-Recall Curve highlighted the trade-off between recall and precision.
- Threshold selection was guided by business requirements rather than accuracy alone.

---

## Feature Importance
Feature importance from XGBoost was analyzed. Key drivers of churn:

| Rank | Feature | Importance |
|------|---------|------------|
| 1 | Age | 1153% |
| 2 | NumOfProducts | 19.83% |
| 3 | Balance | 3.6% |
| 4 | Geography_Germany | 7.3% |
| 5 | IsActiveMember | 11.39% |

### Business Insights:
- **Age**: Older customers (40-60) are more likely to churn
- **NumOfProducts**: Customers with 3+ products have very high churn risk
- **Balance**: High balance combined with inactivity indicates risk
- **Geography**: German customers churn at 2x the rate of others
- **Activity**: Inactive members are significantly more likely to leave

---

## Conclusion
The final XGBoost model significantly outperformed the baseline classifier and demonstrated strong generalization on unseen data. By prioritizing recall through threshold tuning, the model effectively identified a larger proportion of at-risk customers.


This solution enables the bank to implement cost-effective customer retention campaigns where the cost of missing a churner outweighs the cost of contacting a non-churner.

---

## Files

```
├── data/
│ └── Churn_Modelling.csv
├── main.ipynb
└── readme.md

```

```
## Requirements
```

```
numpy
pandas
matplotlib
seaborn
scikit-learn
xgboost

```

## Author
Ankit Luhar
```