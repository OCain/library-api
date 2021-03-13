from datetime import date, timedelta

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .fee_rules import *
from .models import Book, Client
from .services import BookService
from .exceptions import BorrowedBookException


class BookTest(TestCase):
    def setUp(self):
        client = Client.objects.create(id=1)
        Book.objects.create(id=5, client=client)

    def test_borrowing_book(self):
        book = Book.objects.get(id=5)
        client = Client.objects.get(id=1)
        book.borrow(client)
        self.assertTrue(book.is_borrowed())
        self.assertEqual(book.status, Book.BORROWED)
        self.assertEqual(book.borrowed_date, date.today())
        self.assertEqual(book.client, client)

    def test_available_book_should_not_have_borrowed_status(self):
        book = Book.objects.get(id=5)
        self.assertFalse(book.is_borrowed())


class BookServiceTest(TestCase):
    def setUp(self):
        client = Client.objects.create(id=1)
        Book.objects.create(id=5, client=client)

    def test_1_day_after_reservation_deadline_should_be_1_day_late(self):
        days = BookService.RESERVATION_DAYS + 1
        service = self.__create_service_with_borrowed_book_setting_borrowed_date(days_borrowed=days)
        self.assertEqual(service.get_days_late(), 1)

    def test_day_within_reservation_deadline_should_not_have_late_days(self):
        service = self.__create_service_with_borrowed_book_setting_borrowed_date(
            days_borrowed=BookService.RESERVATION_DAYS)
        self.assertEqual(service.get_days_late(), 0)

    def test_late_return_should_have_fee_percentage_greater_than_zero_applied(self):
        days = BookService.RESERVATION_DAYS + 1
        service = self.__create_service_with_borrowed_book_setting_borrowed_date(days_borrowed=days)
        self.assertTrue(service.get_late_return_fee_percentage() > 0)

    def test_return_within_reservation_deadline_should_not_have_fee_percentage_greater_than_zero_applied(self):
        days = BookService.RESERVATION_DAYS
        service = self.__create_service_with_borrowed_book_setting_borrowed_date(days_borrowed=days)
        self.assertTrue(service.get_late_return_fee_percentage() == 0)

    def test_reserve_borrowed_book_should_raise_exception(self):
        service = self.__create_service_with_borrowed_book_setting_borrowed_date(
            days_borrowed=BookService.RESERVATION_DAYS)
        client = Client.objects.get(id=1)
        with self.assertRaises(BorrowedBookException):
            service.reserve_book(client)

    def test_reserve_available_book_should_change_book_to_borrowed(self):
        book = Book.objects.get(id=5)
        service = BookService(book)
        client = Client.objects.get(id=1)
        service.reserve_book(client)
        self.assertTrue(book.is_borrowed())
        self.assertEquals(book.client, client)

    def __create_service_with_borrowed_book_setting_borrowed_date(self, days_borrowed: int) -> BookService:
        book = Book.objects.get(id=5)
        service = BookService(book)
        client = Client.objects.get(id=1)
        book.borrow(client)
        book.borrowed_date = (date.today() - timedelta(days=days_borrowed))
        return service


class BookAPITest(APITestCase):

    def setUp(self):
        self.book = Book.objects.create(id=5)

    def test_book_creation(self):
        data = {"author": "John Doe", "title": "Test Case"}
        response = self.client.post("/api/books/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_books(self):
        response = self.client.get("/api/books/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reserve_available_book(self):
        Client.objects.create(id=1)
        data = {"client_id": 1}
        response = self.client.put("/api/books/5/reserve/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reserve_borrowed_book(self):
        book_client = Client.objects.create(id=1)
        self.book.borrow(book_client)
        self.book.save()
        data = {"client_id": book_client.id}
        response = self.client.patch("/api/books/5/reserve/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reserve_book_with_nonexistent_book_id(self):
        book_client = Client.objects.create(id=1)
        data = {"client_id": book_client.id}
        response = self.client.patch("/api/books/55/reserve/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reserve_book_with_nonexistent_client_id(self):
        data = {"client_id": 20}
        response = self.client.patch("/api/books/5/reserve/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_borrowed_books(self):
        Client.objects.create(id=1)
        response = self.client.get("/api/client/1/books/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_list_borrowed_books_with_nonexistent_client_id(self):
        Client.objects.create(id=1)
        response = self.client.get("/api/client/2/books/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class FeeRulesTest(TestCase):

    def test_fee_rule_having_3_days_late_should_return_fee(self):
        self.assertEquals(InitialFeeRule().get_fee(days_late=3), 0.036)

    def test_fee_rule_having_4_days_late_should_return_fee(self):
        self.assertEquals(InitialFeeRule().get_fee(days_late=4), 0.066)

    def test_last_fee_rule_having_10_days_late_should_return_fee(self):
        self.assertEquals(InitialFeeRule().get_fee(days_late=10), 0.13)

    def test_last_fee_rule_having_0_days_late_should_return_zero_fee(self):
        self.assertEquals(InitialFeeRule().get_fee(days_late=0), 0)