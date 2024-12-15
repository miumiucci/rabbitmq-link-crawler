import aio_pika
import asyncio
import os
import requests
from bs4 import BeautifulSoup

processed_links = set()  # Отслеживаем обработанные ссылки

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

async def process_message(message: aio_pika.abc.AbstractIncomingMessage):
    async with message.process():
        url = message.body.decode()
        if url in processed_links:
            print(f"Ссылка уже обработана: {url}")
            return
        processed_links.add(url)

        base_domain = url.split('/')[0] + '//' + url.split('/')[2]

        try:
            links = extract_links(url, base_domain)

            # Публикация новых ссылок в очередь
            connection = await aio_pika.connect_robust(
                host=os.getenv('RABBITMQ_HOST', 'localhost'),
                port=int(os.getenv('RABBITMQ_PORT', '5672')),
                login=os.getenv('RABBITMQ_USER', 'guest'),
                password=os.getenv('RABBITMQ_PASSWORD', 'guest')
            )
            async with connection:
                channel = await connection.channel()
                for link in links:
                    await channel.default_exchange.publish(
                        aio_pika.Message(body=link.encode()),
                        routing_key="links_queue",
                    )
                    print(f"Добавлена ссылка: {link}")
        except Exception as e:
            print(f"Ошибка при обработке {url}: {e}")

async def main():
    connection = await aio_pika.connect_robust(
        host=os.getenv('RABBITMQ_HOST', 'localhost'),
        port=int(os.getenv('RABBITMQ_PORT', '5672')),
        login=os.getenv('RABBITMQ_USER', 'guest'),
        password=os.getenv('RABBITMQ_PASSWORD', 'guest')
    )

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        queue = await channel.declare_queue("links_queue", durable=True)

        print("Ожидание сообщений. Для выхода нажмите CTRL+C.")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                await process_message(message)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Consumer остановлен.")
