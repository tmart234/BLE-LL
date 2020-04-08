# BLE-LL

# Notice
As of now, this repo is extremely incomplete. Please use for inspiration only. Accepting PRs!

# Objective
To build a custom python BLE Link Layer, a gnuradio link connection manager for hard timings, and an HCI parser. Ideally will use scapy-radio (https://github.com/BastilleResearch/scapy-radio BLE PHY packets w/ Scapy over SDR) for the tx/rx. Once developed, we will merge BLESuite (https://github.com/nccgroup/BLESuite hackable python Scapy BLE stack, w/ all host layers) and pass thier HCI commands to our parser, which will take care of the rest.

TL;DR:
Send/receive valid/malformed Bluetooth LE packets on any host/controller layer using an ACL (async) data connection.

# Requirements
- BLESuite
- scapy-radio
- scapy (use the sweyntooth PR branch for now which has changes to bluetooth4LE.py, the BLE PHY/LL module)
- gnuradio

# Hardware
- HackRF
