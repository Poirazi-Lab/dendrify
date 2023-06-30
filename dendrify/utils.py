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
        '%(levelname)s [%(name)s:%(lineno)d]\n%(message)s\n')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


class DimensionlessCompartmentError(Exception):
    """
    Raise this error when an operation that is invalid for dimensionless
    compartments is performed.
    """
    pass


class DuplicateEquationsError(Exception):
    """
    Raise this error when a user tries to add the same equations twice.
    """
    pass
