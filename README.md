# Замер скорости интернета

Скрипт N раз (по умолчанию 10) выполняет запрос на указанный URL (по умолчанию speed.cloudflare.com), считает среднее время, объём и скорость в **МБ/с**.
Запросы через [requests](https://requests.readthedocs.io/).

## Установка

```bash
git clone https://github.com/yar-python/speedtest.git
cd speedtest
python3 -m pip install -r requirements.txt
```

Нужны Python **3.9+** и `requests`.

## Запуск

```bash
python3 speedtest.py                         # Cloudflare ~5 МБ, 10 запросов
python3 speedtest.py "https://example.com/file" # свой URL (опция --size игнорируется)

# Флаги для настройки
python3 speedtest.py --size 10               # объём файла Cloudflare, МБ (по умолчанию 5)
python3 speedtest.py --count 5               # число запросов (по умолчанию 10)

python3 speedtest.py --timeout 120           # таймаут для каждого запроса, сек (по умолчанию 60)
python3 speedtest.py --verbose               # вывести детали каждого запроса

# Режим соединения (Connection)
python3 speedtest.py --connection reuse      # Session keep-alive (по умолчанию)
python3 speedtest.py --connection new        # новое соединение для каждого запроса
```
### Режимы соединения
- reuse: все запросы используют одно соединение (быстрее, ближе к реальному скачиванию файла).
- new: для каждого запроса создаётся новое соединение (имитирует скачивания с нуля, например, как в браузере при многократных загрузках/открытиях новых вкладок, а также помогает оценить влияние установления соединения и handshake TLS).

Перед замером проверяется SSL. Если не прошла — предупреждение, замер без проверки сертификата.

## Структура
| Файл                | Роль            |
| ------------------- | --------------- |
| `speedtest.py`      | CLI             |
| `measure.py`        | запросы и замер |
| `logging_config.py` | логи            |
| `requirements.txt`  | зависимости     |
