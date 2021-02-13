import os
import time
import copy
import tarfile
import logging


class Logger(object):
    @staticmethod
    def get_debugger(name):
        """Return a sys.stderr debugger"""

        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s [%(name)s - %(threadName)s]%(message)s')
        return logging.getLogger(name)

    @staticmethod
    def get_logger(name):
        """Return a sys.stderr logger"""

        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(levelname)s [%(name)s - %(threadName)s]%(message)s')
        return logging.getLogger(name)

    @staticmethod
    def get_file_log_logger(name, path):
        """Return a logging file logger"""

        Logger.log_cleaner(path)
        file_tuple = os.path.splitext(path)
        fmt = logging.Formatter('%(asctime)s %(levelname)s [%(name)s - %(threadName)s]%(message)s')
        logger = copy.deepcopy(logging.getLogger(name))
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler("_log".join(file_tuple))
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(fmt)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(fmt)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        return logger

    @staticmethod
    def get_file_debug_logger(name, path):
        """Return a debug file logger"""

        Logger.log_cleaner(path)
        file_tuple = os.path.splitext(path)
        fmt = logging.Formatter('%(asctime)s %(levelname)s [%(name)s - %(threadName)s]%(message)s')
        logger = copy.deepcopy(logging.getLogger(name))
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler("_log".join(file_tuple))
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(fmt)

        debug_file_handler = logging.FileHandler("_debug".join(file_tuple))
        debug_file_handler.setLevel(logging.DEBUG)
        debug_file_handler.setFormatter(fmt)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(fmt)

        logger.addHandler(file_handler)
        logger.addHandler(debug_file_handler)
        logger.addHandler(stream_handler)
        return logger

    @staticmethod
    def log_cleaner(path):
        """Old log file cleaner"""

        file_tuple = os.path.splitext(path)
        if os.path.isfile("_log".join(file_tuple)):
            with open("_log".join(file_tuple), "w") as fp:
                fp.truncate()
        if os.path.isfile("_debug".join(file_tuple)):
            with open("_debug".join(file_tuple), "w") as fp:
                fp.truncate()

    @staticmethod
    def tar_log_file(path, logger=None, keep_file=False):
        """Packing log file using tar.gzip"""

        if not logger:
            logger = Logger.get_logger("Logger")

        if not os.path.isdir("logs"):
            os.mkdir("logs")

        tar_name = time.strftime('%Y-%m-%d-%H-%M-%S')
        file_tuple = os.path.splitext(path)
        if os.path.isfile("_log".join(file_tuple)):
            with tarfile.open(os.path.join("logs", f"{tar_name}.tar.gz"), "w:gz") as tar:
                logger.info(f"[Logger]Log file '{tar_name}' saved")
                time.sleep(0.1)  # 微小的IO延迟
                tar.add("_log".join(file_tuple), arcname=f"biliTools_log_{tar_name}.log")

                if os.path.isfile("_debug".join(file_tuple)):
                    logger.info(f"[Logger]Debug file '{tar_name}' saved")
                    time.sleep(0.1)  # 微小的IO延迟
                    tar.add("_debug".join(file_tuple), arcname=f"biliTools_debug_{tar_name}.log")
        if not keep_file:
            Logger.log_cleaner(path)
