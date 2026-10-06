import time
from enum import Enum

import requests
from requests.exceptions import RequestException, SSLError

from logging_config import logger

DEFAULT_REQUEST_COUNT = 10
BYTES_PER_MB = 1024 * 1024
HEADERS = {"User-Agent": "speedtest/1.0", "Cache-Control": "no-cache"}


class ConnectionMode(str, Enum):
    REUSE = "reuse"
    NEW = "new"


def probe_ssl(url: str, timeout: float) -> bool:
    """True — SSL OK; False — дальше без проверки сертификата."""
    try:
        with requests.get(
            url, timeout=timeout, headers=HEADERS, verify=True, stream=True
        ) as response:
            response.close()
        logger.info("Проверка SSL: OK")
        return True
    except SSLError as err:
        logger.warning(
            "Проверка SSL не удалась: %s. Замер без проверки сертификата.",
            err,
        )
        return False


def fetch(
    url: str,
    timeout: float,
    verify: bool,
    session: requests.Session | None = None,
) -> tuple[float, int]:
    started = time.perf_counter()
    client = session if session is not None else requests
    kwargs = {"timeout": timeout, "headers": HEADERS}
    if session is None:
        kwargs["verify"] = verify
    response = client.get(url, **kwargs)
    response.raise_for_status()
    return time.perf_counter() - started, len(response.content)


def run_requests(
    url: str,
    timeout: float,
    verify: bool,
    request_count: int,
    session: requests.Session | None = None,
) -> int:
    times: list[float] = []
    total_bytes = 0

    for i in range(1, request_count + 1):
        try:
            elapsed, nbytes = fetch(url, timeout, verify, session)
        except RequestException as err:
            logger.error("Запрос %s/%s не удался: %s", i, request_count, err)
            return 1

        times.append(elapsed)
        total_bytes += nbytes
        logger.debug("Запрос %s/%s: %.3f с, %s байт", i, request_count, elapsed, nbytes)
        filled = int(20 * i / request_count)
        logger.info("[%s%s] %s/%s", "#" * filled, "-" * (20 - filled), i, request_count)

    total_sec = sum(times)
    total_mb = total_bytes / BYTES_PER_MB
    speed = total_mb / total_sec if total_sec else 0.0
    logger.info(
        f"Среднее время запроса: {total_sec / request_count:.3f} с\n"
        f"Объём скачанных данных: {total_bytes} байт ({total_mb:.2f} МБ)\n"
        f"Скорость: {speed:.2f} МБ/с"
    )
    return 0


def run_measurement(
    url: str,
    timeout: float,
    verify: bool = True,
    request_count: int = DEFAULT_REQUEST_COUNT,
    connection_mode: ConnectionMode = ConnectionMode.REUSE,
) -> int:
    if connection_mode == ConnectionMode.REUSE:
        logger.info("Старт: %s запросов к %s (keep-alive)", request_count, url)
        with requests.Session() as session:
            session.verify = verify
            return run_requests(url, timeout, verify, request_count, session)

    logger.info("Старт: %s запросов к %s (новые соединения)", request_count, url)
    return run_requests(url, timeout, verify, request_count)
