from typing import Any
from .services import BookService
from .models import Client, Book
from rest_framework import serializers


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
    def __init__(self, instance):
        self.instance = instance
        self.service = BookService(instance)

    days_late = serializers.SerializerMethodField('get_days_late')
    late_return_fee_percentage = serializers.SerializerMethodField('get_late_return_fee_percentage')

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'borrowed_date', 'days_late', 'late_return_fee_percentage']

    def get_days_late(self, instance) -> int:
        return self.service.get_days_late()

    def get_late_return_fee_percentage(self, instance) -> float:
        return self.service.get_late_return_fee_percentage()
