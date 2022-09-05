class Error(Exception):
    """Base class for exceptions in this module."""


class LoadDefaultDataError(Error):
    """Raised if an issue occurs when creating default data."""


class UomConversionError(Error):
    """Raised during uom conversion. If an error occurs."""


class ValidationError(Error):
    """Raised if table field validation fails."""