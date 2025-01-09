from flask import Flask, render_template

app = Flask(__name__)

# Route for homepage
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    # Runs the app in debug mode
    app.run(debug=True)