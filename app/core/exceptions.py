from fastapi import HTTPException

class CustomException(HTTPException):
    def __init__(self, name: str, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)
        self.name = name