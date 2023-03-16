import datetime
import os
import time


class Exceptions_logs(object):

    def __init__(self, name):
        self.name = name

    def send(self, e):
        try:
            os.chdir("C:/finalProject/ServiceTest/rafael-ness-bootcamp/logs")
            self.f = open(f'log_{self.name}.txt', 'a')
            if self.f.tell() > (1000 * 1024):
                self.f = open(f'log_{self.name}.txt', 'a')
                raise ValueError(f'file is up to 1000kb {self.f.tell()}, open new file')
            else:
                date = datetime.datetime.now()
                self.f.write(f"""
name: Meni Rotblat.
date: {date.now()}. 
description: {e}.
                     """)
                self.f.flush()
                self.f.close()
        except Exception as e:
            print(e)
