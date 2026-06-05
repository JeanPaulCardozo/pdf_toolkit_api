from pydantic import BaseModel, Field


class PageRange(BaseModel):
    start: int = Field(gt=0)
    end: int = Field(gt=0)
