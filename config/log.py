
import logging.config
from pathlib import Path, PurePath

config = {
    'version': 1,
    'formatters': {
        'simple': {
            # 'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'format': '[%(asctime)s][%(levelname)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        # 其他的 formatter
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': PurePath("log/app.txt"),
            'level': 'DEBUG',
            'formatter': 'simple',
            'encoding': 'utf-8'
        },
        'access_log': {
            'class': 'logging.FileHandler',
            'filename': PurePath("log/app.txt"),
            'level': 'DEBUG',
            'formatter': 'simple',
            'encoding': 'utf-8'
        },
        # 其他的 handler
    },
    'loggers': {
        'AccessLogger': {
            'handlers': ['console', 'access_log'],
            'level': 'DEBUG',
        },
        'FileLogger': {
            # 既有 console Handler，还有 file Handler
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },

    }
}
print("logger")
logging.config.dictConfig(config)
MainLogger = logging.getLogger("FileLogger")
AccessLogger = logging.getLogger("AccessLogger")
