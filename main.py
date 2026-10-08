from fastapi import FastAPI, Depends, HTTPException, status, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Annotated
import secrets
from base import get_db, engine, Base
from schema import Article, ArticleUpdate, NewUser, UserLogin
from models import Post, User 

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

security = HTTPBasic()

Base.metadata.create_all(bind=engine)

def get_current_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    print("HELLO")
    print("USERNAME:", credentials.username)
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = b"admin"
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = b"admin"
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/")
async def main(request: Request, db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    return templates.TemplateResponse(request=request, name="index.html", context={"posts": posts})
    #return JSONResponse(content=jsonable_encoder(posts)) 

@app.get("/post/{id}")
async def post_by_id(id: int, request: Request, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == id).first() 
    return templates.TemplateResponse(request=request, name="post.html", context={"post": post})
    #return JSONResponse(content=jsonable_encoder(post)) 

@app.post("/create", response_model=Article)
async def create_post(username: Annotated[str, Depends(get_current_username)], db: Session = Depends(get_db), title: str = Form(), content: str = Form()):
    user = db.query(User).filter(User.login == username).first()
    post = Post(
        title = title,
        content = content,
        user_id = user.id 
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/create")
async def create_get(request: Request, username: Annotated[str, Depends(get_current_username)]):
    return templates.TemplateResponse(request=request, name="create.html")

@app.post("/edit/{id}", response_model=ArticleUpdate)
async def edit(id: int, username: Annotated[str, Depends(get_current_username)], db: Session = Depends(get_db), title: str = Form(), content: str = Form()):
    post = db.query(Post).filter(Post.id == id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.user.login != username:
        raise HTTPException(status_code=403, detail="cannot edit")

    if title is not None:
        post.title = title

    if content is not None:
        post.content = content

    db.commit()
    db.refresh(post)

    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/edit/{id}")
async def edit_get(id: int, request: Request, username: Annotated[str, Depends(get_current_username)], db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.user.login != username:
        raise HTTPException(status_code=403, detail="cannot edit")

    return templates.TemplateResponse(request=request, name="edit.html", context={"post": post})

 

@app.post("/delete/{id}")
async def delete(id: int, username: Annotated[str, Depends(get_current_username)], db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.user.login != username:
        raise HTTPException(status_code=403, detail="cannot delete")

    db.delete(post)
    db.commit()

    return RedirectResponse(url="/dashboard", status_code=303)

@app.post("/user", response_model=NewUser)
async def create_user(user: NewUser, db: Session = Depends(get_db)):
    new_user = User(
        login = user.login,
        password = user.password
    ) 

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    incoming_user = db.query(User).filter(User.login == user.login).first()

    if not incoming_user:
        raise HTTPException(status_code=401, detail="user does not exists")

    if incoming_user.password != user.password:
        raise HTTPException(status_code=401, detail="wrong password") 

    return {"message": "alright alright alright"}

@app.get("/dashboard")
async def dashboard(request: Request, username: Annotated[str, Depends(get_current_username)], db: Session = Depends(get_db)):
    posts = db.query(Post).all()

    return templates.TemplateResponse(request=request, name="dashboard.html", context={"posts": posts})


@app.get("/me")
async def read_current_user(username: Annotated[str, Depends(get_current_username)]):
    return {"username": username}