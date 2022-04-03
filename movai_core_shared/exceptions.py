"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Manuel Silva (manuel.silva@mov.ai) - 2020
   - Tiago Paulino (tiago@mov.ai) - 2020
   - Dor Marous (Dor@mov.ai) - 2022
"""

# The exceptions used by MOV.AI api


class MovaiException(Exception):
    """General MovAI API exception occurred."""


class DoesNotExist(MovaiException):
    """Raised when something is not found."""


class AlreadyExist(MovaiException):
    """Raised when something already exists."""


class InvalidStructure(MovaiException):
    """Raised when structure to be saved in DB is invalid."""


class TransitionException(MovaiException):
    """Raised a GD_Node transition happens."""


class ResourceException(MovaiException):
    """
    A resource handling exception
    """


class CommandError(MovaiException):
    """
    Raise when the command does not exist
    """


class ActiveFlowError(MovaiException):
    """
    Raise when the command requires an active flow
    """
