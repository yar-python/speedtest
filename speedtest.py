import argparse
import sys

from logging_config import logger, setup_logging
from measure import (
    BYTES_PER_MB,
    ConnectionMode,
    DEFAULT_REQUEST_COUNT,
    probe_ssl,
    run_measurement,
)

DEFAULT_URL = "https://speed.cloudflare.com/__down?bytes={bytes}"
DEFAULT_SIZE_MB = 5.0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Замер скорости скачивания по URL.")
    parser.add_argument("url", nargs="?", help="URL (по умолчанию Cloudflare)")
    parser.add_argument(
        "--size",
        type=float,
        default=None,
        metavar="MB",
        help=f"Объём Cloudflare-файла в МБ (по умолчанию {DEFAULT_SIZE_MB:g})",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=DEFAULT_REQUEST_COUNT,
        metavar="N",
        help=f"Число запросов (по умолчанию {DEFAULT_REQUEST_COUNT})",
    )
    parser.add_argument("--timeout", type=float, default=60, help="Таймаут, сек")
    parser.add_argument(
        "--connection",
        type=ConnectionMode,
        choices=list(ConnectionMode),
        default=ConnectionMode.REUSE,
        help="reuse — Session keep-alive; new — без сохранения соединения",
    )
    parser.add_argument("--verbose", action="store_true", help="Детали каждого запроса")
    args = parser.parse_args(argv)

    if args.size is not None and args.size <= 0:
        parser.error("--size должен быть больше 0")
    if args.count < 1:
        parser.error("--count должен быть не меньше 1")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    setup_logging(args.verbose)

    size_mb = args.size if args.size is not None else DEFAULT_SIZE_MB
    if args.url:
        url = args.url
        if args.size is not None:
            logger.warning("--size игнорируется: задан свой URL")
    else:
        url = DEFAULT_URL.format(bytes=int(size_mb * BYTES_PER_MB))
        logger.info("URL не указан, Cloudflare ~%.2f МБ", size_mb)

    verify = probe_ssl(url, args.timeout)
    return run_measurement(
        url=url,
        timeout=args.timeout,
        verify=verify,
        request_count=args.count,
        connection_mode=args.connection,
    )


if __name__ == "__main__":
    sys.exit(main())
