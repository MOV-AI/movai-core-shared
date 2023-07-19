""" Compilation of necessary environment variables to push to the database """
import os
from logging import DEBUG, NOTSET, INFO
import socket
from .consts import MESSAGE_SERVER_HOST, ADMIN_ROLE

# Setting for logging verbosity levels
# Will be set only once at startup
MOVAI_STDOUT_VERBOSITY_LEVEL = int(
    os.getenv("MOVAI_STDOUT_VERBOSITY_LEVEL", str(DEBUG))
)
MOVAI_FLEET_LOGS_VERBOSITY_LEVEL = int(
    os.getenv("MOVAI_FLEET_LOGS_VERBOSITY_LEVEL", str(DEBUG))
)
MOVAI_LOG_FILE = os.getenv("MOVAI_LOG_FILE", "/opt/mov.ai/app/movai.log")
# default as NOTSET that will turn off the output for the addition log file
MOVAI_LOGFILE_VERBOSITY_LEVEL = int(
    os.getenv("MOVAI_LOGFILE_VERBOSITY_LEVEL", str(NOTSET))
)
MOVAI_GENERAL_VERBOSITY_LEVEL = int(
    os.getenv("MOVAI_GENERAL_VERBOSITY_LEVEL", str(DEBUG))
)
LOG_HTTP_HOST = os.environ.get('LOG_HTTP_HOST', 'http://health-node:8081')

# Read variables from current environment
APP_PATH = os.getenv("APP_PATH")
APP_LOGS = os.getenv("APP_LOGS")
SYSLOG_ENABLED = os.getenv("SYSLOG_ENABLED", False)
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
MESSAGE_SERVER_BIND_ADDR = f"tcp://{MESSAGE_SERVER_BIND_IP}:{MESSAGE_SERVER_PORT}"
MESSAGE_SERVER_LOCAL_ADDR = f"tcp://{MESSAGE_SERVER_HOST}:{MESSAGE_SERVER_PORT}"
MESSAGE_SERVER_REMOTE_ADDR = f"tcp://{REDIS_MASTER_HOST}:{MESSAGE_SERVER_PORT}"
MOVAI_ZMQ_TIMEOUT_MS = int(os.getenv("MOVAI_ZMQ_TIMEOUT_MS", "1000"))
LOG_STREAMER_BIND_IP = os.getenv("LOG_STREAMER_BIND_IP", "0.0.0.0")
LOG_STREAMER_BIND_ADDR = f"tcp://{LOG_STREAMER_BIND_IP}:{MESSAGE_SERVER_PORT}"
# Custom vars
ROS1_LIB = f"/opt/ros/{ROS_DISTRO}/lib"
ROS2_LIB = f"/opt/ros/{ROS2_DISTRO}/lib"
ROS2_PATH = f"/opt/ros/{ROS2_DISTRO}/lib/python3/site-packages"
ROS1_NODELET_CMD = f"/opt/ros/{ROS_DISTRO}/lib/nodelet/nodelet"

ENVIRON_ROS1 = {}
ENVIRON_ROS2 = {}
ENVIRON_GDNODE = {}

for (key, value) in os.environ.items():
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

for (key, value) in ENVIRON_GDNODE_INJECT.items():
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
    "GraphicScene"
]

#LDAP vars
LDAP_SEARCH_TIME_LIMIT = int(os.getenv('LDAP_SEARCH_TIME_LIMIT', "10"))
LDAP_POOLING_LOOP_TIMEOUT = int(os.getenv('LDAP_POOLING_LOOP_TIMEOUT', "5"))
LDAP_CONNECTION_RECEIVE_TIMEOUT = int(os.getenv('LDAP_CONNECTION_RECEIVE_TIMEOUT', "5"))
LDAP_KEY_LENGTH = int(os.getenv('LDAP_KEY_LENGTH', "32"))

#Token Vars
DEFAULT_JWT_ACCESS_DELTA_SECS = int(os.getenv('DEFAULT_JWT_ACCESS_DELTA_SECS', "3600"))
DEFAULT_JWT_REFRESH_DELTA_DAYS = int(os.getenv('DEFAULT_JWT_REFRESH_DELTA_DAYS', "7"))

#General Vars

DEFAULT_ROLE_NAME = os.getenv('DEFAULT_ROLE_NAME', ADMIN_ROLE)
FLEET_NAME = os.getenv('FLEET_NAME', "movai")
DEVICE_NAME = os.getenv('DEVICE_NAME', "UNDEFINED_ROBOT_NAME")
SERVICE_NAME = os.getenv('HOSTNAME', socket.gethostname())

#SMTP Vars
SMTP_EMAIL = os.getenv('SMTP_EMAIL', "do-not-reply@mov.ai")
SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY', "")
