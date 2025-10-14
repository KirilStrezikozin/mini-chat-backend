import logging

root_logger = logging.getLogger("app")
root_logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter(
        "%(asctime)s %(levelname)-8s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
)

root_logger.addHandler(handler)
root_logger.propagate = False
