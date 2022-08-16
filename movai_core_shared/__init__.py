"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Dor Marcous (Dor@mov.ai) - 2022
"""
# pylint: skip-file
from movai_core_shared.consts import (
    ROS1_NODELET,
    ROS1_NODE,
    ROS1_PLUGIN,
    MOVAI_NODE,
    MOVAI_STATE,
    MOVAI_SERVER,
    ROS2_NODE,
    ROS2_LIFECYCLENODE,
    NODE_TYPE,
    MOVAI_INIT,
    MOVAI_TRANSITIONFOR,
    MOVAI_TRANSITIONTO,
    MOVAI_DEPENDS,
    MOVAI_DEPENDENCY,
    MOVAI_WIDGET,
    REDIS_SUBSCRIBER,
    ROS1_TIMER,
    ROS1_RECONFIGURECLIENT,
    ROS1_SERVICECLIENT,
    ROS1_ACTIONSERVER,
    ROS1_ACTIONCLIENT,
    ROS1_SUBSCRIBER,
    ROS1_TFPUBLISHER,
    ROS1_SERVICESERVER,
    ROS1_PUBLISHER,
    ROS1_TFSUBSCRIBER,
    ROS1_PLUGINCLIENT,
    ROS1_PLUGINSERVER,
    ROS1_NODELETCLIENT,
    ROS1_NODELETSERVER,
    FLASK_HTTPENDPOINT,
    HTTP_ENDPOINT,
    HTTP_SOCKETIO,
    PORTS_TEMPLATE,
    TRANSITION_TYPE,
    NAME_REGEX,
    LINK_REGEX,
    CONFIG_REGEX,
    TIMEOUT_PROCESS_SIGINT,
    TIMEOUT_PROCESS_SIGTERM,
)
from movai_core_shared.envvars import (
    MOVAI_STDOUT_VERBOSITY_LEVEL,
    MOVAI_FLEET_LOGS_VERBOSITY_LEVEL,
    MOVAI_LOGFILE_VERBOSITY_LEVEL,
    MOVAI_GENERAL_VERBOSITY_LEVEL,
    APP_PATH,
    APP_LOGS,
    LD_LIBRARY_PATH,
    MOVAI_HOME,
    PATH,
    PKG_CONFIG_PATH,
    PRODUCTION,
    PYTHONPATH,
    PYTHON_EXTERNAL_LIBS,
    REDIS_LOCAL_HOST,
    REDIS_LOCAL_PORT,
    REDIS_MASTER_HOST,
    REDIS_MASTER_PORT,
    ROSLISP_PACKAGE_DIRECTORIES,
    ROS_DISTRO,
    ROS_ETC_DIR,
    ROS_MASTER_URI,
    ROS_PACKAGE_PATH,
    ROS_PYTHON_VERSION,
    ROS_ROOT,
    ROS_VERSION,
    ROS1_MOVAI_WS,
    ROS1_USER_WS,
    ROS1_WS,
    ROS2_DISTRO,
    ROS1_LIB,
    ROS2_LIB,
    ROS2_PATH,
    ROS1_NODELET_CMD,
    ENVIRON_ROS1,
    ENVIRON_ROS2,
    ENVIRON_GDNODE,
    ENVIRON_GDNODE_INJECT,
    REST_SCOPES,
    SCOPES_TO_TRACK,
    JWT_SECRET_KEY,
    JWT_EXPIRATION_DELTA,
    JWT_REFRESH_EXPIRATION_DELTA,
)

from movai_core_shared.exceptions import (
    MovaiException,
    DoesNotExist,
    AlreadyExist,
    InvalidStructure,
    TransitionException,
    ResourceException,
    CommandError,
    ActiveFlowError,
)
from movai_core_shared.logger import Log, LogAdapter

__all__ = [
    "Log",
    "MovaiException",
    "DoesNotExist",
    "AlreadyExist",
    "InvalidStructure",
    "TransitionException",
    "ResourceException",
    "CommandError",
    "ActiveFlowError",
    "MOVAI_STDOUT_VERBOSITY_LEVEL",
    "MOVAI_FLEET_LOGS_VERBOSITY_LEVEL",
    "MOVAI_LOGFILE_VERBOSITY_LEVEL",
    "MOVAI_GENERAL_VERBOSITY_LEVEL",
    "APP_PATH",
    "APP_LOGS",
    "LD_LIBRARY_PATH",
    "MOVAI_HOME",
    "PATH",
    "PKG_CONFIG_PATH",
    "PRODUCTION",
    "PYTHONPATH",
    "PYTHON_EXTERNAL_LIBS",
    "REDIS_LOCAL_HOST",
    "REDIS_LOCAL_PORT",
    "REDIS_MASTER_HOST",
    "REDIS_MASTER_PORT",
    "ROSLISP_PACKAGE_DIRECTORIES",
    "ROS_DISTRO",
    "ROS_ETC_DIR",
    "ROS_MASTER_URI",
    "ROS_PACKAGE_PATH",
    "ROS_PYTHON_VERSION",
    "ROS_ROOT",
    "ROS_VERSION",
    "ROS1_MOVAI_WS",
    "ROS1_USER_WS",
    "ROS1_WS",
    "ROS2_DISTRO",
    "ROS1_LIB",
    "ROS2_LIB",
    "ROS2_PATH",
    "ROS1_NODELET_CMD",
    "ENVIRON_ROS1",
    "ENVIRON_ROS2",
    "ENVIRON_GDNODE",
    "ENVIRON_GDNODE_INJECT",
    "REST_SCOPES",
    "SCOPES_TO_TRACK",
    "JWT_SECRET_KEY",
    "JWT_EXPIRATION_DELTA",
    "JWT_REFRESH_EXPIRATION_DELTA",
    "ROS1_NODELET",
    "ROS1_NODE",
    "ROS1_PLUGIN",
    "MOVAI_NODE",
    "MOVAI_STATE",
    "MOVAI_SERVER",
    "ROS2_NODE",
    "ROS2_LIFECYCLENODE",
    "NODE_TYPE",
    "MOVAI_INIT",
    "MOVAI_TRANSITIONFOR",
    "MOVAI_TRANSITIONTO",
    "MOVAI_DEPENDS",
    "MOVAI_DEPENDENCY",
    "MOVAI_WIDGET",
    "REDIS_SUBSCRIBER",
    "ROS1_TIMER",
    "ROS1_RECONFIGURECLIENT",
    "ROS1_SERVICECLIENT",
    "ROS1_ACTIONSERVER",
    "ROS1_ACTIONCLIENT",
    "ROS1_SUBSCRIBER",
    "ROS1_TFPUBLISHER",
    "ROS1_SERVICESERVER",
    "ROS1_PUBLISHER",
    "ROS1_TFSUBSCRIBER",
    "ROS1_PLUGINCLIENT",
    "ROS1_PLUGINSERVER",
    "ROS1_NODELETCLIENT",
    "ROS1_NODELETSERVER",
    "FLASK_HTTPENDPOINT",
    "HTTP_ENDPOINT",
    "HTTP_SOCKETIO",
    "PORTS_TEMPLATE",
    "TRANSITION_TYPE",
    "NAME_REGEX",
    "LINK_REGEX",
    "CONFIG_REGEX",
    "TIMEOUT_PROCESS_SIGINT",
    "TIMEOUT_PROCESS_SIGTERM",
    "LogAdapter",
]
