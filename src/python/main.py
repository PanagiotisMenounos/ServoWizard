import os
import sys
import time
# from PyQt5 import QtWidgets, uic, QtCore
from multiprocessing import Process, Pipe
from PyQt5 import QtGui
import numpy as np
import serial.tools.list_ports
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from data_process import f
from mainwindow import Ui_MainWindow

if __name__ == '__main__':
#v2.2 Assign plot work to thread -------------------------------------------------------------------------    
    # class WorkerSignals(QObject):
    #     finished = pyqtSignal()
    #     error = pyqtSignal(tuple)
    #     result = pyqtSignal(object)
    #     progress = pyqtSignal(int)


    class Worker(QRunnable):
        def __init__(self, *args, **kwargs):
            super(Worker, self).__init__()
            self.dosomething = False
            window.p2.clicked.connect(self.doSmth)

        def doSmth(self):
            self.dosomething = True

        def SendReceive(self):
            parent_pipe_1.send(2)
            parent_pipe_1.send(window.Parameters)
            self.update()

        def update(self):            
            xdata = parent_pipe_1.recv()
            ydata = parent_pipe_1.recv()
            udata = [window.Parameters[12]/100000]*len(xdata)
            window.plotwidget_1.plotItem.curves[0].setData(xdata, udata)
            window.plotwidget_1.plotItem.curves[window.spinBox.value()].setData(xdata, ydata)           

        @pyqtSlot()
        def run(self):
            while True:
                if window.stopWorkers == True:
                    break

                if self.dosomething:
                    window.save_settings()
                    self.SendReceive()
                    self.dosomething = False
                time.sleep(0.05)
#------------------------------------------------------------------------------------------------------------

    class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow, QRunnable):
        def __init__(self, *args, obj=None, **kwargs):
            super(MainWindow, self).__init__(*args, **kwargs)
            self.setupUi(self)
            self.assign_buttons()
            self.load_settings()
            self.declare_vars()
            
            self.threadpool = QThreadPool()

            self.plotwidget_1.setBackground('w')
            
            self.comboBox.currentTextChanged.connect(self.selectPort)
            self.addPosCurve()
            self.addPosCurve()
            self.comboBox_2.currentIndexChanged.connect(self.setCurveColor)

        def declare_vars(self):
            #v2.0
            self.Parameters = np.zeros(14,np.int32)
            self.con_state = 0
            #v2.1
            self.chosenPort = ""
            self.ports = serial.tools.list_ports.comports()
            self.comboBox.addItem("")
            for p in self.ports:
                self.comboBox.addItem(p.device)
            #v2.2
            self.stopWorkers = False

        def assign_buttons(self):
            #v2.0
            self.p0.clicked.connect(self.con_discon_port)
            self.p1.clicked.connect(self.reset_port)
            #self.p2.clicked.connect(self.pos_step)
            self.p3.clicked.connect(self.vel_step)
            #v2.1
            self.comboBox.currentTextChanged.connect(self.selectPort)
            #v2.3
            self.PlotButt2.setEnabled(False)
            self.PlotButt1.clicked.connect(self.addPosCurve)
            self.PlotButt2.clicked.connect(self.remPosCurve)
            # self.radioButton.toggled.connect(self.referenceCurve)
            #v2.4
            self.checkBox.stateChanged.connect(self.referenceCurve)

        def load_settings(self):
            file = open(os.getenv('LOCALAPPDATA')+'\\Cervo\\settings\\settings.txt','r') #read general setting file and set them
            boxes = file.readlines()
            file.close()
            for i in range (0,14): #b0-bmax
               b = getattr(self, "b{}".format(i))  #self.b[i], https://stackoverflow.com/questions/47666922/set-properties-of-multiple-qlineedit-using-a-loop
               b.setValue(float(boxes[i].strip())) #strip() removes'/n'

        def save_settings(self):
            file = open(os.getenv('LOCALAPPDATA')+'\\Cervo\\settings\\settings.txt','w') #read general setting file and set them
            for i in range (0,14):
               b = getattr(self, "b{}".format(i)) #self.b[i], https://stackoverflow.com/questions/47666922/set-properties-of-multiple-qlineedit-using-a-loop
               text = str(b.value()) #v2.4 spin box read
               if (text==''): #check if it is an empty string
                   file.write("\n")
                   self.Parameters[i] = 0
               else:
                   file.write(text+"\n")
                   self.Parameters[i] = int(float(text)*100000)
            file.close()

        def con_discon_port(self):
            if worker.dosomething == False: #v2.4 Check if worker is communicating with data_process (bug fix)
                if self.con_state == 0:
                    if len(self.chosenPort)>1:
                        parent_pipe_1.send(1)
                        self.con_state = parent_pipe_1.recv()
                        self.p0.setText("Disconnect")

                elif self.con_state == 1:
                    parent_pipe_1.send(3)
                    self.con_state = parent_pipe_1.recv()
                    self.p0.setText("Connect")
                

        def reset_port(self):
            print("reset")

        def vel_step(self):
            print("vel_step")

        def closeEvent(self, event): #trigger on closing
            self.stopWorkers = True
            self.save_settings() #save settings
            parent_pipe_1.send(4)
            p.terminate()

        def update(self):            
            xdata = parent_pipe_1.recv()
            ydata = parent_pipe_1.recv()
            udata = [self.Parameters[12]/100000]*len(xdata)
            self.plotwidget_1.plotItem.curves[0].setData(xdata, ydata)
            self.plotwidget_1.plotItem.curves[1].setData(xdata, udata)
            

