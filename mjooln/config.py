import logging
from logging.handlers import TimedRotatingFileHandler

from mjooln.file.folder import Folder
from mjooln.file.file import File

logger = logging.getLogger(__name__)

home_folder = Folder.home()


class Config:

    @classmethod
    def get(cls):
        platform = Folder.platform()
        if platform == Folder.OSX:
            return config['development']
        elif platform == Folder.LINUX:
            return config['test']
        else:
            raise ValueError(f'Platform not handled: {platform}')

    @classmethod
    def set_logger(cls, thread_name=''):
        cfg = cls.get()
        file_name = cfg.LOG_FILE_NAME
        file = File.join(cfg.LOGDIR, file_name)
        log_handler = TimedRotatingFileHandler(file, when='midnight',
                                               backupCount=cfg.LOG_FILE_BACKUP_COUNT)

        handlers = [log_handler]
        if cfg.DEVELOPMENT or cfg.TEST:
            log_level = logging.DEBUG
        else:
            log_level = logging.WARNING

        if not thread_name:
            thread_name = '__main_thread__'

        log_format = cfg.LOG_FILE_SEPARATOR.join(['%(asctime)s',
                                                  '%(name)s',
                                                  thread_name,
                                                  '%(levelname)s',
                                                  '%(message)s'])
        if cfg.DEVELOPMENT:
            logging.basicConfig(level=log_level,
                                format=log_format)
        else:
            logging.basicConfig(level=log_level,
                                format=log_format,
                                handlers=handlers)


class DevelopmentConfig:

    BASEDIR = Folder.join(home_folder, 'dev', 'data', 'mjooln')
    BASEDIR.touch()

    TESTDIR = BASEDIR.append('tests')
    TESTDIR.touch()

    LOGDIR = BASEDIR.append('log')
    LOGDIR.touch()

    SOURCEDIR = BASEDIR.append('source')
    SOURCEDIR.touch()

    DEVELOPMENT = True
    TEST = False
    LOG_FILE_BACKUP_COUNT = 10
    LOG_FILE_SEPARATOR = '\t'
    LOG_FILE_NAME = 'mjooln.log'
    MONGO_SERVER = {
        'host': 'localhost',
        'port': 27017,
        'serverSelectionTimeoutMS': 200,
    }

    DEVELOPMENT_SOURCE_LINE_LIMIT = 1000


class TestConfig(DevelopmentConfig):
    DEVELOPMENT = False
    TEST = True


class ProductionConfig(DevelopmentConfig):
    DEVELOPMENT = False
    TEST = False


config = {
    'development': DevelopmentConfig,
    'test': TestConfig,
    'production': None,
}
