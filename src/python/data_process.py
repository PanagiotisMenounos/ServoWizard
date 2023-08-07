from multiprocessing import Process, Pipe
import time
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import os
import math
import time
import serial
import struct

position = np.array(1)
Time = np.array(1)

def f(data_pipe):
    global Time, position
    
    p = "p"
    p = p[0].encode('ascii')
    
    while True:
        todo = data_pipe.recv()
        if todo==1:
            try:
               ser = serial.Serial(port ,115200, timeout = 0.5)
               data_pipe.send(1)
               time.sleep(0.5)
            except:
                print("failed to connect")
                data_pipe.send(0)
        if todo==2:
            try:
                ser.write(p)
                # data_pipe.send(1)
                Parameters = data_pipe.recv()
                # Parameters
                mult = 100000
                Time2plot = int(Parameters[11]/100000)# In milliseconds
                Timestep = int(Parameters[10]/100000) # In microseconds
                Kp = Parameters[0]
                Ki = Parameters[1]
                Kd = Parameters[2]
                AS = 124 # Number of elements per array
                BpE = 4 # Bytes per element in array
                stepsize = int(Parameters[12]/100000) # Setpointchange
                # Parameters
                # Define required values
                data = np.array(AS)
                ArrTrec = int(math.ceil(1000*Time2plot/Timestep/AS)) #Number off arrays sent
                PlotSize = int(ArrTrec*AS)
                position = np.zeros(PlotSize, dtype=np.uint64)
                Time = np.zeros(PlotSize, dtype=np.float64)
                case=b'\x00'
                DATA = struct.pack('7i', Kp, Ki,Kd, mult, ArrTrec, Timestep, stepsize)
                ser.write(case) 
                ser.write(DATA)
                getData(ArrTrec,AS,BpE, ser)
                timeArray(PlotSize, Timestep)
                data_pipe.send(Time)
                data_pipe.send(position)
            except:
                print("Failed")
        if todo == 3:
            try:
               ser.close()
               data_pipe.send(0)
            except:
                data_pipe.send(1)
        if todo == 4:
            ser.close()
            break

        if todo == 5:
            port = data_pipe.recv()

def getData(ArrTrec,AS,BpE, ser):
    global position
    for i in range(0,ArrTrec):
        j=i*AS
        size=int(AS*BpE)
        incomebytes=ser.read(size)
        data = struct.unpack("124i",incomebytes)
        position[j:j+AS] = data

def timeArray(PlotSize, Timestep):
    global Time
    for z in range(1,PlotSize):
        Time[z] = Time[z-1] + (Timestep/1000000)

    

























    # ser = serial.Serial('COM4' , 115200)
    # time.sleep(2)
    # print("start moving babe")
    # x="p"
    # ser.write(x[0].encode('ascii'))
    # time.sleep(2)
    # i = 0
    # data = np.array(124)
    # position = np.zeros(40000)
    # timediff = np.zeros(40000)
    # timestart=time.time()
    # # ser.flushInput()
    # # ser.flushOutput()
    # i=0
    # while (time.time()-timestart)<1:
    #     incomebytes=ser.read(248)
    #     data = struct.unpack("124h",incomebytes)
        
    #     position[i:i+62] = data[0:62]
    #     timediff[i:i+62] = data[62:]
    #     i=i+62

    # # del position[i+62:]
    # # del timediff[i+62:]
    # ser.close()
    
    # data_pipe.send(timediff)
    # data_pipe.send(position)

    # ser = serial.Serial('COM4' , 9600)
    # o = 0
    # p = math.pi
    # step = 1/(Hz)
    # ydata = np.zeros((seconds*Hz+1), dtype=np.float32)
    # ydata2 = ydata
    # # ycos = numpy.cos(list(numpy.arange(0,p+p/step,step)))
    # # start = data_pipe.recv()
    # x=p/2
    # data_pipe.send(ydata)
    # bef=time.time()
    # while True:
    #     if time.time()-bef >= step:
    #         b = np.float(ser.readline()[:-2])
    #         ydata = np.append(ydata[1:], b)
    #         data_pipe.send(ydata)
    #         bef=time.time()
    #     else:
    #         ser.readline()

    #     # for i in range(Hz):
            
    #     #     data_pipe.send(ydata)
    #     #     b = np.float(ser.readline()[:-2])
    #     #     # data_pipe.send(ydata2)
    #     #     ydata = np.append(ydata[1:], b)
    #     #     # ydata2 = np.append(ydata2[1:], (np.sin((x)*2, dtype=np.float32)))
    #     #     x += step/8


    # # fps = 1000/(data_pipe.recv()-start)
    # # data_pipe.send(fps)
