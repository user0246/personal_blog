from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from schema import Article, UserLogin
from base import get_db, engine, Base
from models import Post, Users

app = FastAPI()

templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)

@app.get("/")
async def main(request: Request, db: Session = Depends(get_db)):
    posts = db.query(Post).all()

    return JSONResponse(content=jsonable_encoder(posts))
    #return templates.TemplateResponse(name="index.html", request=request, context={
    #    "posts": posts
    #}) 

@app.get("/article/{id}")
async def article(request: Request, id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == id).first()

    return JSONResponse(content=jsonable_encoder(post))
    #return templates.TemplateResponse(request=request, name="post.html", context={
    #    "post": post
    #}) 

@app.post("/create")
async def create(request: Request, article: Article, db: Session = Depends(get_db)):
    post = Post(
        title = article.title,
        content = article.content,
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post