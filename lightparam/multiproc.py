from multiprocessing import Queue
from lightparam import Parametrized


class MultiprocParametrized(Parametrized):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = Queue()

    def enqueue(self):
        self.queue.put(self.params.values)

    def retrieve(self):
        new_params = self.queue.get(timeot=0.0001)
        for key, val in new_params:
            setattr(self, key, val)


