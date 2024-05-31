"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Erez Zomer (erez@mov.ai) - 2022
"""
from abc import ABC, abstractmethod
import sys

from movai_core_shared.logger import Log


class BaseCommand(ABC):
    """Base Class for the various tools commands."""

    def __init__(self, **kwargs) -> None:
        self.log = Log.get_logger(__name__)
        self._name = kwargs.get("name") if "name" in kwargs else self.__class__.__name__
        self.kwargs = kwargs

    def safe_execute(self, **kwargs) -> None:
        """Executes the command in try except block."""
        try:
            self.execute(**kwargs)
            sys.exit(0)
        except Exception as e:
            self.log.error(str(e))
            sys.exit(1)

    @abstractmethod
    def execute(self, **kwargs) -> None:
        """Executes the relevant command."""

    @classmethod
    @abstractmethod
    def define_arguments(cls, subparsers) -> None:
        """An abstract function for implementing command arguments.

        Args:
            subparsers (_type_): _description_
        """

    @property
    def name(self) -> str:
        """return the name of the command"""
        return self._name.lower()
