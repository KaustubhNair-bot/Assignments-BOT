# Bank Customer Churn Prediction: Multi-Algorithm Evaluation

## 1. Project Overview
This assignment focuses on the development of a predictive system to identify customer churn within a banking institution. By leveraging machine learning, the goal is to differentiate between loyal customers and those likely to exit, allowing for data-driven retention strategies. The project compares multiple algorithmic approaches, ranging from basic statistical baselines to optimized ensemble methods.

---

## 2. Data Acquisition and Partitioning
The process begins with the ingestion of the bank marketing dataset. To ensure a robust evaluation and prevent data leakage, the dataset is immediately partitioned into:
* **Training Set (80%):** Used for model training and hyperparameter tuning.
* **Testing Set (20%):** Reserved as "unseen" data for final performance verification.

---

## 3. Feature Engineering and Preprocessing
To improve the predictive capability of the models, a comprehensive preprocessing pipeline was implemented:

* **Categorical Encoding:** 
    * **One-Hot Encoding:** Applied to features with multiple categories (e.g., Geography) to transform them into a machine-readable format.
    * **Binary Encoding:** Applied to dual-category features such as Gender.
* **Feature Selection:** Non-informative columns such as `RowNumber`, `CustomerId`, and `Surname` were dropped to reduce noise and improve computational efficiency.
* **Derived Features:** New features were engineered to capture complex relationships:
    * `CreditScore_Age_Ratio`
    * `Balance_Salary_Ratio`
    * `Tenure_Age_Ratio`
    * `Engagement_Score`
* **Data Transformation:**
    * **Scaling:** Standard scaling was applied to numerical features to ensure all variables contribute equally to the model's decision-making.
    * **SMOTE (Synthetic Minority Over-sampling Technique):** Applied to the training set to address class imbalance, ensuring the models do not become biased toward the majority "Stayed" class.

---

## 4. Model Implementation and Performance
The following models were implemented and evaluated against key metrics: Accuracy, Precision, Recall, F1-Score, and ROC-AUC.

### Model Metrics Summary
| Model Name | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Dummy Classifier (Baseline)** | 0.796 | 0.000 | 0.000 | 0.000 | 0.500 |
| **Decision Tree** | 0.818 | 0.551 | 0.558 | 0.554 | 0.797 |
| **Random Forest (Simple)** | 0.846 | 0.624 | 0.612 | 0.618 | 0.870 |
| **LightGBM** | 0.865 | 0.693 | 0.604 | 0.646 | 0.874 |
| **Random Forest (Optimized)** | 0.845 | 0.616 | 0.631 | 0.624 | **0.876** |

---

## 5. Hyperparameter Tuning
Hyperparameter tuning was performed on the Random Forest model to move beyond default settings and improve generalizability. We utilized `GridSearchCV` to find the optimal configuration.

* **Parameters Tuned:** `n_estimators`, `max_depth`, `min_samples_leaf`, `max_features`, `criterion` and `class_weight`. 
* **Objective:** We tuned these parameters to prevent overfitting and to specifically improve the **ROC-AUC** and **Recall**, ensuring the model catches the maximum number of true churners.
* **Optimal Hyperparameters:** 
    * `n_estimators`: 400
    * `max_depth`: 25
    * `min_samples_leaf`: 2
    * `max_features`: sqrt,
    * `criterion`: entropy,
    * `class_weight`: balanced

---

## 6. Selection of the Primary Model
The **Optimized Random Forest** is selected as the primary model for this assignment. 

While the **LightGBM** model achieved higher raw accuracy, the Optimized Random Forest demonstrated a superior **ROC-AUC of 0.876**. More importantly, it provides the most stable balance between **Precision (0.616)** and **Recall (0.631)**. This ensures that the model is effective at identifying customers who are actually planning to leave (Recall) while maintaining a reliable level of accuracy in its predictions (Precision). Compared to the **Dummy Baseline (ROC-AUC 0.500)**, the Optimized Random Forest shows a significant 37.6% improvement in diagnostic power.

---

## 7. Conclusion
This assignment demonstrates a complete machine learning lifecycle, from data cleaning and feature engineering to advanced model optimization. The results prove that while simple models can provide basic insights, ensemble methods—when properly tuned and balanced—offer the highest reliability for sensitive tasks like bank churn prediction. The project concludes that **Age** and **Product Density** are the most significant drivers in predicting whether a customer will remain with the institution.