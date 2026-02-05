#  Bank Customer Churn Prediction
## Project Overview

This project aims to predict whether a customer will leave the bank (churn) based on demographic and account activity data. The objective is to build a robust, leakage-free machine learning pipeline that not only achieves strong predictive performance but also provides meaningful business insights.

The dataset used is the Bank Customer Churn Prediction Dataset from Kaggle.

## Problem Statement

Predict whether a customer will churn (Exited = 1) using customer demographic and financial attributes.

This is a binary classification problem with class imbalance (~20% churn rate).

## Methodology
1. Data Splitting & Anti-Leakage Strategy

- The dataset was split into 80% training and 20% test sets immediately after loading.
- All EDA, feature engineering, and model tuning were performed only on the training data.
- The test set remained completely unseen until final evaluation.
- A global RANDOM_SEED was used for reproducibility.
- Hyperparameter tuning was performed using 5-fold cross-validation, eliminating the need for a separate validation set.

2. Exploratory Data Analysis (EDA)

- The dataset is imbalanced (~80% non-churn, ~20% churn).
- Older customers showed higher churn tendency.
- Inactive members churn significantly more.
- Customers with fewer products were more likely to leave.
- Regional differences (e.g., Germany) influenced churn rates.
- Correlation analysis suggested moderate linear relationships, reinforcing the choice of tree-based models to capture non-linear patterns.

3. Feature Engineering & Preprocessing

- New features were created to capture deeper behavioral patterns:
    - Balance_per_Product → Measures financial distribution per product.
    - Tenure_per_Age → Reflects loyalty relative to age.
    - Activity_Balance → Identifies high-value but inactive customers.

- Categorical handling:
- Gender → Binary encoding.
- Geography → One-Hot Encoding.
- Numerical features were scaled using StandardScaler, fitted only on the training set to prevent leakage.

4. Model Development

The following models were trained and compared:

- Dummy Classifier (Baseline)
    - Predicts majority class only (Non-Churn).
    - Served as reference to verify meaningful learning.

- Decision Tree
    - Showed very high precision but low recall — indicating conservative churn prediction.

- Random Forest
    - Reduced variance and improved recall by aggregating multiple trees.

- LightGBM
    - Provided best balance between bias and variance through gradient boosting.

5. Hyperparameter Tuning

- Model selected: LightGBM

- Tuning method: RandomizedSearchCV
    - Cross-validation: 5-fold
    - Evaluation metric: ROC-AUC

- Threshold tuning was applied to improve churn recall.

## Final Model Performance (Tuned LightGBM + Threshold Adjustment)

- Accuracy: 0.85
- Precision: 0.64
- Recall: 0.60
- F1-Score: 0.62
- ROC-AUC: 0.86

While overall accuracy improved moderately over baseline (~0.80), the major improvement lies in churn detection. The baseline model failed to detect churners, whereas the final model correctly identifies approximately 60% of churn cases.

##  Key Business Insights

Feature importance analysis revealed that the most influential predictors include:
    - CreditScore
    - EstimatedSalary
    - Age
    - Balance
    - Tenure_per_Age
    - Balance_per_Product

## Customers Most Likely to Churn:

- Older customers
- Customers with fewer products
- High-balance but low-activity customers
- Customers from higher-risk regions

## Business Impact

The model enables targeted retention strategies by identifying high-risk customer segments. Improving recall ensures that more potential churners are captured, allowing proactive engagement before customer loss occurs.