#!/usr/bin/env python
# -*- coding:utf-8 -*-
import socket
import threading
import binascii
import time
import datetime
# from datetime import datetime

import os

import pika
import json
from modules import db

host_address = 'www.dingauto.cn'
FORMAT_MESSAGE = "{channel}  {id:<15} Rx   {dtype} {data}"
FORMAT_DATE = "%a %b %m %I:%M:%S %p %Y"
FORMAT_EVENT = "{timestamp: 9.4f} {message}\n"

now_flag = 0
otherStyleTime = 0

def get_mac_address():
    with open('/sys/class/net/wlan0/address', 'r') as w:
        mac = w.readlines()[0][:-1]
    return mac.replace(":","-")

HOSTNAME = get_mac_address()
MPC5748_QUE = HOSTNAME + '_R_v'

def DUT_receive_UI(body):
    print("DUT_receive_UI start...")
    json_dic = body.decode("utf-8")
    json2python = json.loads(json_dic)
    return json2python


def get_filename(n,format):
    global now_flag
    # global now
    global otherStyleTime
    if now_flag == 0:
        now = datetime.datetime.now()
        otherStyleTime = now.strftime("%Y-%m-%d_%H%M%S")
        now_flag = 1

    return "dut_" + get_mac_address() + '_' + otherStyleTime + '.'+ str(n) + '.'+ str(format).lower()

root_path = db.root_path['log']
'''-----------------------------------------------------------recorder_udp_server-----------------------------------------------------------'''
correlation_dic_start_time = {}
correlation_dic_file = {}
correlation_dic_pid = {}
server_list = []
data_list = []

def recorder_udp_server_sessions(props, body, mpc5748cmd_temp):
    print("Awaiting RPC requests... %s is running3..." % threading.current_thread().name)
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters(host_address, 5672, '/', credentials)
    Send_UI_connection3 = pika.BlockingConnection(parameters)
    Send_UI_channel3 = Send_UI_connection3.channel()

    send_time1 = 0
    num = 0
    correlation_dic_pid[props.correlation_id] = True

    f = open(root_path+correlation_dic_file[props.correlation_id], "w")
    # f.write("Python...\n")
    f.close()
    while correlation_dic_pid[props.correlation_id]:
        if int(round(time.time() * 1000)) > send_time1 + 3000:
            send_time1 = int(round(time.time() * 1000))
            mpc5748cmd_temp["content"] = ""
            s_time = time.mktime(time.localtime(int(time.time()))) - time.mktime(
                correlation_dic_start_time[props.correlation_id])
            m, s = divmod(s_time, 60)
            h, m = divmod(m, 60)
            mpc5748cmd_temp["elapsed time"] = str(h)[:-2] + 'h' + str(m)[:-2] + 'm' + str(s)[:-2] + 's'

            try:
                file_size2 = int(os.path.getsize(root_path + correlation_dic_file[props.correlation_id]))
            except Exception as e:
                print(e)

            mpc5748cmd_temp["log file size"] = str(file_size2 // 1000) + '.' + (str(file_size2 / 1000).split('.')[
                1])[
                                                                               :3] + 'K'
            # print("1111: %s" % mpc5748cmd_temp["log file size"])
            if int(mpc5748cmd_temp["log file size"][:-1].split('.')[0]) >= 50:#50000:
                print("file >50M")
                num = num +1
                correlation_dic_file[props.correlation_id] = get_filename(num,mpc5748cmd_temp["file format"])


            mpc5748cmd_temp["type"] = "LOG_STATUS_UPDATE"
            response = json.dumps(mpc5748cmd_temp)
            Send_UI_channel3.basic_publish(exchange=HOSTNAME,
                                           routing_key='Recording_Running',  # props.reply_to,
                                           properties=pika.BasicProperties(correlation_id= \
                                                                               props.correlation_id),
                                           body=response)

