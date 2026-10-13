from fastapi import  APIRouter,Depends,HTTPException,status,Response
from sqlalchemy.orm import Session
from .. import database,models,utils,Oauth2,schemas
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(tags=['Authentication'])

@router.post('/login',response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
  user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")
  if not utils.verify(user_credentials.password, user.password):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")
  #create a token
  # return token
  access_token = Oauth2.create_access_token(data={"user_id": user.id})

  return {"access_token": access_token, "token_type": "bearer"}