# Bank Customer Churn Prediction

## Project Overview
Customer churn is a major challenge for banks, as retaining existing customers is more cost-effective than acquiring new ones.  
This project focuses on predicting whether a bank customer will churn using machine  learning techniques applied to customer demographic and financial data.

The problem is treated as a binary classification task, where the target variable indicates whether a customer exited the bank.

## Objectives
- Understand the factors that influence customer churn.
- Build a complete machine learning pipeline from data preprocessing to model evaluation.
- Compare multiple tree-based models and identify the best-performing algorithm.
- Extract actionable business insights from the model results.

## Dataset Description
- Dataset: Bank Customer Churn Dataset (Kaggle)
- Total Records: 10,000
- Total Features: 14
- Target Variable: `Exited`  
  - 1 → Customer churned  
  - 0 → Customer retained  

Key features include:
- Demographics: Age, Gender, Geography
- Financial attributes: CreditScore, Balance, EstimatedSalary
- Banking behavior: NumOfProducts, HasCrCard, IsActiveMember, Tenure

## Methodology

### 1. Data Splitting
The dataset was split into training and testing sets before preprocessing to avoid data leakage:
- Training set: 80%
- Test set: 20%

### 2. Data Preprocessing & Feature Engineering
- Removed irrelevant columns such as RowNumber, CustomerId, and Surname.
- Encoded categorical variables (Gender, Geography) using appropriate encoding techniques.
- Scaled numerical features using StandardScaler.
- Created a derived feature: `Balance_per_Product`.
- Checked and handled missing values and data consistency.

### 3. Model Development
Multiple models were trained and compared:

- Dummy Classifier (Baseline Model)  
  Used to establish a benchmark by predicting the majority class.

- Decision Tree  
  A simple interpretable tree-based model.

- Random Forest  
  An ensemble model that improves performance by combining multiple decision trees.

- Gradient Boosting  
  An advanced boosting model used to capture complex patterns in data.

### 4. Model Evaluation
Models were evaluated using multiple metrics:
- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC Score
- Confusion Matrix

This ensured that model performance was not judged solely on accuracy, especially considering class imbalance.

## Key Results & Insights
- Age emerged as the most influential feature in predicting churn.
- Customers with high balances but fewer products showed higher churn probability.
- Inactive customers were more likely to leave the bank.
- Geography significantly influenced churn, with certain regions showing higher risk.
- Random Forest achieved the best overall performance among the tested models.

## Business Implications
The model can help banks:
- Identify high-risk customers early.
- Design targeted retention strategies.
- Improve customer engagement and reduce churn.
- Support data-driven decision-making in customer relationship management.

## Technologies Used
- Programming Language: Python
- Libraries: Pandas, NumPy, Scikit-learn, Matplotlib, Seaborn
- Environment: Jupyter Notebook

## Conclusion
This project demonstrates a complete real-world machine learning workflow — from raw data preprocessing to model building and business interpretation.  
It highlights how predictive analytics can be effectively applied in the banking sector to address customer churn and improve strategic decision-making.
