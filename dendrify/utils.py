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
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(levelname)s [%(name)s:%(lineno)d]\n%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


class ParametersError(Exception):
    """Raise this when something is wrong with the parameters set by the user"""
