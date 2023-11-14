from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to your Flask application!"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Process the login form data here
        # You can access form data like this: request.form['userid'] and request.form['passw']
        # Implement your login logic here

        return "Login successful!"  # You can redirect or display a success message as needed

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Process the login form data here
        # You can access form data like this: request.form['userid'] and request.form['passw']
        # Implement your login logic here

        return "Register successful!"  # You can redirect or display a success message as needed

    return render_template("register.html")

@app.route("/search")
def about():
    return render_template('hashtag-search.html')

if __name__ == "__main__":
    app.run(debug=True)
