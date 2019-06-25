#!/usr/bin/env python
# -*- coding:utf-8 -*-

import socket
import threading
import binascii

def recorder_server():
    ip_port = ('127.0.0.1', 6666)
    s = socket.socket()  # 创建套接字
    s.connect(ip_port)  # 连接服务器

    while True:
        #ASCII码字符串
        server_reply = s.recv(1024).decode()
        # print("server_reply: %s" % server_reply)

        #ASCII码字符串转换为hex string
        server_reply2 = binascii.hexlify("".join(server_reply).encode()).decode()#
        # print("server_reply2: %s" % server_reply2)

        #hex string转换为整形列表
        server_reply3 = bytearray.fromhex(server_reply2)
        server_reply4 = list(server_reply3)
        # print("server_reply4: %s" % server_reply4)

        for i in range(len(server_reply4)):
            with open(r'F:\yhh\0-Source\work\work_data_collect_record\TBOX\data\test.txt', 'a') as f:
                if i == 0:
                    f.write('can0:')
                    f.write(' ')
                f.write(str(hex(server_reply4[i]))[2:])
                f.write(' ')
                if i == 7:
                    f.write('\n')

    s.close()  # 关闭连接
mpc5748cmd_temp = {}
def config_client():
    ip_port = ('127.0.0.1', 6666)
    s = socket.socket()  # 创建套接字
    s.connect(ip_port)  # 连接服务器

    # inp_str = ""
    # inp = "On,12345678,Add".encode()
    # inp = "On,vcan0.123:360,190:300j,vcan1.124:300,180:300,vcan2.,vcan3.111:111".encode()

    # inp_cmd = bytes(0x01)
    # inp_ch = bytes(0xFF)
    # inp_flag = bytes(0x00)
    # inp_filter_count = bytes(0x08)
    # list1 = [1, 255, 0, 8]
    Ch0 = 0
    Ch1 = 0
    Ch2 = 0
    Ch3 = 0
    cmd_list = [1]
    mpc5748cmd_temp["channel"] = ["vcan0", "vcan1","vcan2", "vcan3"]
    for i in mpc5748cmd_temp["channel"]:  # mpc5748cmd_temp["channel"] = ["vcan0", "vcan1", "vcan3"]
        if i == 'vcan0':
            Ch0 = 0x01
        if i == 'vcan1':
            Ch1 = 0x02
        if i == 'vcan2':
            Ch2 = 0x04
        if i == 'vcan3':
            Ch3 = 0x08
    Ch = Ch0 + Ch1 + Ch2 + Ch3
    cmd_list.append(Ch)
    cmd_list.append(0)
    cmd_list.append(0)
    print("cmd_list: %s" % cmd_list)
    inp = bytes(cmd_list)
    print("inp: %s" % inp)
    print("1")
    s.sendall(inp)
    print("1")

    s.close()  # 关闭连接

if __name__ == '__main__':
    t_server = threading.Thread(target=recorder_server, name='Record-Thread', args=())
    t_client = threading.Thread(target=config_client, name='Config-Thread', args=())

    # t_server.start()
    t_client.start()

# mpc5748cmd_temp = {"channel": ["vcan0", "vcan1", "vcan3"], "type": "LOG_START_REQ", "filters": ["123:360,190:300j", "124:300,180:300", "111:111"], "file format": "ASC", "content": {}}
# inp_str = ""
#
# for i,j in zip(mpc5748cmd_temp["channel"],mpc5748cmd_temp["filters"]):
#     inp_str += str(i)
#     inp_str += '.'
#     inp_str += str(j)
#     inp_str += ','
# print(inp_str)


















