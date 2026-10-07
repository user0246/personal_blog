from pydantic import BaseModel

class Article(BaseModel):
    title: str
    content: str

class ArticleUpdate(BaseModel): 
    title: str | None = None
    content: str | None = None

class NewUser(BaseModel):
    login: str
    password: str

class UserLogin(BaseModel):
    login: str
    password: str