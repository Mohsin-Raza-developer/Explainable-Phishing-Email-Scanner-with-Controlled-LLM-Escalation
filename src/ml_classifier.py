import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
import numpy as np
import pickle
import os
import csv
import sys

# Increase CSV field size limit for large email bodies
csv.field_size_limit(sys.maxsize)


class PhishingClassifier:
    def __init__(self, dataset_path='CEAS_08.csv'):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        self.clf = LogisticRegression(max_iter=1000)
        self.is_trained = False
        self.dataset_path = dataset_path
        self.metrics = {}

    def train(self, test_size=0.2, random_state=42):
        """
        Trains the lightweight ML model on CEAS_08.csv dataset.
        Includes train/test split and evaluation metrics.
        """
        print("=" * 60)
        print("Loading CEAS_08.csv Dataset...")
        print("=" * 60)

        # Load dataset
        df = pd.read_csv(self.dataset_path, encoding='utf-8', on_bad_lines='skip')

        print(f"Total emails loaded: {len(df):,}")
        print(f"Phishing emails: {(df['label'] == 1).sum():,}")
        print(f"Safe emails: {(df['label'] == 0).sum():,}")

        # Combine subject and body for better feature extraction
        df['text'] = df['subject'].fillna('') + ' ' + df['body'].fillna('')

        # Prepare data
        emails = df['text'].values
        labels = df['label'].values

        # Split into train and test sets
        print(f"\nSplitting data: {int((1-test_size)*100)}% train, {int(test_size*100)}% test...")
        X_train_text, X_test_text, y_train, y_test = train_test_split(
            emails, labels, test_size=test_size, random_state=random_state, stratify=labels
        )

        print(f"Training set: {len(X_train_text):,} emails")
        print(f"Test set: {len(X_test_text):,} emails")

        # Train the model
        print("\n" + "=" * 60)
        print("Training ML Model...")
        print("=" * 60)

        X_train = self.vectorizer.fit_transform(X_train_text)
        self.clf.fit(X_train, y_train)

        print("Training Complete!")

        # Evaluate on test set
        print("\n" + "=" * 60)
        print("Evaluating Model Performance...")
        print("=" * 60)

        X_test = self.vectorizer.transform(X_test_text)
        y_pred = self.clf.predict(X_test)

        # Calculate metrics
        self.metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred)
        }

        print(f"\nAccuracy:  {self.metrics['accuracy']*100:.2f}%")
        print(f"Precision: {self.metrics['precision']*100:.2f}%")
        print(f"Recall:    {self.metrics['recall']*100:.2f}%")
        print(f"F1-Score:  {self.metrics['f1_score']*100:.2f}%")

        print("\n" + "-" * 60)
        print("Classification Report:")
        print("-" * 60)
        print(classification_report(y_test, y_pred, target_names=['Safe', 'Phishing']))

        print("-" * 60)
        print("Confusion Matrix:")
        print("-" * 60)
        cm = confusion_matrix(y_test, y_pred)
        print(f"                Predicted")
        print(f"                Safe  Phishing")
        print(f"Actual Safe     {cm[0][0]:>5}  {cm[0][1]:>5}")
        print(f"       Phishing {cm[1][0]:>5}  {cm[1][1]:>5}")

        self.is_trained = True
        print("\n" + "=" * 60)
        print("Model Ready for Use!")
        print("=" * 60)

    def save_model(self, filepath='phishing_model.pkl'):
        """Save trained model to disk"""
        if not self.is_trained:
            print("Error: Model not trained yet!")
            return False

        model_data = {
            'vectorizer': self.vectorizer,
            'classifier': self.clf,
            'metrics': self.metrics
        }
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"Model saved to {filepath}")
        return True

    def load_model(self, filepath='phishing_model.pkl'):
        """Load trained model from disk"""
        if not os.path.exists(filepath):
            print(f"Error: Model file {filepath} not found!")
            return False

        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)

        self.vectorizer = model_data['vectorizer']
        self.clf = model_data['classifier']
        self.metrics = model_data.get('metrics', {})
        self.is_trained = True
        print(f"Model loaded from {filepath}")
        return True

    def analyze_email(self, text):
        """
        Analyzes an email and returns a risk score (0-1) and top signals.
        """
        if not self.is_trained:
            raise Exception("Model is not trained! Call train() first.")

        # 1. Get Risk Score (Probability)
        text_vector = self.vectorizer.transform([text])
        risk_score = self.clf.predict_proba(text_vector)[0][1] # Probability of Phishing (1, machine learning classifier

        # 2. Get Explainable Signals (Features)
        feature_names = np.array(self.vectorizer.get_feature_names_out()) # Feature names (words) all words list from training data model
        coefficients = self.clf.coef_.flatten() # Coefficients of the model 
        
        # Extract words present in this specific email
        # We need the indices of non-zero elements in the sparse vector
        # text_vector is a sparse matrix, so we convert to array for easier handling if needed, 
        # or just use coordinate format.
        input_indices = text_vector.nonzero()[1] # Indices of non-zero elements

        word_impacts = []
        for idx in input_indices:
            word = feature_names[idx] # Word from the feature names list 
            # Contribution = Weight * TF-IDF Value
            impact = coefficients[idx] * text_vector[0, idx]
            
            # We only care about words that INCREASE risk (Positive impact towards '1')
            if impact > 0:
                word_impacts.append((word, impact))

        # Sort by highest impact
        word_impacts.sort(key=lambda x: x[1], reverse=True) # Sort by impact in descending order [9, 5, 3, 1]
        
        # Format signals for easier reading
        top_signals = [{"word": w, "impact": round(i, 3)} for w, i in word_impacts[:5]]

        # 3. Create Human-Readable Classification & Explanation
        score_100 = round(risk_score * 100, 1)
        
        # Determine Label
        classification = "Safe"
        if score_100 > 70:
            classification = "Phishing"
        elif score_100 > 44:
            classification = "Suspicious" # This is where LLM would be triggered
            
        # Generate Plain English Explanation
        explanation = f"The email has a risk score of {score_100}/100 and is classified as '{classification}'."
        
        if top_signals:
            explanation += " This is primarily due to high-risk keywords found in the text: "
            word_list = [f"'{s['word']}'" for s in top_signals]
            explanation += ", ".join(word_list) + "."
        else:
            explanation += " No specific high-risk keywords were detected."

        return {
            "risk_score": score_100, # 0-100 Scale
            "classification": classification, # Safe / Suspicious / Phishing
            "explanation": explanation, # Plain English
            "ml_signals": top_signals # Keep technical details for LLM if needed
        }






        

# For testing independently
# if __name__ == "__main__":
#     classifier = PhishingClassifier()
#     classifier.train()
    
#     test_email = "Urgent: Verify your bank password immediately"
#     result = classifier.analyze_email(test_email)
    
#     print("\n--- Analysis Result ---")
#     print(f"Email: {test_email}")
#     print(f"Risk Score: {result['risk_score']}/100")
#     print(f"Classification: {result['classification']}")
#     print(f"Explanation: {result['explanation']}")
    
#     # Logic for LLM Usage (Controlled Escalation)
#     if result['classification'] == "Suspicious":
#         print("\n[System Action]: Escalating to LLM for further review...")
#     else:
#         print("\n[System Action]: No LLM needed. Final verdict delivered.")