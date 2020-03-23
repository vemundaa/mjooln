from mjooln.core.zulu import Zulu
from mjooln.app.configurable import Configurable
from mjooln.app.stats import Stats


class Timer(Configurable):

    def __init__(self, key='nnn', identity=None, zulu=None,
                 init_count=10,
                 log_cycle=10,
                 log_stats_cycle=1000):
        super().__init__(key=key, identity=identity, zulu=zulu)
        self.init_count = init_count
        self.log_cycle = log_cycle
        self.log_stats_cycle = log_stats_cycle
        self._stats = Stats()
        self._time_s = None
        self._zulu_t0 = None
        self._zulu_tf = None

    def _update(self):
        time_delta = self._zulu_tf - self._zulu_t0
        self._time_s = time_delta.total_seconds()
        self._stats.update(self._time_s)

    def _check(self):
        if self._stats.count > self.init_count:
            if self._time_s > self._stats.max:
                self._warning(f'Max execution time '
                              f'exceeded: {self._time_s:.2f} s')

    def tic(self):
        self._zulu_t0 = Zulu()
        if self._zulu_tf:
            self._zulu_tf = None
        elif self._stats.count > 0:
            self._warning(f'Double Tic detected. Use Tic, then Toc. '
                          f'Then Tic and then Toc. And so on.')

    def toc(self):
        self._zulu_tf = Zulu()
        self._update()
        self._check()

    def stats(self):
        return self._stats.dic()

    def stats_text(self, float_format='.3f'):
        key_items = [f'{x}: {format(y, float_format)}' for x, y in self.stats().items()]
        return ', '.join(key_items)

    def log_status(self):
        if self._time_s:
            return f'Count: {self._stats.count}; ' \
                   f'Time: {self._time_s:.3f} s; ' \
                   f'Min: {self._stats.min:.3f} s; ' \
                   f'Max: {self._stats.max:.3f} s; ' \
                   f'Average: {self._stats.average():.3f} s; ' \
                   f'Std: {self._stats.std():.3f} s;'
        else:
            return None


if __name__ == '__main__':
    t = Timer('me2')
    import time
    t.tic()
    time.sleep(1)
    t.toc()
    print(t.stats_text())

    t.tic()
    time.sleep(1)
    t.toc()
    print(t.stats_text())

    t.tic()
    time.sleep(1)
    t.toc()
    print(t.stats_text())

    t.tic()
    time.sleep(1)
    t.toc()
    print(t.stats_text())

    print('Final status:')
    print(t.stats())

