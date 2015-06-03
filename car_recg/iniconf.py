# -*- encoding: utf-8 -*-
import ConfigParser


class MyIni:

    def __init__(self, confpath='recg.conf'):
        self.cf = ConfigParser.ConfigParser()
        self.cf.read(confpath)

    def __del__(self):
        del self.cf

    def get_sys_conf(self):
        """获取系统配置参数"""
        conf = {}
        conf['threads'] = self.cf.getint('SYSSET', 'threads')
        conf['port'] = self.cf.getint('SYSSET', 'port')
        conf['selfip'] = self.cf.get('SYSSET', 'selfip')

        return conf

    def get_ser_centre_conf(self):
        """获取中心服务参数"""
        conf = {}
        conf['ip'] = self.cf.get('SERCENTRE', 'ip')

        return conf