#v2.1 Serialport Autodetect----------------------------------------------------------------------------------------------------------
        def selectPort(self,s):
            self.chosenPort = s
            parent_pipe_1.send(5)
            parent_pipe_1.send(s)

        def PortChange(self):
            prtsNow = serial.tools.list_ports.comports()
            if len(self.ports) < len(prtsNow):
                for i  in prtsNow:
                    if i not in self.ports:
                        self.comboBox.addItem(i.device)
                self.ports = serial.tools.list_ports.comports()

            elif len(self.ports) > len(prtsNow):
                for i  in self.ports:
                    if i not in prtsNow:
                        if i.device == self.chosenPort:
                            self.con_state = 0
                            self.p0.setText("Connect")
                            self.comboBox.setCurrentIndex(0)
                        self.comboBox.removeItem(self.comboBox.findText(i.device))
                self.ports = serial.tools.list_ports.comports()

#v2.3 Multiple curves & Curve colors ----------------------------------------------
        def plotcolorset(self):
            color = QColorDialog.getColor()
            self.plotwidget_1.setForegroundColor(color)

        # def referenceCurve(self, bool):
        #     if bool:
        #         self.plotwidget_1.plotItem.curves[0].setVisible(True)
        #     else:
        #         self.plotwidget_1.plotItem.curves[0].setVisible(False)

        def addPosCurve(self):
            if self.plotwidget_1.numofcurves<100:
                if self.plotwidget_1.numofcurves == 2:
                    self.PlotButt2.setEnabled(True)
                self.comboBox_2.addItem(str(self.plotwidget_1.numofcurves))
                self.plotwidget_1.createCurve()
                if self.plotwidget_1.numofcurves > 1:
                    self.spinBox.setMaximum(self.plotwidget_1.numofcurves-1)

        def remPosCurve(self):
            self.comboBox_2.removeItem(self.plotwidget_1.numofcurves)
            self.plotwidget_1.removeCurve()
            self.spinBox.setMaximum(self.plotwidget_1.numofcurves-1)
            if self.plotwidget_1.numofcurves == 2:
                self.PlotButt2.setEnabled(False)

        def setCurveColor(self, s):
            if s == 0:
                return
            elif s == 1:
                self.comboBox_2.setCurrentIndex(0)
                self.plotwidget_1.rainbow()
            else:
                self.comboBox_2.setCurrentIndex(0)
                color = QColorDialog.getColor()
                self.plotwidget_1.curves[s-1].setPen(color,width=2)

#v2.4 ------------------------------------------------------------------------------------


        def referenceCurve(self, state):
            if state == 2 :
                self.plotwidget_1.plotItem.curves[0].setVisible(True)
            else:
                self.plotwidget_1.plotItem.curves[0].setVisible(False)

#-----------------------------------------------------------------------------------

    
    # Data process (connection pipe, assign, begin)
    parent_pipe_1, child_pipe_1 = Pipe()
    p = Process(target=f , args=(child_pipe_1, ))
    p.start()

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()

    #v2.2 Assign and start thread
    worker = Worker()
    window.threadpool.start(worker)

    #v2.1 Check the port timer
    timer = QtCore.QTimer()
    timer.timeout.connect(window.PortChange)
    timer.start(25)

    

    window.show()
    app.exec()
   