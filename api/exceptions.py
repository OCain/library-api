from .models import Book


class BorrowedBookException(Exception):
    def __init__(self, book: Book) -> None:
        self.book = book
        self.message = "Book (id: {}) is already borrowed.".format(self.book.id)
        super().__init__(self.message)
