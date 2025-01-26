from pydantic import BaseModel, PositiveFloat


class Task(BaseModel):
    weight: PositiveFloat
    min_interval: PositiveFloat
    max_interval: PositiveFloat


class Tasks(BaseModel):
    post_tweet: Task
    reply_to_tweet: Task
    like_tweet: Task
