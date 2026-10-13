from fastapi import Response, status, HTTPException, Depends, APIRouter
from httpx import post
from .. import models, schemas, Oauth2
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List, Optional
from sqlalchemy import func


router = APIRouter(
    prefix="/posts",
    tags=['posts']
)


@router.get("/", response_model=List[schemas.postout])
def get_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(Oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str    ] = ""
):
    print(search)
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    results = (
    db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
    .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
    .group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip)
    .all()
)
    return posts


@router.get("/{id}", response_model=schemas.postres)
def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(Oauth2.get_current_user),
):
    # Find the post by its ID regardless of owner first
    f_post = db.query(models.Post).filter(models.Post.id == id).first()
    post_with_votes = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    # If the post doesn't exist at all, return 404
    if not f_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )

    # If the post exists but belongs to a different user, return 403
    if f_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    return f_post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.postres)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(Oauth2.get_current_user)):
    # cursor.execute(""" INSERT INTO posts (title,content,published) VALUES (%s, %s, %s) RETURNING * """,
    #               (post.title,post.content,post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    print(current_user.id)
    print(current_user.email)
    # Unpacks all fields from the schema, then manually adds the owner
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(Oauth2.get_current_user)
):

    # cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING * """, str((id)))
    # gEpostt = cursor.fetchone()
    # conn.commit()

    post = db.query(models.Post).filter(models.Post.id == id)

    post_data = post.first()

    if post_data == None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found"
        )

    if post_data.owner_id != current_user.id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action"
        )

    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.postres)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(Oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    if post.owner_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action")

    post_query.update(updated_post.model_dump(), synchronize_session=False)

    db.commit()
    return post_query.first()
