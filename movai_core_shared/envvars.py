"""Environment variables.

Attributes:
    DETACHED_PROCESS_OUTPUT (str): Where to forward logs from e.g. tools that
        run outside the entrypoint.

"""
import os
from logging import DEBUG, getLevelName
import socket
from .consts import (
    MESSAGE_SERVER_HOST,
    ADMIN_ROLE,
    LOGS_INFLUX_DB,
    METRICS_INFLUX_DB,
    STRESS_INFLUX_DB,
)

# Setting for logging verbosity levels
# Will be set only once at startup
MOVAI_STDOUT_VERBOSITY_LEVEL = DEBUG  # Minimum log supported by handlers
MOVAI_FLEET_LOGS_VERBOSITY_LEVEL = getLevelName(
    os.getenv("MOVAI_FLEET_LOGS_VERBOSITY_LEVEL", "DEBUG").upper()
)  # Verbosity level for influxdb logs
MOVAI_LOG_FILE = os.getenv("MOVAI_LOG_FILE", "/opt/mov.ai/app/movai.log")
# default as NOTSET that will turn off the output for the addition log file
MOVAI_LOGFILE_VERBOSITY_LEVEL = getLevelName(
    os.getenv("MOVAI_LOGFILE_VERBOSITY_LEVEL", "NOTSET").upper()
)  # Verbosity level for spawner logs in file
MOVAI_GENERAL_VERBOSITY_LEVEL = getLevelName(
    os.getenv("MOVAI_GENERAL_VERBOSITY_LEVEL", "INFO").upper()
)  # Verbosity level for spawner logs
MOVAI_CALLBACK_VERBOSITY_LEVEL = getLevelName(
    os.getenv("MOVAI_CALLBACK_VERBOSITY_LEVEL", "DEBUG").upper()
)  # Verbosity level for callback logs
LOG_HTTP_HOST = os.environ.get("LOG_HTTP_HOST", "http://health-node:8081")
MOVAI_IPC_PATH = os.getenv("MOVAI_IPC_PATH", "/opt/mov.ai/comm")
DETACHED_PROCESS_OUTPUT = os.getenv("DETACHED_PROCESS_OUTPUT")

# Read variables from current environment
APP_PATH = os.getenv("APP_PATH")
APP_LOGS = os.getenv("APP_LOGS")
SYSLOG_ENABLED = os.getenv("SYSLOG_ENABLED", "False").lower() in ("true", "1", "t")
LD_LIBRARY_PATH = os.getenv("LD_LIBRARY_PATH")
MOVAI_HOME = os.getenv("MOVAI_HOME")
PATH = os.getenv("PATH")
PKG_CONFIG_PATH = os.getenv("PKG_CONFIG_PATH")
PRODUCTION = os.getenv("PRODUCTION")
PYTHONPATH = os.getenv("PYTHONPATH")
PYTHON_EXTERNAL_LIBS = os.getenv("PYTHON_EXTERNAL_LIBS")
REDIS_LOCAL_HOST = os.getenv("REDIS_LOCAL_HOST", "redis-local")
REDIS_LOCAL_PORT = os.getenv("REDIS_LOCAL_PORT", "6379")
REDIS_MASTER_HOST = os.getenv("REDIS_MASTER_HOST", "redis-master")
REDIS_MASTER_PORT = os.getenv("REDIS_MASTER_PORT", "6379")
REDIS_SLAVE_HOST = os.getenv("REDIS_SLAVE_HOST", "redis-slave")
REDIS_SLAVE_PORT = os.getenv("REDIS_SLAVE_PORT", REDIS_MASTER_PORT)
ROSLISP_PACKAGE_DIRECTORIES = os.getenv("ROSLISP_PACKAGE_DIRECTORIES")
ROS_DISTRO = os.getenv("ROS_DISTRO")
ROS_ETC_DIR = os.getenv("ROS_ETC_DIR")
ROS_MASTER_URI = os.getenv("ROS_MASTER_URI")
ROS_PACKAGE_PATH = os.getenv("ROS_PACKAGE_PATH")
ROS_PYTHON_VERSION = os.getenv("ROS_PYTHON_VERSION")
ROS_ROOT = os.getenv("ROS_ROOT")
ROS_VERSION = os.getenv("ROS_VERSION")
ROS1_MOVAI_WS = os.getenv("ROS1_MOVAI_WS")
ROS1_USER_WS = os.getenv("ROS1_USER_WS")
ROS1_WS = ROS1_MOVAI_WS
ROS2_DISTRO = "dashing"

