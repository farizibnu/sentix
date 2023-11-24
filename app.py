from flask import Flask, render_template, redirect, url_for, flash, session, request
# ... (other imports)

from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
import re

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
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
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
            return render_template('hashtag-search.html')

        flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/logout')
# def logout():
#     session.pop('username', None)
#     flash('You have been logged out.', 'info')
#     return redirect(url_for('index'))

def logout():
    # Check if the user is logged in before logging out
    if 'username' in session:
        session.pop('username', None)
        flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        hashtag = request.form.get("hashtag")

        # Find posts that contain the specified hashtag in the 'hashtags' array
        search_results = mongo.db.posts.find({"hashtags": hashtag})

        print("success")

        flash('Search successful.', 'success')
        return render_template("hashtag-search.html", search_results=search_results)

    print("failed")

    return render_template("hashtag-search.html", search_results=[])


@app.route('/result', methods=['GET', 'POST'])
def result():
    # Hardcoded postId for demonstration purposes
    postId_to_display = '7293132261325540614'

    # Fetch comments for the specified postId
    result = mongo.db.comments.find_one({'postId': postId_to_display})

    if result:
        comments = result.get('comments', [])

        # Calculate the counts of positive and negative sentiments
        positive_count = sum(1 for comment in comments if comment.get('sentiment') == 'positive')
        negative_count = sum(1 for comment in comments if comment.get('sentiment') == 'negative')

        return render_template('result.html', comments=comments, positive_count=positive_count, negative_count=negative_count)

    flash(f'No comments found for postId {postId_to_display}', 'info')
    return render_template('result.html', comments=[], positive_count=0, negative_count=0)


if __name__ == "__main__":
    app.run(debug=True)