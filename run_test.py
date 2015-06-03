from car_recg import app, Users
from car_recg import debug_logging, online_logging, RecgServer, MyIni

if __name__ == '__main__':
    Users.create_table(True)
    debug_logging('log\carrecgser.log')
    rs = RecgServer()
    rs.main()
    ini = MyIni()
    sysini = ini.get_sys_conf()
    app.config['THREADS'] = sysini['threads']
    app.config['MAXSIZE'] = sysini['threads'] * 16
    app.run(host='0.0.0.0', port=sysini['port'], threaded=True)
    del rs
    del ini
