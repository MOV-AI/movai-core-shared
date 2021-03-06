"""
   Copyright (C) Mov.ai  - All Rights Reserved
   Unauthorized copying of this file, via any medium is strictly prohibited
   Proprietary and confidential

   Developers:
   - Dor Marcous (Dor@mov.ai) - 2022
"""

# Constants
ROS1_NODELET = "ROS1/Nodelet"
ROS1_NODE = "ROS1/Node"
ROS1_PLUGIN = "ROS1/Plugin"
MOVAI_NODE = "MovAI/Node"
MOVAI_STATE = "MovAI/State"
MOVAI_SERVER = "MovAI/Server"

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
MOVAI_TRANSITIONFOR = "MovAI/TransitionFor"
MOVAI_TRANSITIONTO = "MovAI/TransitionTo"
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

TIMEOUT_PROCESS_SIGINT = 15
TIMEOUT_PROCESS_SIGTERM = 2
