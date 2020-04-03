from mjooln.path.path import Path
from mjooln.app.job import Job
from mjooln.app.stats import Stats
from mjooln.core.dic_doc import Dic


class Space(Job):

    id = 'space_stats'
    name = 'Space Statistics'



    @classmethod
    def location(cls):
        return Path.location()

    @classmethod
    def current(cls):
        return {
            'memory': Path.virtual_memory(),
            'disk': Path.disk_usage(),
        }

    @classmethod
    def current_flat(cls):
        current = Dic()
        current.add(cls.current())
        return current.flatten()

    def __init__(self, key='space', identity=None, zulu=None,):
        super().__init__(key=key, identity=identity, zulu=zulu)
        self.location = self.location()
        self.stats = dict()
        current = self.current_flat()
        for key in current:
            self.stats[key] = Stats()

    def _execute(self):
        current = self.current_flat()
        for key in current:
            self.stats[key].update(current[key])






if __name__ == '__main__':
    space = Space()
    import time
    space.execute()

    time.sleep(1)
    space.execute()
    for key, item in space.stats.items():
        print(key)
        item.dev_print()

    time.sleep(1)
    space.execute()
    for key, item in space.stats.items():
        print(key)
        item.dev_print()

    time.sleep(1)
    space.execute()
    for key, item in space.stats.items():
        print(key)
        item.dev_print()
