from flask import Flask, render_template, request

app = Flask(__name__)

# @app.route("/")
# def home():
#     return "Welcome to your Flask application!"

@app.route("/", methods=["GET", "POST"])
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

@app.route("/search", methods=["GET", "POST"])
def search():
    # Process the search form data here
    # You can access form data like this: request.form['your_input_field_name']
    # Implement your search logic here

    # For demonstration purposes, let's pass a sample result to the template
    search_results = [{"username": "Sample User"}]

    return render_template("hashtag-search.html", search_results=search_results)

if __name__ == "__main__":
    app.run(debug=True)
