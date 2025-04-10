from googleapiclient.errors import HttpError
from fastapi import HTTPException
from functools import wraps


def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HttpError as error:
            raise HTTPException(status_code=error.resp.status, detail=str(error))
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    return wrapper
