from flask import render_template, flash, redirect, url_for, request, make_response, Response
from werkzeug.urls import url_parse
from app import app, db
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Table
import pandas as pd
import numpy as np
import time
import json

###############
# BASE ROUTES #
###############

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')

#######################
# USER SIGN-IN ROUTES #
#######################

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            message = 'Invalid username or password!'
            return render_template('login.html', title='Register', message=message)
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', message=message)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.form:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        repeat_password = request.form.get('repeat_password')

        if len(username) < 3:
            message = 'You must enter a username!'
            return render_template('register.html', title='Register', message=message)
        if len(email) < 3:
            message = 'You must enter a email!'
            return render_template('register.html', title='Register', message=message)
        if len(password) < 3:
            message = 'You must enter a password!'
            return render_template('register.html', title='Register', message=message)
        if not password == repeat_password:
            message = "You're passwords must match!"
            return render_template('register.html', title='Register', message=message)
        user = User.query.filter_by(username=username).first()
        if user is None:
            print("success")
        else:
            print("exists")
            message = "This username already exists!"
            return render_template('register.html', title='Register', message=message)
            return redirect(url_for('register'))
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', message=message)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    return render_template('user.html', user=user)