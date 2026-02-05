# End-to-End ML Pipeline: Customer Churn Prediction

## Overview
This Jupyter notebook presents a comprehensive, production-ready machine learning pipeline for predicting customer churn in a banking context. It demonstrates best practices for machine learning development, including proper data handling, feature engineering, model training, hyperparameter tuning, and actionable business insights.

## Key Features
- **Anti-Leakage Setup**: Proper train-test splitting and pipeline architecture to prevent data leakage
- **Feature Engineering**: Custom feature creation with derived indicators like Balance_per_Product, Age_per_Tenure, Salary_per_Product, and Balance_to_Salary_Ratio
- **Multiple Models**: Comparison of Dummy Classifier, Decision Tree, Random Forest, and XGBoost
- **Hyperparameter Tuning**: Grid search cross-validation for optimal model selection
- **Comprehensive Evaluation**: Multiple metrics (Accuracy, Precision, Recall, F1-Score, ROC-AUC) and visualizations
- **Business Insights**: Feature importance analysis and actionable customer segmentation

## Pipeline Structure

### Part 1: Data Splitting & Anti-Leakage Setup
- Loads the Churn_Modelling dataset
- Splits data into 80% training and 20% testing with stratification
- Ensures test set remains completely unseen during model development
- Implements reproducible splits using `random_state=42`

### Part 2: Feature Engineering & Preprocessing
**Custom Feature Engineering Class:**
- Drops irrelevant columns (RowNumber, CustomerId, Surname)
- Creates derived features:
  - Balance_per_Product: Average balance per product held
  - Age_per_Tenure: Customer experience relative to age
  - Salary_per_Product: Salary relationship to product count
  - Balance_to_Salary_Ratio: Financial burden indicator

**Preprocessing Transformers:**
- **Numeric Transformer**: Median imputation + StandardScaler
- **Categorical Transformer**: Mode imputation + One-Hot Encoding
- **Binary Transformer**: Mode imputation + Binary Encoding
- **ColumnTransformer**: Unified application to all feature types

### Part 3: Model Development
Four models are trained and compared:

1. **Dummy Classifier**: Baseline model (always predicts majority class)
   - Purpose: Establish minimum performance threshold
   - Typical Accuracy: ~79.65%

2. **Decision Tree Classifier**
   - Max depth: 3 for interpretability
   - Provides feature importance and decision visualization
   - Helps understand model reasoning

3. **Random Forest Classifier**
   - 200 estimators for ensemble learning
   - Max depth: 10 for balanced performance
   - Reduces overfitting compared to single trees
   - Parallel processing (n_jobs=-1)

4. **XGBoost Classifier**
   - 100 estimators with sequential error correction
   - Learning rate: 0.1 for stable convergence
   - Max depth: 5
   - Often provides best performance on tabular data

### Part 4: Hyperparameter Tuning & Cross-Validation
- **5-Fold Cross-Validation**: Reduces bias and detects overfitting
- **GridSearchCV**: Tests combinations of:
  - n_estimators: [100, 200]
  - max_depth: [3, 5, 7]
  - learning_rate: [0.05, 0.1]
- **Evaluation Metric**: ROC-AUC for comprehensive performance assessment

### Part 5: Final Evaluation & Business Insights
- **Train vs Test Performance**: Validates generalization capability
- **Confusion Matrix**: Visualizes True Positives, True Negatives, False Positives, False Negatives
- **ROC Curve Comparison**: Compares model discrimination ability
- **Feature Importance**: Identifies key drivers of churn prediction
- **Business Segmentation Analysis**: Churn patterns by geography, product count, and activity status

## Key Metrics Explained

| Metric | Definition | Business Relevance |
|--------|-----------|-------------------|
| **Accuracy** | Proportion of correct predictions | Overall model reliability |
| **Precision** | True positives / (True positives + False positives) | Avoids wasting retention budget on non-churners |
| **Recall** | True positives / (True positives + False negatives) | Catching as many churners as possible |
| **F1-Score** | Harmonic mean of Precision and Recall | Balanced performance measure |
| **ROC-AUC** | Area under the ROC curve | Model's discrimination ability across thresholds |

## Business Insights

### Critical Findings
1. **Inactive customers churn 2x more** (~27%) than active customers (~14%)
2. **Single-product customers are at risk** (~28% churn) vs. multi-product customers
3. **Geographic variation exists**: Germany ~32% churn vs. France/Spain ~16%
4. **Balance alone doesn't ensure retention**: High-balance inactive customers still at risk
5. **Tenure matters**: Customers with short tenure relative to age show higher churn risk

### Recommended Retention Strategies
- **Prioritize engagement programs** for inactive members
- **Cross-sell multiple products** to strengthen customer ties
- **Investigate regional factors** in Germany for competitive pressures
- **Create early onboarding initiatives** for new customers
- **Develop targeted retention campaigns** for high-risk segments identified by the model

## Dataset Description
**File**: `Churn_Modelling.csv`
**Target Variable**: `Exited` (0 = No Churn, 1 = Churn)
**Number of Rows**: 10,000 customers
**Number of Features**: 13 (plus derived features)

### Key Features
- CreditScore: Customer's credit score
- Age: Customer age
- Tenure: Years with the bank
- Balance: Current account balance
- NumOfProducts: Number of products held
- IsActiveMember: Binary activity status
- EstimatedSalary: Estimated annual salary
- Geography: Customer location
- Gender: Customer gender

## Model Performance Summary
The notebook compares all four models using:
- Confusion matrices for detailed prediction analysis
- ROC curves for threshold-independent evaluation
- Feature importance for interpretability
- Train vs. test performance for overfitting detection

## Dependencies
pandas
matplotlib
seaborn
scikit-learn
xgboost

## Key Learnings
**Proper anti-leakage practices** prevent unrealistic performance estimates  
**Custom feature engineering** improves model performance and business interpretability  
**Ensemble methods** (Random Forest, XGBoost) outperform single decision trees  
**Cross-validation** provides robust performance estimates  
**Feature importance analysis** enables actionable business insights  
**Model comparison** helps select the best performer for production deployment  

## Conclusion
This pipeline demonstrates how to build a production-ready churn prediction model that not only achieves strong predictive performance but also provides clear business interpretability. By combining rigorous machine learning practices with domain understanding, the solution enables the bank to proactively identify and retain high-risk customers through data-driven strategies.

