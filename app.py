from datetime import datetime
from flask import Flask, redirect, render_template, request, url_for
from flask import session

app = Flask(__name__)
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


class TodoItem(object):

    def __init__(self, item: str, plan_time: str) -> None:
        self.item: str = item
        self.created_at: datetime = datetime.now()
        self.plan_time: str = plan_time

    def __str__(self) -> str:
        return f'{self.item}, {self.created_at}, {self.plan_time}'

    def __repr__(self) -> str:
        return self.__str__()


items: list[TodoItem] = []


@app.route("/hello/<username>")
def hello(username: str):
    return render_template('hello.html', username=username)


@app.route('/')
def index():
    if 'username' in session:
        return f'Logged in as {session["username"]}'
    return 'You are not logged in'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return '''
        <form method="post">
            <p><input type=text name=username /></p>
            <p><input type=submit value=Login /></p>
        </form>
    '''


@app.route('/add-todo', methods=['GET', 'POST'])
def add_todo():
    if request.method == 'POST':
        todo_item = TodoItem(request.form['item'], request.form['date'])
        items.append(todo_item)
        return redirect(url_for('todo_items'))
    return '''
        <form method="post">
            <p><input type=text name=item /></p>
            <p><input type=date name=date /></p>
            <p><input type=submit value=createDate /></p>
        </form>
        '''


@app.route('/delete-todo', methods=['GET', 'POST'])  # type: ignore
def delete_todo():
    if request.method == 'POST':
        for item in items:
            if item.item == request.form['item']:
                items.remove(item)  # type: ignore
                return redirect(url_for('todo_items'))
    return """
        <form method="post">
        <p><input type=text name=item /></p>
        <p><input type=submit value=delete /></p>
        <form>
"""


@app.route('/update-todo', methods=['GET', 'POST'])  # type: ignore
def update_todo():
    if request.method == 'POST':
        for item in items:
            if item.item == request.form['item']:
                items.remove(item)  # type: ignore
                return redirect(url_for('todo_items'))
    return """
        <form method="post">
        <p><input type=text name=item /></p>
        <p><input type=submit value=delete /></p>
        <form>
"""


@app.route('/todo-items')
def todo_items():
    return render_template('todo-items.html', items=items)


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)  # type: ignore
    return redirect(url_for('index'))
