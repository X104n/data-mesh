from filelock import FileLock

log_lock = FileLock("src/platform_code/log.lock")