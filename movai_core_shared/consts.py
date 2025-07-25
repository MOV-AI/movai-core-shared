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

# Constants
USER_LOG_TAG = "user_log"
UI_LOG_TAG = "ui"
CALLBACK_LOGGER = "CALLBACK_LOGGER"
MAX_LOG_QUERY = 1000000
MIN_LOG_QUERY = 0
DEFAULT_LOG_LIMIT = 1000
DEFAULT_LOG_OFFSET = 0
ROS1_NODELET = "ROS1/Nodelet"
ROS1_NODE = "ROS1/Node"
ROS1_PLUGIN = "ROS1/Plugin"
MOVAI_NODE = "MovAI/Node"
MOVAI_STATE = "MovAI/State"
MOVAI_SERVER = "MovAI/Server"
DEFAULT_CALLBACK = "place_holder"
ROS2_NODE = "ROS2/Node"
ROS2_LIFECYCLENODE = "ROS2/LifecycleNode"

NODE_TYPE = [
    ROS1_NODELET,
    ROS1_NODE,
    ROS1_PLUGIN,
    MOVAI_NODE,
    MOVAI_STATE,
    MOVAI_SERVER,
    ROS2_NODE,
    ROS2_LIFECYCLENODE,
]

MOVAI_INIT = "MovAI/Init"
MOVAI_TRANSITION = "MovAI/Transition"
MOVAI_TRANSITIONFOR = "MovAI/TransitionFor"
MOVAI_TRANSITIONTO = "MovAI/TransitionTo"
MOVAI_CONTEXTCLIENTIN = "MovAI/ContextClientIn"
MOVAI_DEPENDS = "MovAI/Depends"
MOVAI_DEPENDENCY = "MovAI/Dependency"

MOVAI_WIDGET = "MovAI/Widget"


REDIS_SUBSCRIBER = "Redis/Subscriber"

ROS1_TIMER = "ROS1/Timer"
ROS1_RECONFIGURECLIENT = "ROS1/ReconfigureClient"
ROS1_SERVICECLIENT = "ROS1/ServiceClient"
ROS1_ACTIONSERVER = "ROS1/ActionServer"
ROS1_ACTIONCLIENT = "ROS1/ActionClient"
ROS1_SUBSCRIBER = "ROS1/Subscriber"
ROS1_TFPUBLISHER = "ROS1/TFPublisher"
ROS1_SERVICESERVER = "ROS1/ServiceServer"
ROS1_PUBLISHER = "ROS1/Publisher"
ROS1_TFSUBSCRIBER = "ROS1/TFSubscriber"
ROS1_PLUGINCLIENT = "ROS1/PluginClient"
ROS1_PLUGINSERVER = "ROS1/PluginServer"
ROS1_NODELETCLIENT = "ROS1/NodeletClient"
ROS1_NODELETSERVER = "ROS1/NodeletServer"

FLASK_HTTPENDPOINT = "Flask/HttpEndpoint"

HTTP_ENDPOINT = "Http/Endpoint"
HTTP_SOCKETIO = "Http/SocketIO"

PORTS_TEMPLATE = [
    MOVAI_INIT,
    MOVAI_TRANSITIONFOR,
    MOVAI_TRANSITIONTO,
    MOVAI_DEPENDS,
    MOVAI_DEPENDENCY,
    ROS1_NODELETCLIENT,
    ROS1_NODELETSERVER,
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
    FLASK_HTTPENDPOINT,
    HTTP_ENDPOINT,
    HTTP_SOCKETIO,
]

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
STRESS_INFLUX_DB = "stress"
INFLUXDB_DB_NAMES = [LOGS_INFLUX_DB, METRICS_INFLUX_DB, STRESS_INFLUX_DB]

# inluxdb measurements names:
SYSLOG_MEASUREMENT = "syslog"
LOGS_MEASUREMENT = "app_logs"
METRICS_MEASUREMENT = "metric_logs"
STRESS_MEASUREMENT = "stress_logs"

# Message-Server msgs types:
LOGS_HANDLER_MSG_TYPE = "logs"
COMMAND_HANDLER_MSG_TYPE = "command"
SYSLOGS_HANDLER_MSG_TYPE = "syslog"
LOGS_QUERY_HANDLER_MSG_TYPE = "logs_query"
METRICS_HANDLER_MSG_TYPE = "metrics"
METRICS_QUERY_HANDLER_MSG_TYPE = "metrics_query"
NOTIFICATIONS_HANDLER_MSG_TYPE = "notifications"
ALERTS_HANDLER_METRIC_TYPE = "alerts"

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
