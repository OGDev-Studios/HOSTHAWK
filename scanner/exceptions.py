class HostHawkException(Exception):
    pass


class ScannerException(HostHawkException):
    pass


class NetworkScanException(ScannerException):
    pass


class PortScanException(ScannerException):
    pass


class VulnerabilityScanException(ScannerException):
    pass


class ConfigurationException(HostHawkException):
    pass


class ValidationException(HostHawkException):
    pass


class TimeoutException(ScannerException):
    pass


class PermissionException(ScannerException):
    pass


class InvalidTargetException(ValidationException):
    pass


class InvalidPortRangeException(ValidationException):
    pass


class ReportGenerationException(HostHawkException):
    pass


class DNSEnumerationException(ScannerException):
    pass


class SNMPScanException(ScannerException):
    pass


class WebCrawlerException(ScannerException):
    pass
