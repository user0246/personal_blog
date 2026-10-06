from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from base import get_db, engine, Base
from schema import Article, ArticleUpdate
from models import Post 

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
async def main(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    return JSONResponse(content=jsonable_encoder(posts)) 

@app.get("/post/{id}")
async def post_by_id(id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == id).first() 
    return JSONResponse(content=jsonable_encoder(post)) 

@app.post("/create", response_model=Article)
async def create_post(article: Article, db: Session = Depends(get_db)):
    post = Post(
        title = article.title,
        content = article.content
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post

@app.patch("/edit/{id}", response_model=ArticleUpdate)
async def edit(id: int, article: ArticleUpdate, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == id).first()

    if not post:
        return HTTPException(status_code=404, detail="Post not found")

    if article.title is not None:
        post.title = article.title

    if article.content is not None:
        post.content = article.content

    db.commit()
    db.refresh(post)

    return post

@app.delete("/delete/{id}")
async def delete(id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == id).first()

    if not post:
        return HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()

    return {"message": "post deleted"}