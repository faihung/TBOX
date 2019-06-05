#!/usr/bin/env python
# -*- coding:utf-8 -*-

import socket
import threading
import binascii
from datetime import datetime
import time

import pika
import json


host_address = 'www.dingauto.cn'
FORMAT_MESSAGE = "{channel}  {id:<15} Rx   {dtype} {data}"
FORMAT_DATE = "%a %b %m %I:%M:%S %p %Y"
FORMAT_EVENT = "{timestamp: 9.4f} {message}\n"

# def get_mac_address():
#     with open('/sys/class/net/wlan0/address', 'r') as w:
#         mac = w.readlines()[0][:-1]
#     return mac.replace(":","-")

# HOSTNAME = get_mac_address()

MPC5748_QUE = '00:0F:00:C3:F6:EB_R_v'

def DUT_receive_UI(body):
    print("DUT_receive_UI start...")
    json_dic = body.decode("utf-8")
    json2python = json.loads(json_dic)
    # print("Python-data(%s)" % json2python)
    return json2python


'''-----------------------------------------------------------HeartBeat-----------------------------------------------------------'''
# heart_dic = {
#     'source': 'source_clientID',
#     'destination': 'destination_clientID',
#     'type': 'HEARTBEAT',
#     'content': '',
#
#     'channel status': {},
#     'MAC': HOSTNAME
# }
# def fun_timer():
#     # print("heart_dic %s" % heart_dic)
#     json_heart = json.dumps(heart_dic)
#     # print("json_heart %s" % json_heart)
#     # print("HOST-MAC: %s" % HOSTNAME)
#     HB_channel.basic_publish(exchange='online_client',
#                              routing_key='DUT_online',
#                              body=json_heart)
#     global timer
#     timer = threading.Timer(5, fun_timer)
#     timer.start()
#
#
# def heartbeat():  # 线程任务函数 heartbeat()
#     print('%s is running...' % threading.current_thread().name)
#     timer = threading.Timer(1, fun_timer)
#     timer.start()
#     HB_channel.start_consuming()










'''-----------------------------------------------------------recorder_udp_server-----------------------------------------------------------'''
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

        # with open('/home/root/test.asc', 'a') as f:
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

'''-----------------------------------------------------------config_client-----------------------------------------------------------'''

def mpc5748_process(Mpc5748Cmd_channel, props, body, mpc5748cmd_temp):
    ip_port = ('192.168.0.200', 8)  #ip_port = ('127.0.0.1', 6666)#
    s = socket.socket()
    s.connect(ip_port)
    inp = "On,12345678,Add".encode()
    print("2")
    s.sendall(inp)
    print("2")
    # while True:  # 通过一个死循环不断接收用户输入，并发送给服务器
    #     inp = input("Please enter the information to be sent: ").strip()
    #     print("1: %s" % inp)
    #     print("2")
    #     # print("On,12345678,Add".strip())
    #     print("2")
    #     if not inp:  # 防止输入空信息，导致异常退出
    #         continue
    #     print(inp.encode('UTF-8'))
    #     print("3")
    #     s.sendall(inp.encode())
    #
    #     if inp == "exit":  # 如果输入的是‘exit’，表示断开连接
    #         break
    #
    #     server_reply = s.recv(1024).decode()
    #     print("server_reply: %s" % server_reply)
    s.close()  # 关闭连接

def on_request_mpc5748(Mpc5748Cmd_channel, method, props, body):
    json2python_mpc5748cmd = DUT_receive_UI(body)
    mpc5748_process(Mpc5748Cmd_channel, props, body, json2python_mpc5748cmd)
    response = json.dumps(json2python_mpc5748cmd)
    print("response: %s" % response)
    Mpc5748Cmd_channel.basic_publish(exchange='',
                                routing_key=props.reply_to,
                                properties=pika.BasicProperties(correlation_id= \
                                                                    props.correlation_id),
                                body=str(response))
    Mpc5748Cmd_channel.basic_ack(delivery_tag=method.delivery_tag)

def config_client():
    Mpc5748Cmd_channel.queue_declare(queue=MPC5748_QUE, auto_delete=True)
    Mpc5748Cmd_channel.basic_qos(prefetch_count=1)
    Mpc5748Cmd_channel.basic_consume(on_request_mpc5748, queue=MPC5748_QUE)
    print("Awaiting RPC requests... %s is running..." % threading.current_thread().name)
    Mpc5748Cmd_channel.start_consuming()



if __name__ == '__main__':
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters(host_address, 5672, '/', credentials)

    # HB_connection = pika.BlockingConnection(parameters)
    Mpc5748Cmd_connection = pika.BlockingConnection(parameters)

    # HB_channel = HB_connection.channel()
    Mpc5748Cmd_channel = Mpc5748Cmd_connection.channel()

    # t0 = threading.Thread(target=heartbeat, name='HeartBeat-Thread', args=())
    t_server = threading.Thread(target=recorder_udp_server, name='Record-Thread', args=())
    t_client = threading.Thread(target=config_client, name='Config-Thread', args=())

    # t0.start()
    t_server.start()
    t_client.start()
