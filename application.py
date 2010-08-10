from flask import Flask
app = Flask(__name__)

from flask import render_template

@app.route('/')
def home():
    return render_template('home.html', );

app.secret_key = '7%@0g6y!hu^flbmkcfb$@zxs9ftmh=t0blgnog-ibh52za$6nu'

if __name__ == '__main__':
    app.run()
