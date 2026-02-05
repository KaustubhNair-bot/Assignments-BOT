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
- Set a global random seed for reproducibility.
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
  - Gender → Binary encoding
  - Geography → One-hot encoding
- Scaled numerical features using `StandardScaler`:
  - CreditScore
  - Age
  - Tenure
  - Balance
  - EstimatedSalary
- Created a derived feature:
  - `Balance_per_Product = Balance / (NumOfProducts + 1)`
- Ensured train–test feature alignment after encoding.

---

## Part 3: Model Development
The following models were trained on the processed training data:

- **Dummy Classifier** (Baseline)
- **Decision Tree** (max depth = 3, visualized)
- **Random Forest**
- **XGBoost**

### Training Accuracy Results:
- Dummy Classifier: ~79.6%
- Decision Tree: ~84.0%
- Random Forest: ~100% (indicative of overfitting)
- XGBoost: ~87.1%

The baseline model established a minimum performance benchmark.

---

## Part 4: Hyperparameter Tuning & Cross-Validation
- Performed 5-fold cross-validation on Random Forest and XGBoost.
- Observed overfitting in Random Forest via cross-validation.
- Selected **XGBoost** for tuning due to more stable CV performance.
- Used `RandomizedSearchCV` with 5-fold cross-validation to tune:
  - n_estimators
  - max_depth
  - learning_rate
  - subsample
  - colsample_bytree
- Selected the best estimator based on cross-validated accuracy.

---

## Part 5: Final Evaluation & Business Insights

### Test Set Evaluation Metrics (Threshold = 0.50)
- Accuracy: ~86%
- Precision: ~0.76
- Recall: ~0.48
- F1-score: ~0.58
- ROC-AUC: Reported

A confusion matrix was plotted to analyze false positives and false negatives.

---

## Recall Optimization (Business-Driven)
Since recall is critical in churn prediction, the decision threshold was adjusted.

### Threshold Analysis
Multiple thresholds were evaluated using predicted probabilities.  
A threshold of **0.30** was selected as the optimal operating point.

At threshold = 0.30:
- Recall improved from ~48% → ~66%
- Precision remained acceptable (~60%)
- F1-score was maximized among recall-prioritized thresholds

A new confusion matrix was generated at this threshold, showing a significant reduction in false negatives at the cost of increased false positives.

---

## ROC & Precision–Recall Analysis
- ROC Curve confirmed strong class separation capability.
- Precision–Recall Curve highlighted the trade-off between recall and precision.
- Threshold selection was guided by Precision–Recall analysis rather than accuracy alone.

---

## Feature Importance
- Feature importance from XGBoost was analyzed.
- Key drivers of churn included:
  - Age
  - Balance
  - Number of Products
  - IsActiveMember
  - Geography-related features

---

## Conclusion
The final XGBoost model significantly outperformed the baseline classifier and demonstrated strong generalization on unseen data. By prioritizing recall through threshold tuning, the model effectively identified a larger proportion of at-risk customers. This makes the solution suitable for proactive retention strategies, where the cost of missing a churner outweighs the cost of contacting a non-churner.

---

