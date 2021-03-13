from datetime import date
from .models import Book, Client
from .exceptions import BorrowedBookException
from .fee_rules import *


class BookService:
    RESERVATION_DAYS = 3

    def __init__(self, book: Book):
        self.book = book

    def reserve_book(self, client: Client):
        if self.book.is_borrowed():
            raise BorrowedBookException(self.book)
        self.book.borrow(client)
        self.book.save()

    def get_days_late(self) -> int:
        days_borrowed = (date.today() - self.book.borrowed_date).days
        if days_borrowed <= self.RESERVATION_DAYS:
            return 0
        return days_borrowed - self.RESERVATION_DAYS

    def get_late_return_fee_percentage(self) -> float:
        late_fee = 0
        if self.__is_late():
            late_fee = self.__calculate_late_return_fee_rate()
        return round(late_fee * 100, 2)

    def __is_late(self) -> bool:
        return self.get_days_late() > 0

    def __calculate_late_return_fee_rate(self) -> float:
        days_late = self.get_days_late()
        rule = InitialFeeRule()
        return rule.get_fee(days_late=days_late)
