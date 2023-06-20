import logging


def get_logger(name):
    """A simple function that returns a logger

    Parameters
    ----------
    name : str
        The name used for logging, should normally be the module name as
        returned by ``__name__``.

    Returns
    -------
    logger : logging.Logger
        Used for nicely displaying error, warnings etc.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(levelname)s - %(name)s:  %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
