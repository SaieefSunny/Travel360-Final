from flask import Blueprint, render_template, request, flash, redirect, url_for
import re
from .models import Agency  
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

auth = Blueprint('auth', __name__)

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        agency = Agency.query.filter_by(email=email).first()  
        if agency:
            if check_password_hash(agency.password_hash, password):  
               
                agency.last_login_date = datetime.datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')
                db.session.commit()
                flash('Logged in Successfully!', category='success')
                login_user(agency, remember=True)  
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect Password. Try Again', category='error')
        else:
            flash('Email Does Not Exist.', category='error')
            
    return render_template("login.html", user=current_user)


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        agency_name = request.form.get('agency_name')
        password = request.form.get('password')
        password_repeat = request.form.get('password-repeat')
        
        agency = Agency.query.filter_by(email=email).first() 
        
        if agency: 
            flash('Email Already Exists.', category='error')
        elif not is_valid_email(email):
            flash('Invalid email address', category='error')

        elif len(password) < 7:
            flash('Password must be at least 7 characters long', category='error')
        elif password_repeat != password:
            flash('Passwords didn\'t match', category='error')
        else:
            new_agency = Agency(email=email, 
                           agency_name=agency_name, 
                           password_hash=generate_password_hash(password, method='sha256'),
                           registration_date=datetime.datetime.utcnow().strftime('%B %d %Y - %H:%M:%S'), 
                           last_login_date=None,  
                           currency='BDT'
            )
            
            db.session.add(new_agency)
            db.session.commit()
            
            login_user(new_agency, remember=True)  
            flash('Account created', category='success')
            return redirect(url_for('views.home'))
    
    return render_template("signup.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout Successfull', category='success')
    return redirect(url_for('auth.login'))
