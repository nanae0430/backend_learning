from pydantic import BaseModel, ConfigDict, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=10)
    rerank: bool = False
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class AskResponse(BaseModel):
    answer: str
    top_k: int
    rerank: bool


class PostRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=50)


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    title: str = Field(min_length=1, max_length=200)


class DocumentCreate(BaseModel):
    user_id: int
    title: str = Field(min_length=1, max_length=200)


class DocumentUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
