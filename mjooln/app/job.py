import logging
import time

from mjooln.app.configurable import Configurable
from mjooln.app.timer import Timer

logger = logging.getLogger(__name__)


class JobError(Exception):
    pass


class Job(Configurable):
    # TODO: Refactor to separate actual job from finding all jobs.
    # TODO: Alternatively, move finding jobs to app.

    id = ''
    name = ''
    description = ''

    # Tic toc applied in execute method. Set to False to custom implement in child class
    _tic_toc_auto = True

    @classmethod
    def default(cls):
        dic = super().default()
        dic['timer_config'] = Timer.default()
        return dic

    def __init__(self, key='nnn', identity=None, zulu=None,
                 timer=Timer.default(),
                 **kwargs):
        if not self.id or not self.name:
            raise JobError('id and name must be overridden in child class.')
        super().__init__(key=key, identity=identity, zulu=zulu)
        self._timer = Timer(**timer)
        self._logger = logging.getLogger(self.id)

    def _execute(self):
        raise JobError('Method \'_execute\' must be implemented in child class')

    def execute(self):
        if self._tic_toc_auto:
            self._timer.tic()
        self._execute()
        if self._tic_toc_auto:
            self._timer.toc()


class SampleJob(Job):

    id = 'sample_job'
    name = 'Sample Job'

    def __init__(self, key='nnn', identity=None, zulu=None,
                 timer=Timer.default(),
                 waiter=4):
        super().__init__(key=key, identity=identity, zulu=zulu,
                         timer=timer)
        self.waiter = waiter

    def _execute(self):
        time.sleep(self.waiter)
        print('Have slept a bit.')

if __name__ == '__main__':
    print(SampleJob.default())
    job = SampleJob()
    job.dev_print()
    for i in range(5):
        job.execute()
        print(job._timer.stats_text())
