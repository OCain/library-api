from typing import Any

from rest_framework import serializers

from .models import Client, Book
from .services import BookService


class ClientSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name']


class BookSerializer(serializers.HyperlinkedModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'status', 'client_id', 'borrowed_date']

    def get_status(self, instance) -> Any:
        return instance.get_status_display()


class BorrowedBookSerializer(BookSerializer):

    days_late = serializers.SerializerMethodField()
    late_return_fee_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'borrowed_date', 'days_late', 'late_return_fee_percentage']

    def get_days_late(self, instance) -> int:
        service = BookService(instance)
        return service.get_days_late()

    def get_late_return_fee_percentage(self, instance) -> float:
        service = BookService(instance)
        return service.get_late_return_fee_percentage()
