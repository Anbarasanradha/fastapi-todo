from fastapi import FastAPI, Depends, HTTPException
from schemas import Todo as TodoSchema,TodoCreate
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from models import Todo

Base.metadata.create_all(bind=engine)
app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# POST - Create TODO Task
@app.post("/todos", response_model=TodoSchema)
def create(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = Todo(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo 

# GET - Read TODO Task
@app.get("/todos", response_model=list[TodoSchema])
def read(db: Session = Depends(get_db)):
    todos = db.query(Todo).all()
    return todos

# GET - Read TODO Task by ID
@app.get("/todos/{todo_id}", response_model=TodoSchema)
def read_by_id(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

# PUT - Update TODO Task
@app.put("/todos/{todo_id}", response_model=TodoSchema)
def update(todo_id: int, todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    for key, value in todo.dict().items():
        setattr(db_todo, key, value)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# DELETE - Delete TODO Task
@app.delete("/todos/{todo_id}")
def delete(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(db_todo)
    db.commit()
    return {"message": "Todo deleted successfully"}