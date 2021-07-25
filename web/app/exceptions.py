from web.app.constants import HttpStatus
from typing import Optional

class BookStoreException(Exception):
    def __init__(
            self,
            code: Optional[int] = None,
            error_text: Optional[str] = None,
    ):
        self.code = code or HttpStatus.HTTP_200_OK
        self.error_text = error_text or ''

