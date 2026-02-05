# Bank Customer Churn Prediction

## Problem Statement
The objective of this project is to **predict whether a bank customer will leave the bank (churn)** based on their demographic, financial, and activity-related attributes.

This is a **binary classification problem** where:
- `1` → Customer exits the bank  
- `0` → Customer stays with the bank  



## Dataset Overview
The dataset contains customer-level information such as:
- Demographics: Geography, Gender, Age  
- Financial data: Credit Score, Balance, Estimated Salary  
- Product usage: Number of products, credit card status, activity level  
- Target variable: `Exited` (churn indicator)

## Machine Learning Workflow

This project follows a **leakage-safe, production-style ML pipeline**, ensuring that the test data remains completely unseen until final evaluation.


## Part 1: Data Splitting & Anti-Leakage Setup

### Objective
To ensure unbiased model evaluation by preventing **data leakage**.

### Steps Performed
- Loaded the dataset.
- Set a **global random seed** for reproducibility.
- Split the dataset **immediately** into:
  - **Training set (80%)**
  - **Test set (20%)**
- All preprocessing, feature engineering, model selection, and hyperparameter tuning were performed **only on the training data**.
- The test set was used **only once**, during final evaluation.

This setup simulates real-world deployment where future data is unseen during training.


## Part 2: Feature Engineering & Preprocessing

### Objective
Transform raw data into model-ready features.

### Feature Selection
The following columns were removed because they provide **no predictive value**:
- `RowNumber`
- `CustomerId`
- `Surname`

### Categorical Encoding
- **Geography** → One-Hot Encoding  
- **Gender** → Binary Encoding (Label Encoding)

### Numerical Scaling
- Applied **StandardScaler** to numerical features:
  - `CreditScore`
  - `Balance`
  - `EstimatedSalary`
  - `Age`

Scaling ensures fair contribution of features during model training.

### Feature Creation
A new derived feature was created:


This feature captures **customer engagement intensity** and improves model expressiveness.


## Part 3: Model Development (Tree-Based Models)

### Objective
Compare different machine learning models.

### Models Trained

#### 1. Baseline Model – Dummy Classifier
- Strategy: Always predicts **“Not Churn”**
- Purpose: Establishes a **minimum benchmark**
- Demonstrates whether advanced models actually learn meaningful patterns

#### 2. Decision Tree Classifier
- Trained a single decision tree
- Tree visualization with **maximum depth = 3**
- Helps in understanding feature splits and interpretability

#### 3. Random Forest Classifier
- Ensemble of multiple decision trees
- Reduces overfitting
- Handles non-linear feature interactions well

#### 4. Gradient Boosting Model
- Used **XGBoost / LightGBM**
- Sequentially improves weak learners
- Strong performance on structured/tabular data


## Part 4: Hyperparameter Tuning & Cross-Validation

### Objective
Improve generalization and avoid overfitting.

### Selected Model
**Random Forest / XGBoost** (best-performing model from Part 3)

### Methodology
- Used **5-Fold Cross-Validation**
- Applied **GridSearchCV / RandomizedSearchCV**
- Tuned hyperparameters such as:
  - `n_estimators`
  - `max_depth`
  - `min_samples_split`
  - `learning_rate` (for boosting)

Cross-validation ensures the model performs consistently across different data splits.


## Part 5: Final Evaluation & Business Insights

### Test Set Evaluation
The optimized model was evaluated on the **unseen test set**.

### Metrics Reported
- Accuracy
- Precision
- Recall
- F1-Score

These metrics provide a balanced evaluation, especially important for **imbalanced churn data**.


### Confusion Matrix
- Visualized True Positives, False Positives, True Negatives, and False Negatives
- Helps understand **business cost trade-offs**, such as missing a churned customer


### Feature Importance Analysis
- Generated feature importance plot from the final model
- Key influential features included:
  - Age
  - Balance
  - Number of Products
  - Geography
  - IsActiveMember
  - Balance_per_Product


## Conclusion & Business Insights

- The final model **significantly outperformed the baseline**, proving it learned meaningful patterns.
- Customers most likely to churn are:
  - Older customers
  - Customers with high balances but low product usage
  - Inactive customers
  - Customers from specific geographical regions
- These insights can help the bank:
  - Design targeted retention campaigns
  - Offer personalized financial products
  - Reduce customer attrition and revenue loss


## Technologies Used
- Python
- Pandas, NumPy
- Scikit-learn
- XGBoost / LightGBM
- Matplotlib, Seaborn
- Jupyter Notebook
