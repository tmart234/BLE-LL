from scapy.layers.bluetooth4LE import *
from scapy.layers.bluetooth import *

from blesuite.pybt.stack import *
from blesuite.pybt.stack import *

import sys
import os
from enum import Enum

from threading import Timer

import util
import diver

# rewrite BLESuite stack.py to not use sockets but rather a "fake socket" class to send pkts/commands?
# write an "HCI parser" that returns event codes.... oh boy this sounds fun


class LinkLayer:
    # LL states
    class StateMachine(Enum):
        standby = 0
        advertising = 1
        scanning = 2
        initiating = 3
        connected = 4
        synced = 5
        iso_broadcasting = 6

    def __init__(self):
        self.mac_address = '80:ea:ca:80:00:01'
        # Internal vars
        self.state = StateMachine['standby']

        self.driver = Driver()
        self._pkt = None
        self.channel = None
        self.response = None
        self.scan_timer = None
        # advertising channel
        self.pdu_ac_payload_size_max = 37
        self.pdu_ll_hdr_size = 2
        self.pdu_ac_size_max = self.pdu_ac_payload_size_max + self.pdu_ll_hdr_size
        self.pdu_ac_access_addr = 0x8e89bed6
        # data channel
        self.pdu_dc_payload_size_min = 27
        self.pdu_dc_payload_time_min = 328
        self.pdu_ac_size_min = self.pdu_dc_payload_size_min + self.pdu_ll_hdr_size
        self.conn_access_addr = 0xe213bc42
        # size and time vars for DLE
        self.max_tx_bytes = 251
        self.max_rx_bytes = 251
        self.max_tx_time = 2120
        self.max_rx_time = 2120

    # for sending raw ll packets
    # useage: send_raw_ll(BTLE() / BTLE_ADV() / BTLE_SCAN_REQ() / data)
    def send_raw_ll(self, body):
        self.raw_ll(body)
        return self.response

    @staticmethod
    def raw_ll(body):
        if block:
            while True:
                time.sleep(0.1)
        driver.raw_ll(body)

        # process ll packet

    def process_ll(self, data):
        if data is None:
            return
        else:
            self.response = BTLE(data)
            if self.response is None:
                print('recieved packet is NONE')
                return
            elif BTLE_DATA in self.response:
                if self.state.name is 'initiating':
                    self.state.name = 'connected'
                    print('Connected (L2Cap channel established)')
                    # Send version indication request
                    self._pkt = BTLE(access_addr=access_address) / BTLE_DATA() / CtrlPDU() / LL_VERSION_IND(
                        version='5.0')
                    driver.send(pkt)
                    return
                elif self.state.name is 'connected':
                    print('Recv data pkt {}'.format(self.response))
                    if L2CAP_Hdr() in self.response:
                        BTLE_DATA(self.response)
                        core.process_l2cap(body)  # have blesuite core process
                        # pass to HCI layer?
                        return
                    elif CtrlPDU in self.response:
                        if LL_LENGTH_REQ in response:
                            set_dle()   # TODO: compare dle here
                            send_ll_len_response() # TODO
            elif BTLE_ADV in self.response:
                if self.state.name is 'scanning':
                    if BTLE_ADV_IND in self.response:
                        # adv_ind recvd
                        # deal with adv here, get dev_local/complete_name?
                        return
                elif self.state.name is 'initiating':
                    # scan response recvd
                    if BTLE_SCAN_RSP in self.response and self.response.AdvA == mac_address.lower():
                        #  Send connection request back to advertiser
                        conn_request = BTLE_ADV(RxAdd=self.response.TxAdd, TxAdd=0) / BTLE_CONNECT_REQ(
                            InitA=self.master_address,
                            AdvA=self.mac_address,  # TODO: check values!! from sweyntooth repo
                            AA=self.pdu_ac_access_addr,
                            crc_init=0x179a9c,  # CRC init (any)
                            win_size=2,  # 2.5 of windows size (anchor connection window size)
                            win_offset=1,  # 1.25ms windows offset (anchor connection point)
                            interval=16,  # 20ms connection interval
                            latency=0,  # Slave latency (any)
                            timeout=50,  # Supervision timeout, 500ms (any)
                            chM=0x1FFFFFFFFF,  # Any
                            hop=5,  # Hop increment (any)
                            SCA=0,  # Clock tolerance
                        )
                        self.driver.raw_ll(conn_request)

    # look up rf center freq for channel
    def rf_lookup_feq(self):
        if self.chan <= 10:
            return 4 + 2 * self.chan
        elif self.chan <= 36:
            return 6 + 2 * self.chan
        elif self.chan == 37:
            return 2
        elif self.chan == 38:
            return 26
        else:
            return 80

        # def scan_timeout(self, timeout):
        #     if self.state.name is not 'connected':
        #         send_scan_req()
        #         if self.state.name is not 'initiating':
        #             self.state.name = 'initiating'
        #             start_timeout('scan_timeout', timeout, scan_timeout)
        #             if self.switch_length_pkt:
        #                 self.switch_length_pkt = 0
        #             else:
        #                 self.switch_length_pkt = 1

    # Flow chart in BLE core spec Version 5.2 | Vol 6, Part D page 3120
    def ll_scan_timeout(self):
        if self.state.name is 'standby':
            self.ll_set_scan_prams(le_scan_interval=0x0010, le_scan_window=0x0010)
            # TODO: add command complete to upper HCI levels
            self.ll_set_scan_enable(True, None)
            # set scan timer
            if self.ll_scan_window_ms < self.ll_scan_interval_ms:
                scan_timer = LLTimer(name='scan_timer', seconds=self.ll_scan_interval_ms / 1000)
                self.scan_timer = scan_timer.timer
            # set adv channel
            self.channel = (os.random() % 3) + 37
            while self.scan_timer:
                # Check if packet from advertised is received
                if self._pkt and BTLE_ADV in pkt and pkt.AdvA == advertiser_address.lower() and \
                        self.state.name is not 'connected':
                    self.scan_timer.disable_timeout('scan_timer')
                    self.slave_addr_type = pkt.TxAdd
                    # search for dev_local_name here?
                    print(advertiser_address.upper() + ': ' + pkt.summary()[7:] + ' Detected')
        # pass HCI scan timeout event?

    def len_req(self):
        pkt = BTLE() / CtrlPDU() / LL_LENGTH_REQ(max_tx_bytes = self.max_tx_bytes,
                                                 max_rx_bytes = self.max_rx_bytes,
                                                 max_rx_time = self.max_rx_time,
                                                max_tx_time = self.max_tx_time)
        self.driver.send(pkt)
        # compare fields and choose lowest values

    # only one advertising channel is being looked at during each scanInterval
    # le_scan_interval = le_scan_window is continuous scanning
    # Apple apparently uses a 30 ms scanWindow with 40 ms scanInterval in iOS with apps in foreground mode
    def ll_set_scan_prams(self, le_scan_type= 0x00, le_scan_interval=64, le_scan_window=48, own_address_type=0x01, scanning_filter_policy=0x00):
        self.ll_scan_interval_ms = le_scan_interval * 0.625
        self.ll_scan_window_ms = le_scan_window * 0.625
        self.address_type = own_address_type # random address
        self.scan_type = le_scan_type # passive scan
        self.scan_filter_policy = scanning_filter_policy # grab everything advertising
        print('LE scan  prams: scan type {}, address type {}, '.format(self.ll_scan_interval_ms,
                                                                    self.ll_scan_window_ms))
        print('LE scan timing prams: window {}ms, interval {}'.format(self.ll_scan_interval_ms,
                                                                    self.ll_scan_window_ms))

    def ll_set_scan_enable(self, le_scan_enable, filter_duplicates):
        if le_scan_enable:
            return self.ll_start_scanning(filter_duplicates)
        else:
            self.ll_stop_scanning()

    def ll_start_scanning(self, filter_duplicates):
        if self.state.name is not 'standby':
            print('LL needs to be in standby')
            return
        print('Starting scan')
        self.state = StateMachine['scanning']
        # set events?
        print('LE Scan Channel: {}'.format(self.channel))
        # recv() here

    def ll_stop_scanning(self):
        if self.state.name is not 'scanning':
            print('LL needs to be in scanning state')
            return
        print('LE Scan Stop')
        self.state.name = 'standby'
        # stop recv()

    def send_scan_req(self):
        # Send scan request
        _pkt = BTLE() / BTLE_ADV(RxAdd=self.slave_addr_type) / BTLE_SCAN_REQ(
            ScanA=self.master_address,
            AdvA=self.mac_address)
        driver.send(self._pkt)

    #  Apple recommended peripheral advertising intervals are 152.5, 211.25, 318.75,
    #  417.5, 546.25, 760, 852.5, 1022.5, 1285 ms
    def ll_set_adv_prams(self):
        pass


if __name__ == '__main__':
    ll = LinkLayer()
    # set mac to system's BLE mac
    ll.mac_address = ll.get_sys_mac()
    print(ll.address.lower())
    exit(0)
