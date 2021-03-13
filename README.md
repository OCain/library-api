# Agriness Developer Backend Challenge
## Desafio
Criação de uma API REST em Python, utilizando o Django Rest Framework para controle de empréstimos de uma Livraria Online, de acordo com regras de negócio definidas pela Agriness.

## Endpoints:
### Listagem de livros emprestados:
- GET: /client/{id_client}/books/
    
### Reserva de livro:
- PUT/PATCH: /books/{id}/reserve/
### Listagem de livros:
- GET: /books/

## Executando o programa:

### Requisitos:
- Docker-compose instalado na máquina

### Execução:
Após clonar o projeto para a máquina, rodar o comando na pasta raíz do projeto:
```sh
$ docker-compose up --build
```
 Com o Postman ou outro cliente para realizar requisições HTTP, acessar http://localhost:8000/api/ e criar requisições com os devidos endpoints.
 
