import logging
import os

# Define the debug and the basic log files

#   - Define the format of the messages
Log_Format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

#   - Delete old logs
if os.path.exists(".log_info"):
  os.remove(".log_info")

if os.path.exists(".log_deb"):
  os.remove(".log_deb")

#   - Creates the handler for the info log
fileinfo = logging.FileHandler('.log_info')
fileinfo.setFormatter(Log_Format)
log1 = logging.getLogger('Info')
log1.addHandler(fileinfo)
log1.setLevel(logging.INFO)

#   - Creates the handler for the debug log
filedeb = logging.FileHandler('.log_deb')
filedeb.setFormatter(Log_Format)
log2 = logging.getLogger('Debug')
log2.addHandler(filedeb)
log2.setLevel(logging.DEBUG)

# Define basic methods 
def loginfo(mess):
    log1.info(' '+mess)
    log2.info(' '+mess)

def logdeb(mess):
    log2.debug(mess)

def logerror(mess):
    log1.error(mess)
    log2.error(mess)
    print('!!! ERROR: Please check log files')
