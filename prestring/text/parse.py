import logging

logger = logging.getLogger(__name__)


def main(filename: str) -> None:
    pass


if __name__ == "__main__":
    import sys

    main(sys.argv[1:] or [__file__])
