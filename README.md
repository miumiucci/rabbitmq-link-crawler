# Message Queue Parser

**Message Queue Parser** — это асинхронное приложение для обработки ссылок с веб-страниц с использованием очередей сообщений RabbitMQ.

## Состав проекта

- **Producer** — извлекает ссылки с указанного URL и добавляет их в очередь `links_queue`.
- **Consumer** — обрабатывает ссылки из очереди, извлекает новые ссылки и публикует их обратно в очередь.

## Используемые технологии


- Python 3.11
- RabbitMQ
- aio-pika
- BeautifulSoup4

## Установка и настройка

1. Убедитесь, что у вас установлены:
   - Python 3.11
   - RabbitMQ
2. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/miumiucci/rabbitmq-link-crawler.git
   cd rabbitmq-link-crawler
   
## 3.Установите зависимости:
  ```bash```
   pip install -r requirements.txt
## 4.Настройте RabbitMQ:

-Убедитесь, что RabbitMQ запущен на localhost
-Настройте переменные окружения для подключения:
- RABBITMQ_HOST
- RABBITMQ_PORT
- RABBITMQ_USER
- RABBITMQ_PASSWORD

## 5.Запуск:
1. Producer: Для запуска producer.py укажите URL веб-страницы для обработки:
  ```bash```
  python producer.py ссылка

2. Consumer: Для запуска consumer.py выполните:
   ```bash```
  python python consumer.py
