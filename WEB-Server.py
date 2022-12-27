import socket
import datetime

def set_settings():
    global dct
    file1 = open("settings.txt", "r")
    dct = {}
    while True:
        line = file1.readline()
        if not line:
            break
        el = line.strip().split(' = ')
        dct.update({el[0]: el[1]})

    file1.close()

def start_server():
    set_settings()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('localhost', int(dct['port'])))
            print("Using port 80")
        except OSError:
            sock.bind(('localhost', 80))
            print("Using port 80")
        except OSError:
            sock.bind(('localhost', 8080))
            print("Using port 8080")

        sock.listen(5)
        while True:
            try:
                conn, addr = sock.accept()
                print("Connected", addr)
                data = conn.recv(int(dct['reqsize'])).decode('utf-8')
                resp = load_page(data)
                conn.send(resp)
                log = f'{datetime.datetime.now()} {addr} {data.split()[1]} {log_code}'
                with open('log.txt', 'a') as file:
                    file.write(log + '\n')
                conn.shutdown(socket.SHUT_WR)
            except TypeError:
                pass
    except KeyboardInterrupt:
        print('Прерывание сервера')
        conn.close()


def load_page(request_data):
    global log_code
    try:
        HDRS = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n'
        HDRS_404 = 'HTTP/1.1 404 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n'
        HDRS_403 = 'HTTP/1.1 403 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n'
        path = request_data.split(' ')[1]
        response = ''
        if path.split('.')[1] in ['html', 'css', 'js', 'png', 'ico']:
            try:
                with open(dct['dir']+path, 'rb') as file:
                    response = file.read()
                log_code = '200'
                return HDRS.encode('utf-8') + response
            except (FileNotFoundError, PermissionError):
                log_code = '404'
                return (HDRS_404 + '404 PAGE NOT FOUND').encode('utf-8')
        else:
            log_code = '403'
            return (HDRS_403 + '403 FORBIDDEN').encode('utf-8')
    except IndexError:
        pass

if __name__ == '__main__':
    start_server()