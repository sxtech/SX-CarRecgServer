#-*- encoding: gb2312 -*-
import ConfigParser

class CarRecgSerIni:
    def __init__(self,confpath = 'recg.conf'):
        self.path = ''
        self.confpath = confpath
        self.cf = ConfigParser.ConfigParser()
        self.cf.read(confpath)

    def getSysConf(self):
        sysconf = {}
        sysconf['threads'] = self.cf.getint('SYSSET','threads')
        sysconf['port'] = self.cf.getint('SYSSET','port')
        return sysconf

     
if __name__ == "__main__":

    try:
        ftpini = CarRecgSerIni()
        s= ftpini.getSysConf()
        print s

        #del i
    except ConfigParser.NoOptionError,e:
        print e
        time.sleep(10)
