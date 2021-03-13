from django.db import models
from datetime import date


class Client(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name


class Book(models.Model):
    AVAILABLE = 1
    BORROWED = 2

    STATUS = (
        (AVAILABLE, 'Disponível'),
        (BORROWED, 'Emprestado'),
    )

    author = models.CharField(max_length=80)
    title = models.CharField(max_length=100)
    status = models.PositiveSmallIntegerField(
        choices=STATUS,
        default=AVAILABLE
    )
    client = models.ForeignKey('api.Client', null=True, default=None, on_delete=models.CASCADE)
    borrowed_date = models.DateField(null=True)

    def is_borrowed(self):
        return self.status == self.BORROWED

    def borrow(self, client):
        self.status = self.BORROWED
        self.borrowed_date = date.today()
        self.client = client

    def __str__(self):
        return '{}: {}'.format(self.author, self.title)
