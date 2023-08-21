"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Manuel Silva (manuel.silva@mov.ai) - 2020
   - Tiago Paulino (tiago@mov.ai) - 2020
   - Dor Marcous (Dor@mov.ai) - 2022
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


class InitializationError(MovaiException):
    """Failure to initialize an object."""


class RestrictedPathError(MovaiException):
    """The client tries to access restricted path."""


class UserError(MovaiException):
    """A base class for user errors."""

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class UserAlreadyExist(UserError):
    """The requested user is already exist in the system."""


class UserDoesNotExist(UserError):
    """The requested user is not exist in the system."""


class UserPermissionsError(UserError):
    """The user's permissions can't be retrieved."""


class LoginError(MovaiException):
    """A base class for login errors."""

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class DomainDoesNotExist(LoginError):
    """The required domain is not registered in the systm."""


class AuthorizationError(LoginError):
    """Failure to get access to the system."""


class InvalidCredentials(LoginError):
    """Supplied credentials are incorrect."""


class TokenError(LoginError):
    """General Token error"""


class InvalidToken(TokenError):
    """Failed to get access token."""


class TokenExpired(TokenError):
    """Token's signature has expired."""


class TokenRevoked(TokenError):
    """Token have been revoked."""


class AclObjectError(MovaiException):
    """a base class for AclObject model exceptions."""

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class AclObjectDoesNotExist(AclObjectError):
    """the required object is not found on DB."""


class AclObjectAlreadyExist(AclObjectError):
    """the required object is already found on DB."""


class AclObjectIDMismatch(AclObjectError):
    """The name and the ID of the required object are mismatched."""


class AclObjectInvalidAttribute(AclObjectError):
    """The required attribute does id not defined in AclObject scheme."""


class LdapConfigError(MovaiException):
    """a base class for LdapConfig model exceptions."""

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class LdapConfigAlreadyExist(LdapConfigError):
    """A configuration with the supplied name is already exist in DB."""


class LdapConfigDoesNotExist(LdapConfigError):
    """the required configuration is not found on DB."""


class LdapConfigMissingParameter(LdapConfigError):
    """a required parameter is missing in supplied LdapConfig dictionary."""


class LdapConfigInvalidStructure(LdapConfigError):
    """a required parameter is missing in supplied LdapConfig dictionary."""


class RoleError(MovaiException):
    """a base class for Role model exceptions."""

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class RoleDoesNotExist(RoleError):
    """the requested role is not found on DB."""


class RoleAlreadyExist(RoleError):
    """the requested role is already found in DB."""


class PasswordError(MovaiException):
    """a base class for password exceptions."""

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class PasswordComplexityError(PasswordError):
    """The password doesn't comply with complexity settings."""


class PasswordASCIIFormatError(MovaiException):
    """The supplied password isn't comprised of ascii symbols."""


class SecretKeyError(MovaiException):
    """a base class for Role model exceptions."""

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class SecretKeyDoesNotExist(SecretKeyError):
    """the requested secret key is not found on DB."""


class SecretKeyAlreadyExist(SecretKeyError):
    """the requested secret key is already found in DB."""


class ArgumentError(MovaiException):
    """The supplied argument is invalid."""


class HandlerNotFoundError(MovaiException):
    """The message has no suitable handler."""


class MessageError(MovaiException):
    """There are missing keys in the message."""


class MessageFormatError(MessageError):
    """There are missing keys in the message."""


class MetricError(MessageError):
    """Something is wrong with the metric."""


class QueryError(MovaiException):
    """Something is wrong with the metric."""


class UnknownRequestError(MovaiException):
    """The request format is unknown."""


class ConfigurationDoesNotExist(DoesNotExist):
    """The requested configuration could not be found."""


class DBHandlerError(MovaiException):
    """General exception in DBHandler."""


class TimeError(MovaiException):
    """The supplied time is not a timestamp"""
