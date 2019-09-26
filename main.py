from flask import Flask
from flask import render_template, request
import eth


app = Flask(__name__)

@app.route('/')
def hello_world(name=None):
    return render_template('main.html', name=name)

@app.route('/adding')
def login(): 
    users = watcher.watch_list
    return render_template('adding.html', users = users)

@app.route('/watch')
def profile(): 
    logs = watcher.logs.logs
    return render_template('watch.html', logs = logs["transactions"])

@app.route('/adding', methods=['GET','POST'])
def my_form_post():
    if request.method == 'POST':
        text = request.form['text']
        print(text)
        watcher.account.add(text)
        watcher.update_watchList()
    return render_template('adding.html', users = watcher.watch_list)

if __name__ == '__main__':
    watcher = eth.Watcher()
    watcher.start()
    app.run()