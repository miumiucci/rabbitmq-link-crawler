import sys
import os
import requests
from bs4 import BeautifulSoup
import pika

# Подключение к RabbitMQ
def connect_to_rabbitmq():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=os.getenv('RABBITMQ_HOST', 'localhost'),
            port=int(os.getenv('RABBITMQ_PORT', 5672)),
            credentials=pika.PlainCredentials(
                username=os.getenv('RABBITMQ_USER', 'guest'),
                password=os.getenv('RABBITMQ_PASSWORD', 'guest')
            )
        )
    )
    return connection.channel()

# Извлечение ссылок
def extract_links(url, base_domain):
    try:
        response = requests.get(url, timeout=10, verify=False)  # Отключение SSL для тестирования
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Логируем название страницы
        title = soup.title.string.strip() if soup.title else "No Title"
        print(f"Обработка страницы: '{title}' ({url})")

        links = set()

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href.startswith('/'):  # Относительные ссылки
                href = base_domain + href
            elif not href.startswith('http'):  # Ссылки вида some/path
                href = base_domain + '/' + href
            if base_domain in href:
                links.add(href)
        return links

    except requests.RequestException as e:
        print(f"Ошибка при обработке {url}: {e}")
        return set()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python producer.py <URL>")
        sys.exit(1)

    start_url = sys.argv[1]
    base_domain = start_url.split('/')[0] + '//' + start_url.split('/')[2]

    print(f"Извлечение ссылок из {start_url}")
    links = extract_links(start_url, base_domain)

    channel = connect_to_rabbitmq()
    channel.queue_declare(queue='links_queue', durable=True)

    for link in links:
        channel.basic_publish(exchange='', routing_key='links_queue', body=link)
        print(f"Добавлена ссылка: {link}")

    print("Все ссылки добавлены в очередь.")
