from flask import Flask, render_template, redirect, url_for, flash, session, request
# ... (other imports)

from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/Tubes'
app.secret_key = 'bond123'
mongo = PyMongo(app)

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Register')

@app.route('/')
def index():
    form = RegistrationForm()
    return render_template('register.html', form=form)

@app.route('/register', methods=['POST'])
def signup():
    form = RegistrationForm()

    if form.validate_on_submit():
        users = mongo.db.users
        existing_user = users.find_one({'username': form.username.data})

        if existing_user is None:
            users.insert_one({
                'username': form.username.data,
                'password': form.password.data,
                'email': form.email.data
            })
            flash('Registration successful!', 'success')
            return redirect(url_for('index'))

        flash('Username already exists. Choose a different one.', 'danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = mongo.db.users
        existing_user = users.find_one({'username': username})

        if existing_user and existing_user['password'] == password:
            session['username'] = username
            flash(f'Hello, {username}! You are now logged in.', 'success')
            return render_template('login.html')

        flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route("/search", methods=["GET", "POST"])
def search():
    # Process the search form data here
    # You can access form data like this: request.form['your_input_field_name']
    # Implement your search logic here

    # For demonstration purposes, let's pass a sample result to the template
    search_results = [{"username": "Sample User"}]

    return render_template("hashtag-search.html", search_results=search_results)


@app.route("/result", methods=["GET", "POST"])
def result():
    # Process the search form data here
    # You can access form data like this: request.form['your_input_field_name']
    # Implement your search logic here

    # For demonstration purposes, let's pass a sample result to the template
    result = [{"username": "Sample User"}]

    return render_template("result.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