# message-server environment variables
MESSAGE_SERVER_BIND_IP = os.getenv("MESSAGE_SERVER_BIND_IP", "0.0.0.0")
MESSAGE_SERVER_PORT = os.getenv("MESSAGE_SERVER_PORT", "9000")
MESSAGE_SERVER_LOG_PUBLISHER_PORT = os.getenv("MESSAGE_SERVER_LOG_PUBLISHER_PORT", "9001")
MESSAGE_SERVER_BIND_ADDR = f"tcp://{MESSAGE_SERVER_BIND_IP}:{MESSAGE_SERVER_PORT}"
LOCAL_MESSAGE_SERVER = f"tcp://{MESSAGE_SERVER_HOST}:{MESSAGE_SERVER_PORT}"
MASTER_MESSAGE_SERVER_HOST = os.getenv("MANAGER_MESSAGE_SERVER_ADDR", "haproxy")
MASTER_MESSAGE_SERVER_PORT = os.getenv("MANAGER_MESSAGE_SERVER_PORT", "9009")
MASTER_MESSAGE_SERVER = f"tcp://{MASTER_MESSAGE_SERVER_HOST}:{MASTER_MESSAGE_SERVER_PORT}"
MOVAI_ZMQ_RECV_TIMEOUT_MS = int(os.getenv("MOVAI_ZMQ_RECV_TIMEOUT_MS", "2500"))
MOVAI_ZMQ_SEND_TIMEOUT_MS = int(os.getenv("MOVAI_ZMQ_SEND_TIMEOUT_MS", "1000"))
MESSAGE_SERVER_DEBUG_MODE = os.getenv("MESSAGE_SERVER_DEBUG_MODE", "False").lower() in (
    "true",
    "1",
    "t",
)
MESSAGE_SERVER_PERIODIC_WRITE = float(os.getenv("MESSAGE_SERVER_PERIODIC_WRITE", "1.0"))
MESSAGE_SERVER_STRESS_MODE = os.getenv("MESSAGE_SERVER_STRESS_MODE", "False").lower() in (
    "true",
    "1",
    "t",
)

# DBWriter environment variables
DBWRITER_EMPTY_THREASHOULD = int(os.getenv("DBWRITER_EMPTY_THREASHOULD", "1000"))
DBWRITER_IPC_PATH = os.getenv("DBWRITER_IPC_PATH", APP_PATH)
LOGS_DBWRITER_BIND_ADDR = f"ipc://{DBWRITER_IPC_PATH}/{LOGS_INFLUX_DB}"
METRICS_DBWRITER_BIND_ADDR = f"ipc://{DBWRITER_IPC_PATH}/{METRICS_INFLUX_DB}"
STRESS_DBWRITER_BIND_ADDR = f"ipc://{DBWRITER_IPC_PATH}/{STRESS_INFLUX_DB}"

# Custom vars
ROS1_LIB = f"/opt/ros/{ROS_DISTRO}/lib"
ROS2_LIB = f"/opt/ros/{ROS2_DISTRO}/lib"
ROS2_PATH = f"/opt/ros/{ROS2_DISTRO}/lib/python3/site-packages"
ROS1_NODELET_CMD = f"/opt/ros/{ROS_DISTRO}/lib/nodelet/nodelet"

ENVIRON_ROS1 = {}
ENVIRON_ROS2 = {}
ENVIRON_GDNODE = {}

for key, value in os.environ.items():
    ENVIRON_ROS1[key] = value
    ENVIRON_GDNODE[key] = value

