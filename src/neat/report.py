class Report:
    """Base class for a report
    """

    def print_report(self, logger):
        pass


class Reporter:
    """Class to hold multiple reports made by differing modules"""

    def __init__(self) -> None:
        self.reports = []
