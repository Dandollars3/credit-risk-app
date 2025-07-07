from flask import Blueprint, render_template, request, flash
from flask_login import login_required
from app.utils.model_loader import credit_model

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    top_features = credit_model.feature_importance.head(10).to_dict(orient='records')
    return render_template('main/dashboard.html', metrics=credit_model.metrics, top_features=top_features)

@bp.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    if request.method == 'POST':
        result = credit_model.predict(request.form)

        if not result['success']:
            flash(f"Error: {result['error']}", 'danger')
            return render_template('main/predict.html')

        return render_template('main/results.html', result=result)

    return render_template('main/predict.html')
