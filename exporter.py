import socket
from flask import Flask

app = Flask(__name__)
path='/var/run/clamav/clamd.ctl'
timeout=None


def clamd_socket_send(cmd: str):    
    clamd_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        clamd_socket.connect(path)
    except:
        print("No such file or directory")
    clamd_socket.settimeout(timeout)
    cmd = 'n{cmd}\n'.format(cmd=cmd).encode()
    try:
        clamd_socket.send(cmd)
        return clamd_socket.recv(1024).decode()
    except:
        print("Transport endpoint is not connected")

@app.route('/health')
def health():
    return "OK"

@app.route("/clamav")
def return_metrics():
    try:
        clamAV_status = clamd_socket_send('PING').rstrip('\n')
        clamd_version = clamd_socket_send('VERSION').rstrip('\n').replace('/',' ').split(' ')
        clamAV_version = clamd_version[1]
        database_version = clamd_version[2]
        if clamd_version[5] == '':
            database_date = '0' + clamd_version[6]+ '-' + clamd_version[4] + '-' + clamd_version[8]
        else:
            database_date = clamd_version[5] + '-' + clamd_version[4] + '-' + clamd_version[7]
    except:
        print('There was a problem with clamAV')
        clamAV_status = 0
    metrics = "# HELP clamAV_vm_details show clamAV status. \n# TYPE clamAV_vm_details gauge\n"
    if clamAV_status == 'PONG':
        status = 1
        metrics += 'clamAV_vm_details{host="%s", clamav_version="%s", database_version="%s", database_age="%s"} %s\n' % (socket.gethostname(), clamAV_version, database_version, database_date, status)
    else:
        status = 0
        metrics += 'clamAV_vm_details{host="%s", clamav_version="%s", database_version="%s", database_age="%s"} %s\n' % (socket.gethostname(), 'N/A', 'N/A', 'N/A', status)
    return metrics

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9123)
