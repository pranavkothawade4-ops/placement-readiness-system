import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from config import Config

def generate_synthetic_training_data(n_samples=800, seed=42):
    """
    Generates realistic historical campus placement training data.
    Correlates CGPA, DSA coding problems, Project count, Internships,
    Aptitude, and Soft Skills to Placement outcome and CTC.
    """
    np.random.seed(seed)
    
    # Features:
    # 1. cgpa (5.5 - 9.8)
    # 2. backlogs (0 - 4)
    # 3. dsa_problems (0 - 600)
    # 4. projects_count (0 - 6)
    # 5. internship_months (0 - 12)
    # 6. aptitude_score (20 - 100)
    # 7. comm_rating (1 - 5)
    # 8. certifications (0 - 5)
    
    cgpa = np.random.normal(7.8, 0.9, n_samples).clip(5.5, 9.9)
    backlogs = np.random.choice([0, 1, 2, 3], size=n_samples, p=[0.75, 0.15, 0.07, 0.03])
    dsa_problems = np.random.exponential(120, n_samples).clip(0, 650)
    projects_count = np.random.choice([0, 1, 2, 3, 4, 5], size=n_samples, p=[0.05, 0.20, 0.35, 0.25, 0.10, 0.05])
    internship_months = np.random.choice([0, 2, 3, 6, 9, 12], size=n_samples, p=[0.40, 0.25, 0.15, 0.12, 0.05, 0.03])
    aptitude_score = (cgpa * 8.5 + np.random.normal(10, 8, n_samples)).clip(30, 98)
    comm_rating = np.random.choice([1, 2, 3, 4, 5], size=n_samples, p=[0.05, 0.20, 0.40, 0.25, 0.10])
    certifications = np.random.choice([0, 1, 2, 3, 4], size=n_samples, p=[0.2, 0.35, 0.25, 0.15, 0.05])
    
    # Calculate Latent Placement Score (0 - 100)
    latent_score = (
        (cgpa - 5.0) * 5.0
        - backlogs * 8.0
        + (dsa_problems / 600.0) * 32.0
        + (projects_count / 5.0) * 18.0
        + (internship_months / 12.0) * 14.0
        + (aptitude_score / 100.0) * 15.0
        + (comm_rating / 5.0) * 14.0
        + (certifications / 4.0) * 7.0
        + np.random.normal(0, 3, n_samples)
    ).clip(0, 100)
    
    # Target Class:
    # 0 = Unplaced / At-Risk (score < 45 or backlogs > 1)
    # 1 = Tier 3 Service/Core (score 45 - 65, CTC 3.5 - 7 LPA)
    # 2 = Tier 2 High Growth/Product (score 65 - 82, CTC 7.5 - 16 LPA)
    # 3 = Tier 1 Super Dream (score >= 82, CTC 16 - 45 LPA)
    
    tiers = []
    ctc_values = []
    
    for i in range(n_samples):
        s = latent_score[i]
        b = backlogs[i]
        
        if b >= 2 or s < 45:
            tiers.append(0) # At-risk / unplaced
            ctc_values.append(np.random.uniform(2.5, 4.0))
        elif s < 65:
            tiers.append(1) # Tier 3
            ctc_values.append(np.random.uniform(4.0, 7.5))
        elif s < 82:
            tiers.append(2) # Tier 2
            ctc_values.append(np.random.uniform(8.0, 16.0))
        else:
            tiers.append(3) # Tier 1
            ctc_values.append(np.random.uniform(16.5, 38.0))
            
    df = pd.DataFrame({
        'cgpa': cgpa,
        'backlogs': backlogs,
        'dsa_problems': dsa_problems,
        'projects_count': projects_count,
        'internship_months': internship_months,
        'aptitude_score': aptitude_score,
        'comm_rating': comm_rating,
        'certifications': certifications,
        'placement_tier': tiers,
        'ctc_lpa': ctc_values
    })
    return df

