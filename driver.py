# HackRF driver, would need 2 HackRFs to implement

# from scapyradio import *

class Driver():
    def __init__(self):
        self.sock = None
        self.r = None
        pass

    def raw_ll(self, data):
        self.send(BTLE() / data)

    def send(self, pkt):
        self.r = None
        scapyradio.send(pkt)
        while True:
            self.r = self.recv(len(pkt))
            if self.r is not None:
                return self.r

    def recv(self, len):
        return BTLE(self.scapyradio.recv(len))