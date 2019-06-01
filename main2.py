#!/usr/bin/env python
# -*- coding:utf-8 -*-

import socket
import threading
import binascii

# from datetime import datetime
# import can
# from can import Logger
#
# # BaseIOHandler类
# from abc import ABCMeta, abstractmethod
# #Listener类 同上
#
# #Logger类
# import logging
#
# #ASCWriter类
# from datetime import datetime
# import time
# #import logging
#
# #channel2int
# import re
#
# #ASCWriter类
# #import time
#
#
# def channel2int(channel):
#     """Try to convert the channel to an integer.
#
#     :param channel:
#         Channel string (e.g. can0, CAN1) or integer
#
#     :returns: Channel integer or `None` if unsuccessful
#     :rtype: int
#     """
#     if channel is None:
#         return None
#     if isinstance(channel, int):
#         return channel
#     # String and byte objects have a lower() method
#     if hasattr(channel, "lower"):
#         match = re.match(r'.*(\d+)$', channel)
#         if match:
#             return int(match.group(1))
#     return None
#
#
# class BaseIOHandler(object):
#     """A generic file handler that can be used for reading and writing.
#
#     Can be used as a context manager.
#
#     :attr file-like file:
#         the file-like object that is kept internally, or None if none
#         was opened
#     """
#
#     __metaclass__ = ABCMeta
#
#     def __init__(self, file, mode='rt'):
#         """
#         :param file: a path-like object to open a file, a file-like object
#                      to be used as a file or `None` to not use a file at all
#         :param str mode: the mode that should be used to open the file, see
#                          :func:`builtin.open`, ignored if *file* is `None`
#         """
#         if file is None or (hasattr(file, 'read') and hasattr(file, 'write')):
#             # file is None or some file-like object
#             self.file = file
#         else:
#             # file is some path-like object
#             self.file = open(file, mode)
#
#         # for multiple inheritance
#         super(BaseIOHandler, self).__init__()
#
#     def __enter__(self):
#         return self
#
#     def __exit__(self, *args):
#         self.stop()
#
#     def stop(self):
#         if self.file is not None:
#             # this also implies a flush()
#             self.file.close()
#
#
# class Listener(object):
#     """The basic listener that can be called directly to handle some
#     CAN message::
#
#         listener = SomeListener()
#         msg = my_bus.recv()
#
#         # now either call
#         listener(msg)
#         # or
#         listener.on_message_received(msg)
#
#     """
#
#     __metaclass__ = ABCMeta
#
#     @abstractmethod
#     def on_message_received(self, msg):
#         """This method is called to handle the given message.
#
#         :param can.Message msg: the delivered message
#
#         """
#         pass
#
#     def __call__(self, msg):
#         return self.on_message_received(msg)
#
#     def on_error(self, exc):
#         """This method is called to handle any exception in the receive thread.
#
#         :param Exception exc: The exception causing the thread to stop
#         """
#
#     def stop(self):
#         """
#         Override to cleanup any open resources.
#         """
#
#
# log1 = logging.getLogger("can.io.logger")
# class Logger(BaseIOHandler, Listener):
#     """
#     Logs CAN messages to a file.
#
#     The format is determined from the file format which can be one of:
#       * .asc: :class:`can.ASCWriter`
#       * .blf :class:`can.BLFWriter`
#       * .csv: :class:`can.CSVWriter`
#       * .db: :class:`can.SqliteWriter`
#       * .log :class:`can.CanutilsLogWriter`
#       * other: :class:`can.Printer`
#
#     .. note::
#         This class itself is just a dispatcher, and any positional an keyword
#         arguments are passed on to the returned instance.
#     """
#
#     @staticmethod
#     def __new__(cls, filename, *args, **kwargs):
#         """
#         :type filename: str or None or path-like
#         :param filename: the filename/path the file to write to,
#                          may be a path-like object if the target logger supports
#                          it, and may be None to instantiate a :class:`~can.Printer`
#
#         """
#         if filename:
#             if filename.endswith(".asc"):
#                 return ASCWriter(filename, *args, **kwargs)
#             # elif filename.endswith(".blf"):
#             #     return BLFWriter(filename, *args, **kwargs)
#             # elif filename.endswith(".csv"):
#             #     return CSVWriter(filename, *args, **kwargs)
#             # elif filename.endswith(".db"):
#             #     return SqliteWriter(filename, *args, **kwargs)
#             # elif filename.endswith(".log"):
#             #     return CanutilsLogWriter(filename, *args, **kwargs)
#
#         # else:
#         log1.info('unknown file type "%s", falling pack to can.Printer', filename)
#         return Printer(filename, *args, **kwargs)
#
# log3 = logging.getLogger('can.io.printer')
# class Printer(BaseIOHandler, Listener):
#     """
#     The Printer class is a subclass of :class:`~can.Listener` which simply prints
#     any messages it receives to the terminal (stdout). A message is tunred into a
#     string using :meth:`~can.Message.__str__`.
#
#     :attr bool write_to_file: `True` iff this instance prints to a file instead of
#                               standard out
#     """
#
#     def __init__(self, file=None):
#         """
#         :param file: an optional path-like object or as file-like object to "print"
#                      to instead of writing to standard out (stdout)
#                      If this is a file-like object, is has to opened in text
#                      write mode, not binary write mode.
#         """
#         self.write_to_file = file is not None
#         super(Printer, self).__init__(file, mode='w')
#
#     def on_message_received(self, msg):
#         if self.write_to_file:
#             self.file.write(str(msg) + '\n')
#         else:
#             print(msg)
#
#
# logger2 = logging.getLogger('can.io.asc')
# class ASCWriter(BaseIOHandler, Listener):
#     """Logs CAN data to an ASCII log file (.asc).
#
#     The measurement starts with the timestamp of the first registered message.
#     If a message has a timestamp smaller than the previous one or None,
#     it gets assigned the timestamp that was written for the last message.
#     It the first message does not have a timestamp, it is set to zero.
#     """
#
#     FORMAT_MESSAGE = "{channel}  {id:<15} Rx   {dtype} {data}"
#     FORMAT_DATE = "%a %b %m %I:%M:%S %p %Y"
#     FORMAT_EVENT = "{timestamp: 9.4f} {message}\n"
#
#     def __init__(self, file, channel=1):
#         """
#         :param file: a path-like object or as file-like object to write to
#                      If this is a file-like object, is has to opened in text
#                      write mode, not binary write mode.
#         :param channel: a default channel to use when the message does not
#                         have a channel set
#         """
#         super(ASCWriter, self).__init__(file, mode='w')
#         self.channel = channel
#
#         # write start of file header
#         now = datetime.now().strftime("%a %b %m %I:%M:%S %p %Y")
#         self.file.write("date %s\n" % now)
#         self.file.write("base hex  timestamps absolute\n")
#         self.file.write("internal events logged\n")
#
#         # the last part is written with the timestamp of the first message
#         self.header_written = False
#         self.last_timestamp = None
#         self.started = None
#
#     def stop(self):
#         if not self.file.closed:
#             self.file.write("End TriggerBlock\n")
#         super(ASCWriter, self).stop()
#
#     def log_event(self, message, timestamp=None):
#         """Add a message to the log file.
#
#         :param str message: an arbitrary message
#         :param float timestamp: the absolute timestamp of the event
#         """
#
#         if not message:  # if empty or None
#             logger2.debug("ASCWriter: ignoring empty message")
#             return
#
#         # this is the case for the very first message:
#         if not self.header_written:
#             self.last_timestamp = (timestamp or 0.0)
#             self.started = self.last_timestamp
#             formatted_date = time.strftime(self.FORMAT_DATE, time.localtime(self.last_timestamp))
#             self.file.write("Begin Triggerblock %s\n" % formatted_date)
#             self.header_written = True
#             self.log_event("Start of measurement")  # caution: this is a recursive call!
#
#         # figure out the correct timestamp
#         if timestamp is None or timestamp < self.last_timestamp:
#             timestamp = self.last_timestamp
#
#         # turn into relative timestamps if necessary
#         if timestamp >= self.started:
#             timestamp -= self.started
#
#         line = self.FORMAT_EVENT.format(timestamp=timestamp, message=message)
#         self.file.write(line)
#
#     def on_message_received(self, msg):
#
#         if msg.is_error_frame:
#             self.log_event("{}  ErrorFrame".format(self.channel), msg.timestamp)
#             return
#
#         if msg.is_remote_frame:
#             dtype = 'r'
#             data = []
#         else:
#             dtype = "d {}".format(msg.dlc)
#             data = ["{:02X}".format(byte) for byte in msg.data]
#
#         arb_id = "{:X}".format(msg.arbitration_id)
#         if msg.is_extended_id:
#             arb_id += 'x'
#
#         channel = channel2int(msg.channel)
#         if channel is None:
#             channel = self.channel
#         else:
#             # Many interfaces start channel numbering at 0 which is invalid
#             channel += 1
#
#         serialized = self.FORMAT_MESSAGE.format(channel=channel,
#                                                 id=arb_id,
#                                                 dtype=dtype,
#                                                 data=' '.join(data))
#
#         self.log_event(serialized, msg.timestamp)
#







def recorder_server():
    ip_port = ('192.168.0.200', 7)
    # ip_port = ('127.0.0.1', 6666)
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
        print("server_reply4: %s" % server_reply4)

        for i in range(len(server_reply4)):
            # with open(r'F:\yhh\0-Source\work\work_data_collect_record\TBOX\data\test.txt', 'a') as f:
            with open('/mnt/hgfs/work/work_data_collect_record/TBOX/data/test.asc', 'a') as f:
                if i == 0:
                    f.write('can0:')
                    f.write(' ')
                f.write(str(hex(server_reply4[i]))[2:])
                f.write(' ')
                if i == 7:
                    f.write('\n')
        # logger = Logger('1.asc')
        # try:
        #     while True:
        #         msg = s.recv(1024)
        #         if msg is not None:
        #             logger(msg)
        # except KeyboardInterrupt:
        #     pass
        # finally:
        #     logger.stop()

    s.close()  # 关闭连接

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
    t_server = threading.Thread(target=recorder_server, name='Record-Thread', args=())
    t_client = threading.Thread(target=config_client, name='Config-Thread', args=())

    t_server.start()
    t_client.start()