class PlacementMLEngine:
    FEATURE_NAMES = [
        'cgpa', 'backlogs', 'dsa_problems', 'projects_count',
        'internship_months', 'aptitude_score', 'comm_rating', 'certifications'
    ]
    
    def __init__(self, model_file=Config.MODEL_PATH):
        self.model_file = model_file
        self.classifier = None
        self.regressor = None
        self._load_or_train()
        
    def _load_or_train(self):
        if os.path.exists(self.model_file):
            try:
                bundle = joblib.load(self.model_file)
                self.classifier = bundle['classifier']
                self.regressor = bundle['regressor']
                return
            except Exception as e:
                print(f"Error loading model, retraining: {e}")
                
        self.train_and_save()
        
    def train_and_save(self):
        data = generate_synthetic_training_data()
        X = data[self.FEATURE_NAMES]
        y_tier = data['placement_tier']
        y_ctc = data['ctc_lpa']
        
        clf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
        clf.fit(X, y_tier)
        
        reg = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
        reg.fit(X, y_ctc)
        
        self.classifier = clf
        self.regressor = reg
        
        joblib.dump({
            'classifier': clf,
            'regressor': reg,
            'features': self.FEATURE_NAMES
        }, self.model_file)
        
    def predict(self, feature_dict):
        """
        Receives dict of feature inputs and predicts:
        - Placement Probability (%)
        - Placement Tier
        - Expected CTC range (min, max in LPA)
        - Key feature influences
        """
        raw_vals = [
            float(feature_dict.get('cgpa', 7.5)),
            float(feature_dict.get('backlogs', 0)),
            float(feature_dict.get('dsa_problems', 50)),
            float(feature_dict.get('projects_count', 2)),
            float(feature_dict.get('internship_months', 0)),
            float(feature_dict.get('aptitude_score', 65)),
            float(feature_dict.get('comm_rating', 3)),
            float(feature_dict.get('certifications', 1))
        ]
        
        X_df = pd.DataFrame([raw_vals], columns=self.FEATURE_NAMES)
        
        # Probabilities across [Unplaced, Tier 3, Tier 2, Tier 1]
        probs = self.classifier.predict_proba(X_df)[0]
        # Overall placement probability = sum of probability of tier 1, 2, 3
        # If classifier classes are [0, 1, 2, 3]
        classes = self.classifier.classes_
        prob_placed = 0.0
        for cls_idx, cls_label in enumerate(classes):
            if cls_label > 0:
                prob_placed += probs[cls_idx]
                
        placement_prob_pct = round(min(max(prob_placed * 100, 5.0), 99.0), 1)
        predicted_tier_id = self.classifier.predict(X_df)[0]
        
        tier_names = {
            3: "Super Dream (Tier 1 Product)",
            2: "Dream (Tier 2 High-Growth)",
            1: "Core / Service (Tier 3)",
            0: "Developing / Needs Polish"
        }
        tier_str = tier_names.get(predicted_tier_id, "Developing")
        
        # Predicted CTC
        base_ctc = float(self.regressor.predict(X_df)[0])
        # Generate reasonable salary range
        ctc_min = round(max(2.8, base_ctc * 0.88), 1)
        ctc_max = round(base_ctc * 1.25, 1)
        
        # Feature importance impact
        importances = self.classifier.feature_importances_
        feature_impact = []
        for name, imp in zip(self.FEATURE_NAMES, importances):
            feature_impact.append({
                'feature': name.replace('_', ' ').title(),
                'weight': round(float(imp) * 100, 1)
            })
        feature_impact = sorted(feature_impact, key=lambda x: x['weight'], reverse=True)
        
        return {
            'placement_probability': placement_prob_pct,
            'tier': tier_str,
            'tier_id': int(predicted_tier_id),
            'expected_ctc_min': ctc_min,
            'expected_ctc_max': ctc_max,
            'feature_impact': feature_impact
        }

# Global singleton
ml_engine = PlacementMLEngine()
