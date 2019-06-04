#!/usr/bin/env python
# -*- coding:utf-8 -*-

import socket
import threading
import binascii
from datetime import datetime
import time


FORMAT_MESSAGE = "{channel}  {id:<15} Rx   {dtype} {data}"
FORMAT_DATE = "%a %b %m %I:%M:%S %p %Y"
FORMAT_EVENT = "{timestamp: 9.4f} {message}\n"

def recorder_udp_server():
    ip_port = ('192.168.0.221', 6666)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    s.bind(ip_port)

    # the last part is written with the timestamp of the first message
    timestamp = None
    header_written = False
    last_timestamp = None
    started = None

    while True:
        data = s.recv(1024).strip().decode()
        # print(data)
        server_reply2 = binascii.hexlify("".join(data).encode()).decode()  #
        # print("server_reply2: %s" % server_reply2)

        server_reply3 = bytearray.fromhex(server_reply2)
        server_reply4 = list(server_reply3)
        # print("server_reply4: %s" % server_reply4)#server_reply4: [0, 48, 49, 50, 51, 52, 53, 54]

        with open(r'F:\yhh\0-Source\work\work_data_collect_record\TBOX\data\test.txt', 'a') as f:
            # this is the case for the very first message:
            if not header_written:
                # write start of file header
                now = datetime.now().strftime("%a %b %m %I:%M:%S %p %Y")
                f.write("date %s\n" % now)
                f.write("base hex  timestamps absolute\n")
                f.write("internal events logged\n")

                last_timestamp = (timestamp or 0.0)
                started = last_timestamp
                formatted_date = time.strftime(FORMAT_DATE, time.localtime(last_timestamp))
                f.write("Begin Triggerblock %s\n" % formatted_date)
                header_written = True
                f.write("0.0000 Start of measurement\n")  # caution: this is a recursive call!

            # figure out the correct timestamp
            if timestamp is None:
                timestamp = last_timestamp
                timestamp = time.time()
                started = timestamp
            else:
                timestamp = time.time()
                timestamp -= started
                f.write("%0.4f" % timestamp)
                f.write(' ')
                f.write('can0:')
                f.write(' ')
                # can id
                f.write(' ')
                f.write('Rx')
                f.write(' ')
                f.write('d')
                f.write(' ')
                f.write('8')
                f.write(' ')
                for i in range(len(server_reply4)):
                    f.write(str(hex(server_reply4[i]))[2:])
                    f.write(' ')
                f.write('\n')

            # turn into relative timestamps if necessary
            if timestamp >= started:
                started = timestamp

    s.close() # 关闭连接


def config_client():
    ip_port = ('192.168.0.200', 8)
    # ip_port = ('127.0.0.1', 6666)
    s = socket.socket()  # 创建套接字
    s.connect(ip_port)  # 连接服务器

    while True:  # 通过一个死循环不断接收用户输入，并发送给服务器
        inp = input("请输入要发送的信息： ").strip()
        if not inp:  # 防止输入空信息，导致异常退出
            continue
        s.sendall(inp.encode())

        if inp == "exit":  # 如果输入的是‘exit’，表示断开连接
            print("结束通信！")
            break

        server_reply = s.recv(1024).decode()
        print("server_reply: %s" % server_reply)
    s.close()  # 关闭连接

if __name__ == '__main__':
    t_server = threading.Thread(target=recorder_udp_server, name='Record-Thread', args=())
    t_client = threading.Thread(target=config_client, name='Config-Thread', args=())

    t_server.start()
    t_client.start()