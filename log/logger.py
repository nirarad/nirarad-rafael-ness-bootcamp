import os
from datetime import datetime
import datetime

class Log:
    os.chdir(r'C:\\eshop\\Python-eshop\\rafael-ness-bootcamp\\log')
    file = open('e_shop.txt', 'a')


    def writeLog(self, message):
        """
        Receives a message and writes to the log
        :param message:
        """
        self.file.write(f"{datetime.datetime.now()} - {message}\n\n")


