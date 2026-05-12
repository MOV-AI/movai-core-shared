"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Dor Marcous (Dor@mov.ai) - 2022
"""
from os import getpid
import logging

# system
PID = getpid()

# logging
USER_LOG_TAG = "user_log"
UI_LOG_TAG = "ui"
CALLBACK_LOGGER = "CALLBACK_LOGGER"
MAX_LOG_QUERY = 1000000
MIN_LOG_QUERY = 0
DEFAULT_LOG_LIMIT = 1000
DEFAULT_LOG_OFFSET = 0
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_TEXT_FORMAT = "[%(levelname)s][%(asctime)s][%(module)s][%(funcName)s][%(lineno)d]: %(message)s"
LOG_FORMATTER = logging.Formatter(
    LOG_TEXT_FORMAT,
    datefmt=LOG_DATE_FORMAT,
)

# node types
ROS1_NODELET = "ROS1/Nodelet"
ROS1_NODE = "ROS1/Node"
ROS1_PLUGIN = "ROS1/Plugin"
MOVAI_NODE = "MovAI/Node"
MOVAI_STATE = "MovAI/State"
MOVAI_SERVER = "MovAI/Server"
ROS2_NODE = "ROS2/Node"
ROS2_LAUNCH = "ROS2/Launch"
ROS2_LIFECYCLENODE = "ROS2/LifecycleNode"  # left for future use, not supported yet

ROS1_NODE_TYPES = {ROS1_NODELET, ROS1_NODE, ROS1_PLUGIN}
MOVAI_NODE_TYPES = {MOVAI_NODE, MOVAI_STATE, MOVAI_SERVER}
ROS2_NODE_TYPES = {ROS2_NODE, ROS2_LAUNCH}

NODE_TYPES = ROS1_NODE_TYPES | MOVAI_NODE_TYPES | ROS2_NODE_TYPES

# transports
TRANSPORT_ROS1 = "ROS1"
TRANSPORT_ROS2 = "ROS2"
TRANSPORT_REDIS = "Redis"
TRANSPORT_AIOHTTP = "AioHttp"
TRANSPORT_MOVAI = "MovAI"

TRANSPORTS = {TRANSPORT_ROS1, TRANSPORT_ROS2, TRANSPORT_REDIS, TRANSPORT_AIOHTTP, TRANSPORT_MOVAI}

# I/O templates
MOVAI_CONTEXTCLIENT = "MovAI/ContextClient"
MOVAI_CONTEXTSERVER = "MovAI/ContextServer"
MOVAI_DEPENDENCY = "MovAI/Dependency"
MOVAI_DEPENDS = "MovAI/Depends"
MOVAI_EXIT = "MovAI/Exit"
MOVAI_INIT = "MovAI/Init"
MOVAI_TRANSITIONFOR = "MovAI/TransitionFor"
MOVAI_TRANSITIONTO = "MovAI/TransitionTo"

REDIS_SUBSCRIBER = "Redis/Subscriber"
REDIS_VARSUBSCRIBER = "Redis/VarSubscriber"

ROS1_ACTIONCLIENT = "ROS1/ActionClient"
ROS1_ACTIONSERVER = "ROS1/ActionServer"
ROS1_BAG = "ROS1/Bag"
ROS1_NODELETCLIENT = "ROS1/NodeletClient"
ROS1_NODELETSERVER = "ROS1/NodeletServer"
ROS1_PARAMETERSERVER = "ROS1/ParameterServer"
ROS1_PLUGINCLIENT = "ROS1/PluginClient"
ROS1_PLUGINSERVER = "ROS1/PluginServer"
ROS1_PUBLISHER = "ROS1/Publisher"
ROS1_RECONFIGURECLIENT = "ROS1/ReconfigureClient"
ROS1_RECONFIGURESERVER = "ROS1/ReconfigureServer"
ROS1_SERVICECLIENT = "ROS1/ServiceClient"
ROS1_SERVICESERVER = "ROS1/ServiceServer"
ROS1_SUBSCRIBER = "ROS1/Subscriber"
ROS1_TFPUBLISHER = "ROS1/TFPublisher"
ROS1_TFSUBSCRIBER = "ROS1/TFSubscriber"
ROS1_TIMER = "ROS1/Timer"
ROS1_TOPICHZ = "ROS1/TopicHz"

ROS2_PUBLISHER = "ROS2/Publisher"
ROS2_SERVICECLIENT = "ROS2/ServiceClient"
ROS2_SERVICESERVER = "ROS2/ServiceServer"
ROS2_SUBSCRIBER = "ROS2/Subscriber"
ROS2_ACTIONSERVER = "ROS2/ActionServer"
ROS2_ACTIONCLIENT = "ROS2/ActionClient"

AIOHTTP_HTTP = "AioHttp/Http"
AIOHTTP_WEBSOCKET = "AioHttp/Websocket"

# ports templates lists
MOVAI_IO_TEMPLATES = {
    MOVAI_CONTEXTCLIENT,
    MOVAI_CONTEXTSERVER,
    MOVAI_DEPENDENCY,
    MOVAI_DEPENDS,
    MOVAI_EXIT,
    MOVAI_INIT,
    MOVAI_TRANSITIONFOR,
    MOVAI_TRANSITIONTO,
}
REDIS_IO_TEMPLATES = {
    REDIS_SUBSCRIBER,
    REDIS_VARSUBSCRIBER,
}
ROS1_IO_TEMPLATES = {
    ROS1_ACTIONCLIENT,
    ROS1_ACTIONSERVER,
    ROS1_BAG,
    ROS1_NODELETCLIENT,
    ROS1_NODELETSERVER,
    ROS1_PARAMETERSERVER,
    ROS1_PLUGINCLIENT,
    ROS1_PLUGINSERVER,
    ROS1_PUBLISHER,
    ROS1_RECONFIGURECLIENT,
    ROS1_RECONFIGURESERVER,
    ROS1_SERVICECLIENT,
    ROS1_SERVICESERVER,
    ROS1_SUBSCRIBER,
    ROS1_TFPUBLISHER,
    ROS1_TFSUBSCRIBER,
    ROS1_TIMER,
    ROS1_TOPICHZ,
}
ROS2_IO_TEMPLATES = {
    ROS2_SUBSCRIBER,
    ROS2_PUBLISHER,
    ROS2_SERVICECLIENT,
    ROS2_SERVICESERVER,
    ROS2_ACTIONSERVER,
    ROS2_ACTIONCLIENT,
}
AIOHTTP_IO_TEMPLATES = {
    AIOHTTP_HTTP,
    AIOHTTP_WEBSOCKET,
}

# all ports templates
IO_TEMPLATES = (
    MOVAI_IO_TEMPLATES
    | REDIS_IO_TEMPLATES
    | ROS1_IO_TEMPLATES
    | ROS2_IO_TEMPLATES
    | AIOHTTP_IO_TEMPLATES
)

# Port protocols
MOVAI_CONTEXTCLIENTIN = "MovAI/ContextClientIn"
MOVAI_TRANSITION = "MovAI/Transition"

DEFAULT_CALLBACK = "place_holder"

TRANSITION_TYPE = {"Protocol": "Transition", "Transport": "MovAI"}

NAME_REGEX = r"^(\/)?[~@a-zA-Z_0-9-.]+([~@a-zA-Z_0-9-]+)?([\/a-zA-Z_0-9-.]+)?$"
LINK_REGEX = r"^([~@a-zA-Z_0-9-]+)([\/])([\/~@a-zA-Z_0-9]+)+([\/])([~@a-zA-Z_0-9]+)$"
CONFIG_REGEX = r"\$\((param|config|var|flow)[^$)]+\)"

TIMEOUT_PROCESS_SIGINT = 3  # seconds
TIMEOUT_PROCESS_SIGTERM = 2  # seconds
TIMEOUT_SEND_CMD_RESPONSE = 10  # seconds

# Domains
INTERNAL_DOMAIN = "internal"

# Roles
ADMIN_ROLE = "ADMIN"
OPERATOR_ROLE = "OPERATOR"
DEPLOYER_ROLE = "DEPLOYER"

# permissions
READ_PERMISSION = "read"
UPDATE_PERMISSION = "update"
CREATE_PERMISSION = "create"
DELETE_PERMISSION = "delete"
EXECUTE_PERMISSION = "execute"
RESET_PERMISSION = "reset"

# container_names
INFLUXDB_HOST = "influxdb"
MESSAGE_SERVER_HOST = "message-server"


# inluxdb DB names:
LOGS_INFLUX_DB = "logs"
METRICS_INFLUX_DB = "metrics"
PLATFORM_METRICS_INFLUX_DB = "platform_metrics"
PLATFORM_ALERTS_INFLUX_DB = "platform_alerts"
STRESS_INFLUX_DB = "stress"
INFLUXDB_DB_NAMES = [LOGS_INFLUX_DB, METRICS_INFLUX_DB, STRESS_INFLUX_DB]

# inluxdb measurements names:
SYSLOG_MEASUREMENT = "syslog"
LOGS_MEASUREMENT = "app_logs"
METRICS_MEASUREMENT = "metric_logs"
STRESS_MEASUREMENT = "stress_logs"
ALERT_MEASUREMENT = "alert_events"

# Message-Server msgs types:
LOGS_HANDLER_MSG_TYPE = "logs"
COMMAND_HANDLER_MSG_TYPE = "command"
SYSLOGS_HANDLER_MSG_TYPE = "syslog"
LOGS_QUERY_HANDLER_MSG_TYPE = "logs_query"
METRICS_HANDLER_MSG_TYPE = "metrics"
METRICS_QUERY_HANDLER_MSG_TYPE = "metrics_query"
NOTIFICATIONS_HANDLER_MSG_TYPE = "notifications"
ALERT_QUERY_HANDLER_MSG_TYPE = "alerts_query"

CALLBACK_STDOUT_COLORS = {
    logging.DEBUG: "\033[36m",
    logging.INFO: "\u001b[0m",
    logging.WARNING: "\x1b[33m",
    logging.ERROR: "\x1b[31;20m",
    logging.CRITICAL: "\x1b[41;1m",
    logging.WARN: "\x1b[33m",
}

SPAWNER_STDOUT_COLORS = {
    logging.DEBUG: "\x1b[1;34m",
    logging.INFO: "\x1b[1;37m",
    logging.WARNING: "\x1b[1;33m",
    logging.ERROR: "\x1b[31;1m",
    logging.CRITICAL: "\x1b[41;1m",
}


class DeactivationType:
    REQUESTED = "requested"
    AUTO_CLEARED = "auto_cleared"
