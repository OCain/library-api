from django.http import HttpResponse
from django.http.response import HttpResponseBadRequest

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .exceptions import BorrowedBookException
from .models import Client, Book
from .serializers import BorrowedBookSerializer, ClientSerializer, BookSerializer
from .services import BookService


class ClientViewSet(viewsets.ModelViewSet):
    """
    Returns clients registered.
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def get_queryset(self):
        return self.queryset.order_by("name")
    
    @action(methods=['get'], detail=True)
    def books(self, request, pk=None):
        """
        Returns a list of all books borrowed by customer.
        """
        try:
            client = Client.objects.get(pk=pk)
            books = client.book_set.all()
            return Response(BorrowedBookSerializer(books, many=True).data)
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
