from flask import Flask, render_template, redirect, url_for, flash, session, request
# ... (other imports)

from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
import re
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/Tubes'
app.secret_key = 'bond123'
mongo = PyMongo(app)

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Register')

regular_user_search_limit = 3
user_search_counts = {}

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
                'email': form.email.data,
                'membership': 'regular'
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
            session['membership'] = existing_user['membership']
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
        session.pop('membership', None)
        flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/search', methods=["GET", "POST"])
def search():
    if request.method == "POST":
        hashtag = request.form.get("hashtag")

        # Check if the user is a regular user and has reached the search limit
        if session['membership'] == 'regular':
            if 'username' in session:
                username = session['username']
                if username in user_search_counts:
                    # Check if the user has reached the search limit
                    if user_search_counts[username] >= regular_user_search_limit:
                        flash(f'Regular users are limited to {regular_user_search_limit} searches per day.', 'warning')
                        return render_template("hashtag-search.html", search_results=[])

                # Update the user's search count
                user_search_counts[username] = user_search_counts.get(username, 0) + 1

        # Continue with the search logic
        search_results = mongo.db.posts.find({"hashtags": hashtag})
        flash('Search successful.', 'success')
        return render_template("hashtag-search.html", search_results=search_results)

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

# New route for sentiment analysis
@app.route('/sentiment-analysis')
def sentiment_analysis():
    # Connect to MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["db_tiktok"]
    collection = db["comments"]

    # Load sentiment analysis model and tokenizer
    pretrained = "mdhugol/indonesia-bert-sentiment-classification"
    model = AutoModelForSequenceClassification.from_pretrained(pretrained)
    tokenizer = AutoTokenizer.from_pretrained(pretrained)
    sentiment_analysis = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

    # Loop through documents in the collection
    for doc in collection.find():
        # Loop through comments in the document
        for comment_key, comment_value in enumerate(doc.get('comments', [])):
            if 'text' in comment_value:
                # Get the text from the 'text' field of each comment
                text = comment_value['text']

                # Perform sentiment analysis
                label_index = {'LABEL_0': 'positive', 'LABEL_1': 'neutral', 'LABEL_2': 'negative'}
                result = sentiment_analysis(text)
                label = result[0]['label']
                score = result[0]['score']

                # Update the comment in MongoDB with the sentiment
                collection.update_one(
                    {'_id': doc['_id'], f'comments.{comment_key}.text': text},
                    {'$set': {f'comments.{comment_key}.sentiment': label_index[label]}}
                )

    flash("Sentiment analysis and update completed.", "info")
    return redirect(url_for('index'))

@app.route('/change_membership', methods=['POST'])
def change_membership():
    new_membership = request.form.get('membership')

    # Get the 'users' collection from MongoDB
    users_collection = mongo.db.users

    # Update the 'membership' field in the user's document
    # Assuming you have a unique identifier for the user, e.g., 'username'
    username = session['username']

    # Update the 'membership' field in the user's document
    users_collection.update_one({'username': username}, {'$set': {'membership': new_membership}})

    # Update the session with the new membership
    session['membership'] = new_membership

    flash(f'Membership changed to {new_membership.capitalize()}', 'success')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)