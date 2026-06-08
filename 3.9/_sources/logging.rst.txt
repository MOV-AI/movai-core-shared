Logging
=======

Tools executed outside entrypoint
---------------------------------

The logs of processes / tools executed outside the entrypoint do not show in docker logs by default.
In order to improve debugging we forward them to docker logs by configuring the
`DETACHED_PROCESS_OUTPUT` environment variable and by setup a handler in the root logger with
`add_shared_handler_to_root`.
