import re
import uuid

# Get advertiser_address from command line (peripheral addr)
def get_sys_mac(self):
    try:
        self.address = (':'.join(re.findall('..', '%012x' % uuid.getnode())))
    except SysError as error:
        print(error)
        raise