# Inject environment vars
ENVIRON_GDNODE_INJECT = {
    "PATH": PATH,
    "PKG_CONFIG_PATH": f"{ROS1_MOVAI_WS}/lib/pkgconfig:{PKG_CONFIG_PATH}",
    "PYTHONPATH": f"{ROS1_MOVAI_WS}/lib/python3/dist-packages:{PYTHONPATH}",
    "REDIS_LOCAL_HOST": REDIS_LOCAL_HOST,
    "REDIS_LOCAL_PORT": REDIS_LOCAL_PORT,
    "REDIS_MASTER_HOST": REDIS_MASTER_HOST,
    "REDIS_MASTER_PORT": REDIS_MASTER_PORT,
    "ROS_ETC_DIR": ROS_ETC_DIR,
    "ROSLISP_PACKAGE_DIRECTORIES": f"{ROS1_MOVAI_WS}/share/common-lisp",
    "ROS_DISTRO": ROS_DISTRO,
    "ROS_MASTER_URI": ROS_MASTER_URI,
    "ROS_PACKAGE_PATH": f"{ROS1_MOVAI_WS}:{ROS_PACKAGE_PATH}",
    "ROS_PYTHON_VERSION": ROS_PYTHON_VERSION,
    "ROS_ROOT": ROS_ROOT,
    "ROS_VERSION": ROS_VERSION,
    "LD_LIBRARY_PATH": f"{ROS1_MOVAI_WS}/lib:{LD_LIBRARY_PATH}",
    "ROS1_MOVAI_WS": ROS1_MOVAI_WS,
    "ROS1_USER_WS": ROS1_USER_WS,
}

for key, value in ENVIRON_GDNODE_INJECT.items():
    ENVIRON_GDNODE[key] = value

REST_SCOPES = (
    "(Callback|Form|Flow|Node|GraphicScene|Package|StateMachine|Layout|Annotation|Application|"
    "Configuration|SharedDataTemplate|SharedDataEntry|TaskTemplate|TaskEntry)"
)
SCOPES_TO_TRACK = [
    "Node",
    "Callback",
    "Flow",
    "StateMachine",
    "Configuration",
    "Annotation",
    "Layout",
    "GraphicScene",
]

# LDAP vars
LDAP_SEARCH_TIME_LIMIT = int(os.getenv("LDAP_SEARCH_TIME_LIMIT", "10"))
LDAP_POOLING_LOOP_TIMEOUT = int(os.getenv("LDAP_POOLING_LOOP_TIMEOUT", "5"))
LDAP_CONNECTION_RECEIVE_TIMEOUT = int(os.getenv("LDAP_CONNECTION_RECEIVE_TIMEOUT", "5"))
LDAP_KEY_LENGTH = int(os.getenv("LDAP_KEY_LENGTH", "32"))

# Token Vars
DEFAULT_JWT_ACCESS_DELTA_SECS = int(os.getenv("DEFAULT_JWT_ACCESS_DELTA_SECS", "3600"))
DEFAULT_JWT_REFRESH_DELTA_DAYS = int(os.getenv("DEFAULT_JWT_REFRESH_DELTA_DAYS", "7"))

# General Vars
DEFAULT_ROLE_NAME = os.getenv("DEFAULT_ROLE_NAME", ADMIN_ROLE)
FLEET_NAME = os.getenv("FLEET_NAME", "movai")
DEVICE_NAME = os.getenv("DEVICE_NAME", "UNDEFINED_ROBOT_NAME")
SERVICE_NAME = os.getenv("HOSTNAME", socket.gethostname())

# spawner environment variables
SPAWNER_BIND_ADDR = os.getenv(
    "SPAWNER_BIND_ADDR", f"ipc://{MOVAI_IPC_PATH}/SpawnerServer-{DEVICE_NAME}-{FLEET_NAME}.sock"
)
SPAWNER_DEBUG_MODE = os.getenv("SPAWNER_DEBUG_MODE", "False").lower() in (
    "true",
    "1",
    "t",
)

# Docker configuration
DOCKERD_ATTEMPTS = int(os.getenv("DOCKERD_ATTEMPTS", "3"))
DOCKER_TIMEOUT = int(os.getenv("DOCKER_TIMEOUT", "30"))
DOCKER_REGISTRY = os.getenv("DOCKER_REGISTRY", "registry.cloud.mov.ai")

# SMTP Vars
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "do-not-reply@mov.ai")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY", "")
