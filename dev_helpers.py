import os
from datetime import datetime

def log(this, filename='dev.log'):
    """
    writes 'this' to the log file
    """

    log_file = open(filename, 'a')
    log_file.write("%s: %s\n" % (str(datetime.now()), this))
    log_file.close()
