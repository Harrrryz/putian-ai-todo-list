from datetime import datetime
from fastapi import FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship  # type: ignore
from pydantic import BaseModel, field_validator
from contextlib import asynccontextmanager
from sqlalchemy import func
from typing import Generic, TypeVar, Sequence

T = TypeVar('T')


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_name: str = Field(index=True)
    pwd: str = Field(index=True)
    todo_list: list['Todo'] = Relationship(back_populates='user')


class Todo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    item: str = Field(index=True)
    create_time: datetime = Field(default_factory=datetime.now)
    plan_time: datetime | None = Field(default=None)
    user_id: int = Field(default=None, foreign_key="user.id")
    user: User = Relationship(back_populates='todo_list')


class PaginateModel(BaseModel, Generic[T]):
    page: int
    per_page: int
    total_items: int
    items: Sequence[T]


class UserDto(BaseModel):
    user_name: str
    pwd: str


class TodoDto(BaseModel):
    item: str
    plan_time: str | None
    user_id: int

    @field_validator('plan_time')
    @classmethod
    def parse_plan_time(cls, value: str | None):
        if value:
            return datetime.strptime(value, TIME_FORMAT)
        return value


class UpdateTodoDto(BaseModel):
    item: str
    plan_time: str | None

    @field_validator('plan_time')
    @classmethod
    def parse_plan_time(cls, value: str | None):
        if value:
            return datetime.strptime(value, TIME_FORMAT)
        return value


TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

sqlite_file_name = "todo.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"


connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def init_db_and_tables():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    init_users = ['Harry', 'Leo', 'Amy', 'Alvin']
    with Session(engine) as session:
        for user_name in init_users:
            user = User(user_name=user_name, pwd='123456')
            session.add(user)
        session.commit()
    init_todos = [
        "Code",
        "Groceries",
        "Clean",
        "Call",
        "Bills",
        "Walk",
        "Report",
        "Doctor",
        "Plants",
        "Read",
        "Library",
        "Trash",
        "Laundry",
        "Desk"
    ]
    init_todo_user_ids = [1, 2, 3, 4]
    with Session(engine) as session:
        for i in range(len(init_todos)):
            init_todo = init_todos[i]
            init_todo_user_id = init_todo_user_ids[i % 4]
            user = session.exec(select(User).where(User.id == init_todo_user_id)).first()
            todo = Todo(item=init_todo, plan_time=None, user_id=init_todo_user_id, user=user)  # type: ignore
            session.add(todo)
        session.commit()


app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

# TODO: add return type for each function


@app.post("/create_todos/", tags=['todo'])
def create_todo(todoDto: TodoDto) -> Todo:
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == todoDto.user_id)).first()
        if not user:
            raise HTTPException(status_code=400, detail="User does not exist!")
        todo = Todo(item=todoDto.item, plan_time=todoDto.plan_time, user=user)  # type: ignore
        session.add(todo)  # no id in todo, because it has not been saved yet
        session.commit()  # save to db (id generated!)
        session.refresh(todo)
        return todo


@app.get("/get_todos/", tags=['todo'])
# page: int, per_page: int
def read_todos(page: int, per_page: int) -> PaginateModel[Todo]:
    skip = (page - 1) * per_page
    limit = per_page
    with Session(engine) as session:
        count_statement = select(func.count(Todo.create_time))  # type: ignore
        statement = select(Todo).offset(skip).limit(limit)
        result = session.exec(statement)
        total_items = session.exec(count_statement).one()
        items = result.all()
        return PaginateModel[Todo](page=page, items=items, per_page=per_page, total_items=total_items)


@app.delete("/delete_todos/{todo_id}", tags=['todo'])
def delete_todos(todo_id: int):
    with Session(engine) as session:
        statement = select(Todo).where(Todo.id == todo_id)
        results = session.exec(statement)
        todo: Todo = results.one()
        print("Todo: ", todo)
        session.delete(todo)


@app.post("/update_todos/{todo_id}", tags=['todo'])
def update_todos(updateDto: UpdateTodoDto, todo_id: int) -> Todo:
    with Session(engine) as session:
        statement = select(Todo).where(Todo.id == todo_id)
        results = session.exec(statement)
        todo: Todo = results.one()
        print("Todo:", todo)

        todo.item = updateDto.item
        if (updateDto.plan_time != None):
            todo.plan_time = datetime.strptime(updateDto.plan_time, TIME_FORMAT)
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo


@app.post("/create_users/", tags=['user'])
def create_user(userDto: UserDto):
    with Session(engine) as session:
        user = User(user_name=userDto.user_name, pwd=userDto.pwd)
        session.add(user)  # no id in user, because it has not been saved yet
        session.commit()  # save to db (id generated!)
        session.refresh(user)
        return user


@app.delete("/delete_users/{user_id}", tags=['user'])
def delete_user(user_id: int):
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id)
        results = session.exec(statement)
        user: User = results.one()
        session.delete(user)

# TODO: return in paginate model


@app.get("/get_users/", tags=['user'])
# page: int, per_page: int
def read_users():
    with Session(engine) as session:
        # use offset and limit to create pagination
        statement = select(User)
        result = session.exec(statement)
        users = result.all()
        return users


@app.post("/update_users/{user_id}", tags=['user'])
def update_user(user_id: int, userDto: UserDto):
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id)
        results = session.exec(statement)
        user: User = results.one()
        user.user_name = userDto.user_name
        user.pwd = userDto.pwd
        session.add(user)
        session.commit()
        session.refresh(user)


@app.get("/get_user_by_todo/{todo_id}", tags=['apis'])
def get_user_by_todo(todo_id: int):
    with Session(engine) as session:
        statement = select(Todo).where(Todo.id == todo_id)
        results = session.exec(statement)
        return results.one().user

# TODO: use Todo to get user_id = user_id and use offset and limit to paginate
# TODO: return in paginate model


@app.get("/get_todos_by_user/{user_id}", tags=['apis'])
def read_todos_by_user(user_id: int):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise HTTPException(status_code=400, detail='User not found!')
        return user.todo_list


# TODO: return in paginate model
@app.get("/get_todos_by_item_name/{item_name}", tags=['apis'])
def get_todos_by_item_name(item_name: str):
    with Session(engine) as session:
        statement = select(Todo).where(Todo.item == item_name)
        results = session.exec(statement).all()
        return results

# TODO: return in paginate model


@app.get("/get_todos_by_plan_time/{plan_time}", tags=['apis'])
def get_todo_by_plan_time(plan_time: str):
    with Session(engine) as session:
        if (plan_time == "null"):
            statement = select(Todo).where(Todo.plan_time == None)
            results = session.exec(statement).all()
            return results
        statement = select(Todo).where(Todo.plan_time == plan_time)
        results = session.exec(statement).all()
        return results
