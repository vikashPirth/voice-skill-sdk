import logging
import os
import threading
from pathlib import Path

logger = logging.getLogger(__name__)


class ThreadReload:
    def __init__(self, config, target, sockets):
        self.config = config
        self.target = target
        self.sockets = sockets
        self.reloader_name = "threadreload"
        self.thread = threading.Thread(
            target=self.target, kwargs=dict(sockets=self.sockets)
        )
        self.should_exit = threading.Event()
        self.mtimes = {}

    def signal_handler(self, sig, frame):
        """
        A signal handler that is registered with the parent process.
        """
        self.should_exit.set()

    def run(self):
        self.startup()
        while not self.should_exit.wait(self.config.reload_delay):
            if self.should_restart():
                self.restart()

        self.shutdown()

    def startup(self):
        logger.info(
            "Started reloader thread [%s] using %s",
            threading.get_ident(),
            self.reloader_name,
        )
        self.thread.start()

    def restart(self):
        self.mtimes = {}
        self.should_exit = True
        self.thread.join()
        self.thread = threading.Thread(
            target=self.target, kwargs=dict(sockets=self.sockets)
        )
        self.thread.start()

    def shutdown(self):
        self.should_exit = True
        self.thread.join()
        logger.info("Stopping reloader thread [%s]", threading.get_ident())

    def should_restart(self):
        for filename in self.iter_py_files():
            try:
                mtime = os.path.getmtime(filename)
            except OSError:  # pragma: nocover
                continue

            old_time = self.mtimes.get(filename)
            if old_time is None:
                self.mtimes[filename] = mtime

            elif mtime > old_time:
                display_path = os.path.normpath(filename)
                if Path.cwd() in Path(filename).parents:
                    display_path = os.path.normpath(os.path.relpath(filename))
                message = "StatReload detected file change in '%s'. Reloading..."
                logger.warning(message, display_path)
                return True
        return False

    def iter_py_files(self):
        for reload_dir in self.config.reload_dirs:
            for subdir, dirs, files in os.walk(reload_dir):
                for file in files:
                    if file.endswith(".py"):
                        yield subdir + os.sep + file
