import joblib
import json
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline

class CreditRiskModel:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.config = None
        self.feature_importance = None
        self.metrics = None

    def load(self):
        """Load all model components"""
        self.model = joblib.load('random_forest_model.joblib')
        self.preprocessor = joblib.load('preprocessor.joblib')

        with open('rf_model_config.json') as f:
            self.config = json.load(f)

        with open('rf_model_metrics.json') as f:
            self.metrics = json.load(f)

        self.feature_importance = pd.read_csv('rf_feature_importance.csv')

    def validate_input(self, input_data):
        """Validate and transform raw input data"""
        numerical_fields = {
            'num__DurationInMonth': ('Duration (months)', 1, 120),
            'num__CreditAmount': ('Credit Amount (₦)', 1, 1000000),
            'num__InstallmentRate': ('Installment Rate (%)', 1, 100),
            'num__PresentResidenceSince': ('Residence Since (years)', 0, 100),
            'num__AgeInYears': ('Age (years)', 18, 100),
            'num__NumExistingCredits': ('Existing Credits', 0, 10),
            'num__NumPeopleMaintenance': ('People Maintenance', 0, 10)
        }

        validated = {}
        for field, (label, min_val, max_val) in numerical_fields.items():
            try:
                value = float(input_data.get(field, 0))
                if not (min_val <= value <= max_val):
                    raise ValueError(f"{label} must be between {min_val} and {max_val}")
                validated[field] = value
            except (ValueError, TypeError):
                raise ValueError(f"Invalid value for {label}")

        categorical_fields = {
            'cat__Status_CheckingAccount': ('Checking Account Status', ['0', '1', '2', '3']),
            'cat__CreditHistory': ('Credit History', ['0', '1', '2', '3', '4']),
            'cat__SavingsAccount': ('Savings Account', ['0', '1', '2', '3', '4']),
            'cat__EmploymentSince': ('Employment Since', ['0', '1', '2', '3', '4'])
        }

        for field, (label, valid_values) in categorical_fields.items():
            value = str(input_data.get(field, ''))
            if value not in valid_values:
                raise ValueError(f"Invalid selection for {label}")
            validated[field] = value

        # Derived features
        validated['num__CreditAmount_log'] = np.log1p(validated['num__CreditAmount'])
        validated['num__DurationInMonth_log'] = np.log1p(validated['num__DurationInMonth'])
        validated['num__AgeInYears_log'] = np.log1p(validated['num__AgeInYears'])

        # One-hot encoding
        for field in ['cat__Status_CheckingAccount', 'cat__CreditHistory', 'cat__SavingsAccount', 'cat__EmploymentSince']:
            value = validated[field]
            for i in range(5 if 'SavingsAccount' in field or 'CreditHistory' in field or 'EmploymentSince' in field else 4):
                validated[f"{field}_{i}"] = '1' if value == str(i) else '0'

        return validated

    def predict(self, input_data):
        """Make a prediction from validated input data"""
        try:
            validated_data = self.validate_input(input_data)
            input_df = pd.DataFrame([validated_data], columns=self.config['required_features'])

            probability = self.model.predict_proba(input_df)[0][1]
            prediction = probability >= self.config['threshold']

            # Debug print
            print(f"Predicted probability: {probability:.4f}")

            # Suggestions if high risk
            suggestions = []
            if prediction:
                if validated_data['num__CreditAmount'] > 500000:
                    suggestions.append("Consider reducing the credit amount requested.")
                if validated_data['num__InstallmentRate'] > 50:
                    suggestions.append("Lower your installment rate as a percentage of income.")
                if validated_data['num__NumPeopleMaintenance'] > 3:
                    suggestions.append("Reduce financial dependents if possible.")
                if validated_data['num__NumExistingCredits'] > 2:
                    suggestions.append("Limit the number of existing credit obligations.")
                if validated_data['num__PresentResidenceSince'] < 1:
                    suggestions.append("Longer residence history may improve trustworthiness.")
                if validated_data['cat__Status_CheckingAccount'] in ['0', '1']:
                    suggestions.append("Maintain a higher balance in your checking account.")
                if validated_data['cat__SavingsAccount'] in ['0', '1']:
                    suggestions.append("Increase your savings account balance.")
                if validated_data['cat__EmploymentSince'] in ['0', '1']:
                    suggestions.append("Longer employment history can improve your profile.")

            return {
                'prediction': bool(prediction),
                'probability': float(probability),
                'risk_category': 'High Risk' if prediction else 'Low Risk',
                'suggestions': suggestions,
                'success': True
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Singleton instance
credit_model = CreditRiskModel()
credit_model.load()
