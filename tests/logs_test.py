from movai_core_shared.logger import Log

logs_query = Log.get_logs(limit=100, level="info", robots="dev-manager")

print(logs_query)