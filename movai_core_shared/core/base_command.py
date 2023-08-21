from abc import ABC, abstractclassmethod, abstractmethod
import sys

from movai_core_shared.logger import Log

class BaseCommand(ABC):
    """Base Class for the various tools commands."""

    def __init__(self, **kwargs) -> None:
        self.log = Log.get_logger(__name__)
        self.kwargs = kwargs

    def safe_execute(self, **kwargs) -> None:
        try:
            self.execute(**kwargs)
            sys.exit(0)
        except Exception as e:
            self.log.error(str(e))
            sys.exit(1)

    @abstractmethod
    def execute(self, **kwargs) -> None:
        """Executes the relevant command."""

    @abstractclassmethod
    def define_arguments(cls, subparsers) -> None:
        """An abstract function for implementing command arguments.

        Args:
            subparsers (_type_): _description_
        """
