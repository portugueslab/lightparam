import unittest

from multiprocessing import Process, Event
from lightparam import Param
from lightparam.multiproc import MultiprocParametrized
from time import sleep


class Ttestc:
    def __init__(self):
        self.x = 5
        print("In the c init", self.x)


class Mulipr(MultiprocParametrized, Process):
    def __init__(self):
        super().__init__()
        self.x = Param(1.0)
        self.stop = Event()
        print(self.x)

    def run(self):
        while not self.stop.is_set():
            self.retrieve()
            print(self.x)
            sleep(0.1)


class TestMultiprocParams(unittest.TestCase):
    def testMultiProcParam(self):
        p = Mulipr()
        p.start()
        for i in range(10):
            p.x = i
            p.enqueue()
            sleep(0.1)
        p.join()