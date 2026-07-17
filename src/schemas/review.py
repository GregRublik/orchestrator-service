from pydantic import BaseModel

class ResponseReview(BaseModel):
    res: str

class CreateReview(BaseModel):
    review_id: int
    product: str
    review: str
