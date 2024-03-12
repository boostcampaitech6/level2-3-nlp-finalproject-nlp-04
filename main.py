from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models import User, get_password_hash, init_db
from auth import authenticate_user, create_access_token, oauth2_scheme
from database import get_db
import shutil

app = FastAPI()

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    # Generate a token
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/signup")
async def sign_up(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = User(username=username, hashed_password=get_password_hash(password))
    db.add(user)
    db.commit()
    return {"message": "User created successfully"}

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...), db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Here you can add token verification and file saving logic
    with open(f"{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename}
