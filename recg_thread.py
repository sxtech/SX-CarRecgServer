# -*- coding: cp936 -*-
import logging
import time
import os
import Queue
import threading

import gl
from carrecg import CarRecgEngine
from help_func import HelpFunc

logger = logging.getLogger('root')

class RecgThread(threading.Thread):
    def __init__(self,_id):
        threading.Thread.__init__(self)
        self._id = _id
        self.queue = gl.RECGQUE

        self.cre = CarRecgEngine()

        self.hf = HelpFunc()

    def kill(self):
        del self.cre
        del self.hf

    def run(self):
        while 1:
            try:
                p,info = self.queue.get(block=False)
            except Queue.Empty:
                time.sleep(1)
            except Exception,e:
                logger.exception(e)
                time.sleep(1)
            else:
                recginfo = {}
                try:
                    localpath = self.hf.get_img_by_url(info['imgurl'],'img','%s.jpg'%str(self._id))
                except Exception,e:
                    logger.error('Url Error')
                    recginfo = {'carinfo':None,'msg':'Url Error','code':103}
                    try:
                        info['queue'].put(recginfo)
                    except Exception,e:
                        logger.exception(e)
                    return
                
                try:
                    carinfo = self.cre.imgrecg(localpath,info['coordinates'])
                        
                    if carinfo == None:
                        recginfo = {'carinfo':None,'msg':'Recognise Error','code':102}
                        logger.error('Recognise Error')
                    else:
                        recginfo = {'carinfo':carinfo['body'],'msg':'Success','code':100} 
                    os.remove(localpath)
                except Exception,e:
                    logger.exception(e)
                    recginfo = {'carinfo':None,'msg':'Unknow Error','code':104}

                try:
                    info['queue'].put(recginfo)
                except Exception,e:
                    logger.exception(e)



                    
