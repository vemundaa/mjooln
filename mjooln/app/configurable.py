import logging

from mjooln.core.dic_doc import Doc
from mjooln.core.segment import Segment



class Configurable(Doc):

    _logger = logging.getLogger(__name__)

    @classmethod
    def default(cls):
        return cls().dic()

    @classmethod
    def from_file(cls, file, crypt_key=None, password=None):
        dic = file.read(crypt_key=crypt_key, password=password)
        return cls(**dic)

    def __init__(self, key='nnn', identity=None, zulu=None, **kwargs):
        self._segment = Segment(key=key, identity=identity, zulu=zulu)
        self.add(kwargs)

    def segment(self):
        return self._segment

    def _debug(self, message):
        self._logger.debug(f'[{self._segment.identity}] {message}')

    def _info(self, message):
        self._logger.info(f'[{self._segment.identity}] {message}')

    def _warning(self, message):
        self._logger.warning(f'[{self._segment.identity}] {message}')

    def _error(self, message):
        self._logger.error(f'[{self._segment.identity}] {message}')

