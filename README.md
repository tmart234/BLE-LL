# BLE-LL

# Project Notice
As of now, this repo is extremely incomplete. Please use for inspiration only. Accepting PRs!

# Objective
To merge a repo like BLESuite (https://github.com/nccgroup/BLESuite hackable python BLE stack) with scapy-radio (https://github.com/BastilleResearch/scapy-radio BLE PHY packets over SDR) so we can send or receive valid or malformed Bluetooth LE packets on any layer.

# Requirements
- BLESuite
- scapy-radio
- scapy (use the sweyntooth PR branch for now which has changes to bluetooth4LE.py, the BLE PHY/LL module)
- gnuradio

# Hardware
- HackRF
