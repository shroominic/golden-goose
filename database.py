from datetime import datetime
from sqlmodel import Field, SQLModel, create_engine, Session, select

class Task(SQLModel, table=True):
    note_id: str = Field(primary_key=True)
    npub: str = Field(index=True)
    task: str
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="queued")
    result: str = Field(default="")

class UserBalance(SQLModel, table=True):
    npub: str = Field(primary_key=True)
    balance: int = Field(default=0)
    model: str = Field(default="claude-sonnet-4.5")
    custom_instructions: str = Field(default="")

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

def get_or_create_user(npub: str) -> UserBalance:
    with Session(engine) as session:
        user = session.get(UserBalance, npub)
        if not user:
            user = UserBalance(npub=npub)
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

def create_task(note_id: str, npub: str, task: str) -> Task | None:
    with Session(engine) as session:
        if session.get(Task, note_id):
            return None
        task_obj = Task(note_id=note_id, npub=npub, task=task)
        session.add(task_obj)
        session.commit()
        session.refresh(task_obj)
        return task_obj

def update_task_result(note_id: str, result: str, status: str = "completed") -> None:
    with Session(engine) as session:
        task = session.get(Task, note_id)
        if task:
            task.result = result
            task.status = status
            session.add(task)
            session.commit()
