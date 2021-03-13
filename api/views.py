from django.http.response import HttpResponseBadRequest
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from .services import BookService
from .exceptions import BorrowedBookException
from .serializers import BorrowedBookSerializer, ClientSerializer, BookSerializer
from .models import Client, Book
import json


class ClientViewSet(viewsets.ModelViewSet):
    """
    Returns clients registered.
    """
    queryset = Client.objects.all().order_by('name')
    serializer_class = ClientSerializer

    @action(methods=['get'], detail=True)
    def books(self, request, pk=None):
        """
        Returns a list of all books borrowed by customer.
        """
        try:
            client = Client.objects.get(pk=pk)
            books = []
            for book in client.book_set.all():
                serialized_book = BorrowedBookSerializer(book).data
                books.append(serialized_book)
            return HttpResponse(json.dumps(books), content_type='application/json')
        except Client.DoesNotExist:
            return HttpResponseBadRequest("Client ID #{} does not exist!".format(pk))


class BookViewSet(viewsets.ModelViewSet):
    """
    Returns books registered.
    """
    queryset = Book.objects.all().order_by('title')
    serializer_class = BookSerializer

    @action(methods=['patch', 'put'], detail=True)
    def reserve(self, request, pk=None):
        """
        Book reservation for a client. Client ID must be informed in body content.
        """
        try:
            book = Book.objects.get(pk=pk)
            service = BookService(book)
            client_id = request.data['client_id']
            client = Client.objects.get(id=client_id)
            service.reserve_book(client)
        except BorrowedBookException as e:
            return HttpResponseBadRequest(e.message)
        except Book.DoesNotExist:
            return HttpResponseBadRequest("Book ID #{} does not exist!".format(pk))
        except Client.DoesNotExist:
            return HttpResponseBadRequest("Client ID #{} does not exist!".format(client_id))
        return HttpResponse(status=200)