def recorder_udp_server(props, body, mpc5748cmd_temp):
    print("Awaiting RPC requests... %s is running2..." % threading.current_thread().name)
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters(host_address, 5672, '/', credentials)
    Send_UI_connection2 = pika.BlockingConnection(parameters)
    Send_UI_channel2 = Send_UI_connection2.channel()

    ip_port = ('192.168.0.222', 6666)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    s.bind(ip_port)

    # the last part is written with the timestamp of the first message
    timestamp = None
    header_written = False
    last_timestamp = None
    started = None
    send_time2 = 0

    t_server = threading.Thread(target=recorder_udp_server_sessions, name='Record-Thread', args=(props, body, mpc5748cmd_temp))
    t_server.start()

    correlation_dic_pid[props.correlation_id] = True
    while correlation_dic_pid[props.correlation_id]:
        data = s.recv(1024).strip().decode()
        # print("------------------------------------------------------")
        # print(data)
        # print(len(data))
        for i in range(len(data)):
            if (i+1)%16 == 0:
                data_list.append(data[i-15:i+1])# data_list = data.split('\n')
            else:
                pass

        for j in range(len(data_list)):
            # print(data_list[j])
            server_reply4 = list(bytearray.fromhex(binascii.hexlify("".join(data_list[j]).encode()).decode()))
            # print(server_reply4)

            #Sessions
            for k in range(len(server_reply4)):
                server_list.append(str(hex(server_reply4[k]))[2:])
            mpc5748cmd_temp["content"] = " ".join(server_list).replace('\'', "") + '\n'
            server_list.clear()
            if int(round(time.time() * 1000)) > send_time2 + 300:
                send_time2 = int(round(time.time() * 1000))
                mpc5748cmd_temp["content"] = mpc5748cmd_temp["content"][:-1]
                response = json.dumps(mpc5748cmd_temp)
                Send_UI_channel2.basic_publish(exchange='',
                                               routing_key=props.reply_to,
                                               properties=pika.BasicProperties(correlation_id= \
                                                                                   props.correlation_id),
                                               body=response)
                # ***publish之后，content要清空***
                mpc5748cmd_temp["content"] = ""
        # print("------------------------------------------------------")

        with open(root_path+correlation_dic_file[props.correlation_id], 'a') as f:
            # this is the case for the very first message:
            if not header_written:
                # write start of file header
                now = datetime.datetime.now().strftime("%a %b %m %I:%M:%S %p %Y")
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
                f.write('1')#can0:
                f.write(' ')
                f.write('777')# can id
                f.write('             ')
                f.write('Rx')
                f.write('   ')
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
    print("---------------------------close-udp--------------------------------")

'''-----------------------------------------------------------config_client-----------------------------------------------------------'''
def mpc5748_process(Mpc5748Cmd_channel, props, body, mpc5748cmd_temp):
    my_db = db.MySqlConn()
    ip_port = ('192.168.0.200', 8)#ip_port = ('127.0.0.1', 6666)#ip_port = ('192.168.0.200', 8) #  #
    s = socket.socket()
    s.connect(ip_port)
    if mpc5748cmd_temp["type"] == "LOG_START_REQ":  # record start
        inp = "On,12345678,Add".encode()
        print("1")
        s.sendall(inp)
        print("1")
        # s.close()

        mpc5748cmd_temp["file format"] = 'ASC'
        global now_flag
        now_flag = 0
        num1 = 0
        correlation_dic_file[props.correlation_id] = get_filename(num1,mpc5748cmd_temp["file format"])
        correlation_dic_start_time[props.correlation_id] = time.localtime(int(time.time()))
        print("Add Correlation_dic_start_time: %s" % correlation_dic_start_time)
        mpc5748cmd_temp['content'] = {}
        t_server = threading.Thread(target=recorder_udp_server, name='Record-Thread', args=(props, body, mpc5748cmd_temp))
        t_server.start()


    elif mpc5748cmd_temp["type"] == "LOG_END_REQ":  # record end
        inp = "Off,12345678,Add".encode()
        print("2")
        s.sendall(inp)
        print("2")
        correlation_dic_pid[props.correlation_id] = False
        # s.close()
        # db record file msg
        my_db.insert_record(db.file_type_to_table['log'],
                            (correlation_dic_file[props.correlation_id], props.correlation_id,
                             time.strftime("%Y-%m-%d", time.localtime()), '',
                             '', '', ''))

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
    Mpc5748Cmd_connection = pika.BlockingConnection(parameters)
    Mpc5748Cmd_channel = Mpc5748Cmd_connection.channel()


    t_client = threading.Thread(target=config_client, name='Config-Thread', args=())
    t_client.start()