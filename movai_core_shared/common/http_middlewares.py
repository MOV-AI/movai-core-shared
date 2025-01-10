""" Common middlewares used by HTTP services in different MovAI applications """

from contextlib import AbstractContextManager, ExitStack
from json import JSONDecodeError
import re
import requests
import bleach
from typing import Any, Awaitable, Callable, Iterable, List, Union
from aiohttp import web
import urllib.parse

from movai_core_shared.exceptions import InvalidToken, TokenExpired, TokenRevoked
from movai_core_shared.logger import Log

from dal.classes.utils.token import UserToken


LOGGER = Log.get_logger(__name__)


class JWTMiddleware:
    """JWT authentication middleware"""
    _secret: str
    _get_user_func: Callable[[str, str, str], Any]
    _safelist: List[str]

    def __init__(self, secret: str, get_user_func: Callable[[str, str, str], Any], safelist: Iterable[str] = None):
        """Initialize middleware
        secret -> the JWT secret
        get_user_func -> a function that returns a user object
        safelist -> an initial pattern list
        """
        self._secret = secret
        self._get_user_func = get_user_func
        self._safelist = []
        if safelist is not None:
            self._safelist.extend(safelist)

    def add_safe(self, paths: Union[str, List[str]], prefix: str = None) -> None:
        """Add paths to bypass auth list"""

        if isinstance(paths, str):
            paths = [paths]

        if prefix is None:
            prefix = ""

        prefix = prefix.rstrip("/")

        self._safelist.extend([prefix + path for path in paths])

    def _is_safe(self, request: web.Request) -> bool:
        q_string = request.query_string
        xss_check_dict = urllib.parse.parse_qs(q_string)
        for key, value in request.query.items():
            if key in xss_check_dict and value == bleach.clean(xss_check_dict[key][0]):
                xss_check_dict.pop(key)
            else:
                return False
        if q_string.encode("ascii", "ignore").decode() != q_string or len(xss_check_dict) > 0:
            # contains non-ascii chars
            return False
        if bleach.clean(str(request.headers["Host"])) != str(request.headers["Host"]):
            return False
        decoded_params = urllib.parse.unquote(q_string)
        if "<script>" in decoded_params:
            raise requests.exceptions.InvalidHeader("Risky URL params passed")
        if request.method == "OPTIONS":
            return True

        for pattern in self._safelist:
            if re.match(pattern, request.path) is not None:
                return True

        # else
        return False

    @web.middleware
    async def middleware(self, request, handler):
        """the actual middleware JWT authentication verify"""

        safe = self._is_safe(request)
        token_str = None
        try:
            if "token" in request.query:
                token_str = request.query["token"]
            elif "Authorization" in request.headers:
                _, token_str = request.headers["Authorization"].strip().split(" ")
        except ValueError:
            if not safe:
                raise web.HTTPForbidden(reason="Invalid authorization header")

        if token_str is None and not safe:
            raise web.HTTPUnauthorized(reason="Missing authorization token")

        token_obj = None
        try:
            if not safe:
                UserToken.verify_token(token_str)
                token_obj = UserToken.get_token_obj(token_str)
        except InvalidToken:
            raise web.HTTPForbidden(reason="Invalid authorization token")
        except TokenExpired as t:
            raise web.HTTPForbidden(reason=str(t))
        except TokenRevoked as t:
            raise web.HTTPForbidden(reason=str(t))

        if token_obj:
            try:
                try:
                    request["user"] = self._get_user_func(
                        token_obj.user_type, token_obj.domain_name, token_obj.account_name
                    )
                except ValueError:
                    error_msg = "Users's type is invalid."
                    LOGGER.error(error_msg)
                    raise InvalidToken(error_msg)
            except Exception as e:
                LOGGER.error(e)
                raise web.HTTPForbidden(reason=e.__str__())
        return await handler(request)


# Returns an async function (middleware for aiohttp)
def apply_scope_contextmanagers(scope: str, context_managers: List[AbstractContextManager]) -> Callable[..., Awaitable[Any]]:
    @web.middleware
    async def apply_scope_contextmanagers(request, handler):
        """
        Middleware to apply context managers based on the request's scope and record name.

        This middleware dynamically applies a set of context managers associated with a specific
        scope when one of its records is being modified.
        """
        request_scope = request.match_info.get("scope")
        record_name = request.match_info.get("name")
        try:
            record_data = await request.json()
            record_label = record_data.get("data", {}).get("label")
        except JSONDecodeError:
            record_label = None

        if request_scope == scope and request.method in ("POST", "PUT", "DELETE"):
            with ExitStack() as stack:
                for context_manager in context_managers:
                    stack.enter_context(context_manager(record_name, record_label))

                # Wait for the request to resolve
                response = await handler(request)
        else:
            response = await handler(request)

        return response
    return apply_scope_contextmanagers


@web.middleware
async def redirect_not_found(request, handler):
    response = await handler(request)
    if response.status != 404:
        return response
    message = response.message
    return web.json_response({"error": message}, headers={"Server": "Movai-server"})
