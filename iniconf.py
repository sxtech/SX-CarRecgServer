# -*- encoding: utf-8 -*-
import ConfigParser


class CarRecgSerIni:

    def __init__(self, confpath='recg.conf'):
        self.path = ''
        self.confpath = confpath
        self.cf = ConfigParser.ConfigParser()
        self.cf.read(confpath)

    def get_sys_conf(self):
        """获取系统配置参数"""
        sysconf = {}
        sysconf['threads'] = self.cf.getint('SYSSET', 'threads')
        sysconf['port'] = self.cf.getint('SYSSET', 'port')
        sysconf['selfip'] = self.cf.get('SYSSET', 'selfip')

        return sysconf

    def get_ser_centre_conf(self):
        """获取中心服务参数"""
        sysconf = {}
        sysconf['ip'] = self.cf.get('SERCENTRE', 'ip')

        return sysconf

if __name__ == "__main__":

    try:
        ftpini = CarRecgSerIni()
        s = ftpini.getSerCentreConf()
        print s

    except ConfigParser.NoOptionError as e:
        print e
