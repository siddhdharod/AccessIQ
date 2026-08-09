# AccessIQ – Smart Accessibility Assessment System

> An AI-powered accessibility platform for evaluating, comparing, and improving accessibility of public places.

## 📌 Overview

**AccessIQ** is a Machine Learning-powered web application designed to assess the accessibility of public locations and provide intelligent, data-driven recommendations.

The platform analyzes infrastructure, safety, facilities, crowd conditions, waiting time, and other accessibility-related parameters to generate an **Accessibility Score** and classify locations into different accessibility levels.

AccessIQ combines Machine Learning, Explainable AI, interactive visualizations, recommendations, AI assistance, and accessibility booking services into a single platform.

---

## 🎯 Objectives

- Predict the accessibility score of public locations.
- Classify locations based on their accessibility level.
- Compare accessibility between multiple locations.
- Identify similar locations using clustering.
- Recommend suitable locations based on user requirements.
- Explain ML predictions using Explainable AI.
- Provide interactive accessibility analytics and visualizations.
- Enable wheelchair and accessible parking slot booking.
- Provide AI-powered assistance through an integrated chatbot.
- Support data-driven accessibility planning.

---

## ✨ Key Features

### 🤖 Machine Learning

- Accessibility Score Prediction
- Accessibility Classification
- Location Clustering
- Location Recommendation
- Model Comparison
- K-Fold Cross Validation
- Hyperparameter Tuning
- Feature Importance Analysis

### 📊 Analytics & Visualization

- Interactive dashboards
- Accessibility score visualization
- Model performance comparison
- Confusion Matrix
- ROC Curve
- Feature Importance
- PCA/LDA/SVD visualizations
- Location comparison
- Radar charts

### 🔍 Explainable AI

AccessIQ uses **SHAP (SHapley Additive exPlanations)** to explain machine learning predictions and identify which accessibility features have the greatest influence on the predicted result.

### 📍 Location Comparison

Users can compare multiple public locations based on accessibility-related parameters and visualize their differences through interactive charts.

### 💡 Smart Recommendations

The recommendation module suggests suitable locations based on factors such as:

- Accessibility Score
- Safety
- Facilities
- Waiting Time
- Crowd Level
- User Rating
- Accessibility Infrastructure

### ♿ Accessibility Booking

Users can reserve:

- Wheelchairs
- Accessible Parking Slots

The booking system includes:

- User authentication
- Slot selection
- Date and time selection
- Duration selection
- ₹ INR pricing
- Booking confirmation
- Booking ID
- QR Code
- PDF receipt
- Booking history
- Booking cancellation

Bookings are currently stored locally and do not require a database.

### 🤖 AI Chatbot

The integrated **AccessIQ chatbot** assists users with accessibility-related queries, recommendations, and booking information.

### 🌓 Modern UI

- Premium purple-themed interface
- Light Mode
- Dark Mode
- Responsive layout
- Interactive cards
- Modern charts
- Accessible navigation
- Streamlit-based interface

---

# 🧠 Machine Learning Algorithms

## Regression

Used for predicting the numerical Accessibility Score.

- Linear Regression
- Decision Tree Regressor
- Random Forest Regressor
- Support Vector Regressor
- XGBoost Regressor

### Evaluation Metrics

- MAE
- RMSE
- R² Score

---

## Classification

Used for classifying locations into accessibility categories.

- Logistic Regression
- Decision Tree
- Random Forest
- Support Vector Machine
- Bagging Classifier
- XGBoost

### Evaluation Metrics

- Accuracy
- Precision
- Recall
- F1 Score
- Confusion Matrix
- ROC-AUC
- Cohen's Kappa
- Sensitivity
- Specificity

---

## Clustering

Used to identify groups of locations with similar accessibility characteristics.

- DBSCAN
- Gaussian Mixture Model / Expectation Maximization
- Minimum Spanning Tree Clustering

---

## Dimensionality Reduction

- Principal Component Analysis (PCA)
- Linear Discriminant Analysis (LDA)
- Singular Value Decomposition (SVD)

---

## 🔬 Explainable AI

SHAP is used to interpret model predictions.

It helps answer:

> "Why did the model give this accessibility score?"

The system provides feature-level explanations and feature importance visualizations to improve transparency and user trust.

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │      User           │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Streamlit Web App  │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
       ML Prediction     Location Analysis    Booking
             │                 │                 │
             ▼                 ▼                 ▼
       Regression         Comparison          Wheelchair
       Classification     Clustering          Parking
             │                 │
             └──────────┬──────┘
                        ▼
                Explainable AI
                     SHAP
                        │
                        ▼
              Recommendations
                        │
                        ▼
                 User Insights

