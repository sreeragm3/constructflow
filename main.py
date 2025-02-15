from flask import Flask, render_template # type: ignore

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def showcase():
    return render_template('admin.html')
