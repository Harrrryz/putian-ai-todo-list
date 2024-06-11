from datetime import datetime
import time
from flask import Flask, redirect, render_template, request, url_for
from flask import session, jsonify
from flask_cors import CORS
import sqlite3

from flask import g

DATABASE = 'todo.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


app = Flask(__name__)
CORS(app)
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class TodoItem(object):

    def __init__(self, item: str, plan_time: str) -> None:
        self.item: str = item
        self.created_at: datetime = datetime.now()
        self.plan_time: str = plan_time

    def __str__(self) -> str:
        return f'{self.item}, {self.created_at}, {self.plan_time}'

    def __repr__(self) -> str:
        return self.__str__()

    def __settime__(self, plan_time: str) -> None:
        self.plan_time = plan_time

    def __setcreatetime__(self, create_time_str: str) -> None:
        self.created_at = datetime.strptime(
            create_time_str, TIME_FORMAT)

    def to_dict(self):
        return {
            'item': self.item,
            'created_at': self.created_at.strftime(TIME_FORMAT),
            'plan_time': self.plan_time
        }


file = open('C:/Users/harry/code/putian-ai-todo-list/todoData.txt', 'r')
items_string_list: list[str] = file.readlines()
items: list[TodoItem] = []

for item_string in items_string_list:
    item_name, create_time_str, plan_time = (
        stuff.strip() for stuff in item_string.split("\t", 3))
    todo_item: TodoItem = TodoItem(item_name, plan_time)
    todo_item.__setcreatetime__(create_time_str)
    items.append(todo_item)

file.close()


def add_item_totxt(items: list[TodoItem]):
    with open('C:/Users/harry/code/putian-ai-todo-list/todoData.txt', 'w') as file:

        for item in items:
            item_name: str = item.item
            item_create_time_str: str = item.created_at.strftime(TIME_FORMAT)
            item_plan_time_str: str = item.plan_time
            item_str: str = item_name+"\t"+item_create_time_str+"\t"+item_plan_time_str+"\n"
            file.write(item_str)


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
        add_item_totxt(items)
        return redirect(url_for('todo_items'))
    return '''
        <form method="post">
            <p><input type=text name=item /></p>
            <p><input type=date name=date /></p>
            <p><input type=submit value=createDate /></p>
        </form>
        '''


@app.route('/add-todo-json', methods=['POST'])
def add_todo_json():
    todo_item = TodoItem(request.json['item'],  # type: ignore
                         request.json['date'])  # type: ignore
    items.append(todo_item)
    add_item_totxt(items)

    with app.app_context():
        db = get_db()
        script = f"INSERT INTO todo (item) VALUES ({todo_item.item})"
        print(script)
        db.cursor().execute(script)
        db.commit()
    return jsonify({'isOk': True})


@app.route('/delete-todo', methods=['GET', 'POST'])  # type: ignore
def delete_todo():
    if request.method == 'POST':
        for item in items:
            if item.item == request.form['item']:  # type: ignore
                items.remove(item)
                add_item_totxt(items)
                return redirect(url_for('todo_items'))

    return """
        <form method="post">
        <p><input type=text name=item /></p>
        <p><input type=submit value=delete /></p>
        <form>
    """


@app.route('/delete-todo-json', methods=['POST'])  # type: ignore
def delete_todo_json():
    index: int = int(request.json['index'])  # type: ignore
    items.remove(items[index-1])  # type: ignore
    add_item_totxt(items)
    return jsonify({'isOk': True})


@app.route('/update-todo', methods=['GET', 'POST'])  # type: ignore
def update_todo():
    if request.method == 'POST':
        for item in items:
            if item.item == request.form['item']:
                item.__settime__(
                    request.form['date'])
                return redirect(url_for('todo_items'))
    return """
        <form method="post">
        <p> Item to update </p>
        <p><input type=text name=item /></p>

        <p> New item plan time: </p>
        <p><input type=date name=date /></p>
        <p><input type=submit value=updateDate /></p>
        <form>
    """


@app.route('/update-todo-json', methods=['GET', 'POST'])  # type: ignore
def update_todo_json():
    index: int = int(request.json['index'])  # type: ignore
    # type: ignore

    # type: ignore
    items[index-1].__settime__(request.json['plan_date'])  # type: ignore
    items[index-1].item = request.json['item']  # type: ignore
    add_item_totxt(items)
    return jsonify({'isOk': True})


@app.route('/todo-items')
def todo_items():
    return render_template('todo-items.html', items=items)


@app.route('/todo-items-json')
def todo_items_json():
    # time.sleep(3)
    return jsonify([item.to_dict() for item in items])


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)  # type: ignore
    return redirect(url_for('index'))
