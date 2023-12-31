from PyQt5 import QtGui
from PyQt5 import QtWidgets, QtCore
# -*- coding: utf-8 -*-
"""
PlotWidget.py -  Convenience class--GraphicsView widget displaying a single PlotItem
Copyright 2010  Luke Campagnola
Distributed under MIT/X11 license. See license.txt for more information.
"""

from pyqtgraph import QtCore, QtGui
from pyqtgraph import GraphicsView
from pyqtgraph.graphicsItems.PlotItem import *
from math import ceil
import pyqtgraph as pg

__all__ = ['PlotWidget']
class PlotWidget(GraphicsView):
    
    # signals wrapped from PlotItem / ViewBox
    sigRangeChanged = QtCore.Signal(object, object)
    sigTransformChanged = QtCore.Signal(object)
    
    """
    :class:`GraphicsView <pyqtgraph.GraphicsView>` widget with a single 
    :class:`PlotItem <pyqtgraph.PlotItem>` inside.
    
    The following methods are wrapped directly from PlotItem: 
    :func:`addItem <pyqtgraph.PlotItem.addItem>`, 
    :func:`removeItem <pyqtgraph.PlotItem.removeItem>`, 
    :func:`clear <pyqtgraph.PlotItem.clear>`, 
    :func:`setAxisItems <pyqtgraph.PlotItem.setAxisItems>`,
    :func:`setXRange <pyqtgraph.ViewBox.setXRange>`,
    :func:`setYRange <pyqtgraph.ViewBox.setYRange>`,
    :func:`setRange <pyqtgraph.ViewBox.setRange>`,
    :func:`autoRange <pyqtgraph.ViewBox.autoRange>`,
    :func:`setXLink <pyqtgraph.ViewBox.setXLink>`,
    :func:`setYLink <pyqtgraph.ViewBox.setYLink>`,
    :func:`viewRect <pyqtgraph.ViewBox.viewRect>`,
    :func:`setMouseEnabled <pyqtgraph.ViewBox.setMouseEnabled>`,
    :func:`enableAutoRange <pyqtgraph.ViewBox.enableAutoRange>`,
    :func:`disableAutoRange <pyqtgraph.ViewBox.disableAutoRange>`,
    :func:`setAspectLocked <pyqtgraph.ViewBox.setAspectLocked>`,
    :func:`setLimits <pyqtgraph.ViewBox.setLimits>`,
    :func:`register <pyqtgraph.ViewBox.register>`,
    :func:`unregister <pyqtgraph.ViewBox.unregister>`
    
    
    For all 
    other methods, use :func:`getPlotItem <pyqtgraph.PlotWidget.getPlotItem>`.
    """
    def __init__(self, parent=None, background='r', plotItem=None, **kargs):
        """When initializing PlotWidget, *parent* and *background* are passed to 
        :func:`GraphicsWidget.__init__() <pyqtgraph.GraphicsWidget.__init__>`
        and all others are passed
        to :func:`PlotItem.__init__() <pyqtgraph.PlotItem.__init__>`."""
        GraphicsView.__init__(self, parent,useOpenGL=True, background='k')
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.enableMouse(False)
        self.numofcurves = 0 #v2.3
        self.curves = [] #v2.3   
        
        if plotItem is None:
            self.plotItem = PlotItem(**kargs)
        else:
            self.plotItem = plotItem
        self.setCentralItem(self.plotItem)
        ## Explicitly wrap methods from plotItem
        ## NOTE: If you change this list, update the documentation above as well.
        for m in ['addItem', 'removeItem', 'autoRange', 'clear', 'setAxisItems', 'setXRange', 
                  'setYRange', 'setRange', 'setAspectLocked', 'setMouseEnabled', 
                  'setXLink', 'setYLink', 'enableAutoRange', 'disableAutoRange', 
                  'setLimits', 'register', 'unregister', 'viewRect']:
            setattr(self, m, getattr(self.plotItem, m))
        #QtCore.QObject.connect(self.plotItem, QtCore.SIGNAL('viewChanged'), self.viewChanged)
        self.plotItem.sigRangeChanged.connect(self.viewRangeChanged)
        self.rainbo = False #v2.3   
        self.plotItem.setMouseEnabled(x=False, y=False) #v2.3
        self.plotItem.showGrid(x=True, y=True, alpha=1) #v2.3
        

    def close(self):
        self.plotItem.close()
        self.plotItem = None
        #self.scene().clear()
        #self.mPlotItem.close()
        self.setParent(None)
        super(PlotWidget, self).close()

    def __getattr__(self, attr):  ## implicitly wrap methods from plotItem
        if hasattr(self.plotItem, attr):
            m = getattr(self.plotItem, attr)
            if hasattr(m, '__call__'):
                return m
        raise AttributeError(attr)
    
    def viewRangeChanged(self, view, range):
        #self.emit(QtCore.SIGNAL('viewChanged'), *args)
        self.sigRangeChanged.emit(self, range)

    def widgetGroupInterface(self):
        return (None, PlotWidget.saveState, PlotWidget.restoreState)

    def saveState(self):
        return self.plotItem.saveState()
        
    def restoreState(self, state):
        return self.plotItem.restoreState(state)
        
    def getPlotItem(self):
        """Return the PlotItem contained within."""
        return self.plotItem

#v2.3 Multiple curves & Curve colors ----------------------------------------------
    def createCurve(self):
        self.numofcurves +=1     
        self.plotItem.curve = pg.PlotCurveItem()
        self.plotItem.curve.setPen('k',width=2)
        self.plotItem.addItem(self.plotItem.curve)
        self.curves.append(self.plotItem.curve)

    def removeCurve(self):
        self.numofcurves -=1
        self.plotItem.removeItem(self.curves[-1])
        del self.curves[-1]

    def rainbow(self):
        if self.rainbo:
            for idx in range(self.numofcurves-1):
                self.plotItem.curves[idx+1].setPen('k',width=2)
            self.rainbo = False
        else:
            for idx in range(self.numofcurves-1):
                self.plotItem.curves[idx+1].setPen(idx,(self.numofcurves-1)*1.3,width=2)
            self.rainbo = True
#-----------------------------------------------------------------------------------

