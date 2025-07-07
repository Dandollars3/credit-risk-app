from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.utils.model_loader import credit_model
from app.forms import UpdateAccountForm  
from app import db

bp = Blueprint('main', __name__)

# Home Dashboard
@bp.route('/')
@bp.route('/dashboard')
def dashboard():
    top_features = credit_model.feature_importance.head(10).to_dict(orient='records')
    return render_template('main/dashboard.html', metrics=credit_model.metrics, top_features=top_features)

# Prediction Page
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

# Learn More Page
@bp.route('/learn')
def learn():
    return render_template('main/learn.html')

# Settings Page
@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.password.data:
            current_user.set_password(form.password.data)
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(url_for("main.settings"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("main/settings.html", form=form)
