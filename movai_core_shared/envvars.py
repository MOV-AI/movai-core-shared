""" Compilation of necessary environment variables to push to the database """
import os
from datetime import timedelta
from logging import DEBUG, NOTSET, INFO

# Setting for logging verbosity levels
# Will be set only once at startup
MOVAI_STDOUT_VERBOSITY_LEVEL = int(
    os.getenv("MOVAI_STDOUT_VERBOSITY_LEVEL", str(DEBUG))
)
MOVAI_FLEET_LOGS_VERBOSITY_LEVEL = int(
    os.getenv("MOVAI_FLEET_LOGS_VERBOSITY_LEVEL", str(INFO))
)
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
LD_LIBRARY_PATH = os.getenv("LD_LIBRARY_PATH")
MOVAI_HOME = os.getenv("MOVAI_HOME")
PATH = os.getenv("PATH")
PKG_CONFIG_PATH = os.getenv("PKG_CONFIG_PATH")
PRODUCTION = os.getenv("PRODUCTION")
PYTHONPATH = os.getenv("PYTHONPATH")
PYTHON_EXTERNAL_LIBS = os.getenv("PYTHON_EXTERNAL_LIBS")
REDIS_LOCAL_HOST = os.getenv("REDIS_LOCAL_HOST")
REDIS_LOCAL_PORT = os.getenv("REDIS_LOCAL_PORT")
REDIS_MASTER_HOST = os.getenv("REDIS_MASTER_HOST")
REDIS_MASTER_PORT = os.getenv("REDIS_MASTER_PORT")
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
# ZMQ environment variables
MSG_HANDLER_LOCAL_CONN = os.getenv("MSG_HANDLER_LOCAL_CONN", "ipc:///run/movai/comm/msg_handler_local_comm.ipc")
MOVAI_ZMQ_TIMEOUT_MS = os.getenv("MOVAI_ZMQ_TIMEOUT_MS", 1000)



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
    "(Callback|Form|Flow|Node|GraphicScene|Package|StateMachine|Layout|User|Annotation|Application|"
    "Configuration|SharedDataTemplate|SharedDataEntry|TaskTemplate|TaskEntry|Role)"
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
    "User",
    "Role",
]

# JWT Authentication
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_EXPIRATION_DELTA = timedelta(seconds=3600)
JWT_REFRESH_EXPIRATION_DELTA = timedelta(days=7)
