from flask import Flask, render_template, redirect, url_for, flash, session, request
# ... (other imports)
from pymongo import MongoClient
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
import re

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/Tubes'
app.secret_key = 'bond123'
mongo = PyMongo(app)

client = MongoClient('mongodb://localhost:27017/')
db = client['Tubes']  # Ganti 'Tubes' dengan nama database Anda
collection1 = db['posts']  # Ganti 'nama_koleksi1' dengan nama koleksi pertama Anda
collection2 = db['comments']  # Ganti 'nama_koleksi2' dengan nama koleksi kedua Anda

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Register')

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/test')
def test():
    return render_template('test-search.html')

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

# @app.route("/search", methods=["GET", "POST"])
# def search():
#     if request.method == "POST":
#         hashtag = request.form.get("hashtag")

#         # Find posts that contain the specified hashtag in the 'hashtags' array
#         search_results = mongo.db.posts.find({"hashtags": hashtag})

#         print("success")

#         flash('Search successful.', 'success')
#         return render_template("hashtag-search.html", search_results=search_results)

#     print("failed")

#     return render_template("hashtag-search.html", search_results=[])
@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('hashtag')
    
    # Misalkan Anda ingin mencari data berdasarkan field 'hashtags' di dalam koleksi 'collection1'
    # results_collection1 = collection1.find({'hashtags': {'$regex': re.compile(search_query, re.IGNORECASE)}})
    results_collection1 = collection1.find({'hashtags': {'$in': [search_query]}})
    # # Ambil _id dari hasil pencarian pertama di collection1
    # ids = [result['id'] for result in results_collection1]

    # # Lakukan pencarian di collection2 berdasarkan 'postId' yang sesuai dengan ids dari collection1
    # results_collection2 = collection2.find({'postId': {'$in': ids}}, {'comments': 1})
    
    return render_template('hashtag-result.html', results1=results_collection1)

@app.route('/result', methods=['GET', 'POST'])
def result():
    # Hardcoded postId for demonstration purposes
    postId_to_display = request.form.get('postId')

    # Fetch comments for the specified postId
    result = mongo.db.comments.find_one({'postId': postId_to_display})

    if result:
        comments = result.get('comments', [])

        # Calculate the counts of positive and negative sentiments
        positive_count = sum(1 for comment in comments if comment.get('sentiment') == 'positive')
        negative_count = sum(1 for comment in comments if comment.get('sentiment') == 'negative')
        neutral_count = sum(1 for comment in comments if comment.get('sentiment') == 'neutral')

        return render_template('result.html', comments=comments, positive_count=positive_count, negative_count=negative_count, neutral_count=neutral_count)

    flash(f'No comments found for postId {postId_to_display}', 'info')
    return render_template('result.html', comments=[], positive_count=0, negative_count=0, neutral_count=0)

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


if __name__ == "__main__":
    app.run(debug=True)