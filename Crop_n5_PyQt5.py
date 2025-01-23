import PyQt5 
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication,QVBoxLayout, QFileDialog,QMainWindow, QMessageBox
from PyQt5.QtWidgets import QButtonGroup, QPushButton, QLineEdit, QRadioButton, QCheckBox
from PyQt5.QtWidgets import QLabel, QSlider, QHBoxLayout, QWidget, QSpinBox,QGroupBox, QGridLayout
from PyQt5.QtGui import QFont 
import zarr, sys,cv2,imageio.v2 as imageio
import os, random,re
import subprocess,functools
import napari, numpy as np
import dask.array as da


# Check if natsort is installed
try:
    import natsort
    print("natsort is already installed.")
except ImportError:
    print("natsort is not installed. Installing...")
    subprocess.check_call(["pip", "install", "natsort"])
    print("natsort has been successfully installed.")
from natsort import natsorted


class Crop_n5(QMainWindow):

 def __init__(self):
  super().__init__()
  self.GetPathWindow()

 def GetPathWindow(self):
   self.setWindowTitle("Location of dataset to crop")
   self.lbl1=QLabel("Where do you want to make the croppy crops from?  : ", self)
   self.lbl1.setGeometry(270,1,650,50)
   self.lbl1.setFont(QFont('Times',12))   

   self.fusedn5button=QPushButton("Fused raw n5 data",self)
   self.fusedn5button.setGeometry(200,70,200,50)
   self.fusedn5button.setFont(QFont('times',10))
   self.fusedn5button.clicked.connect(self.fusedn5buttonclicked)
   self.tiledn5button=QPushButton("Tiled n5 data",self)   
   self.tiledn5button.setGeometry(500,70,200,50)
   self.tiledn5button.setFont(QFont('times',10))
   self.tiledn5button.clicked.connect(self.tiledn5buttonclicked)

   self.exitbutton=QPushButton("Exit",self)
   self.exitbutton.setGeometry(800,70,200,50)
   self.exitbutton.setFont(QFont('times',10))
   self.exitbutton.clicked.connect(self.on_Exit)
 
 def clear_layout(self, layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            layout.removeWidget(widget)
            widget.setParent(None)
        #else:
         #   self.clear_layout(item.layout())

 def on_Exit(self):
    if hasattr(self, 'napari_viewer'):
     self.napari_viewer.close()
     QApplication.quit()  
    self.close() 
    if hasattr(self, 'tiledn5button_mainlayout'):
     self.clear_layout(self.tiledn5button_mainlayout)
     self.second_window.close()
    if hasattr(self, 'fusedn5button_mainlayout'):
     self.clear_layout(self.fusedn5button_mainlayout)
     self.second_window.close()  
 
   
  
 def on_napari_close(self):
   # Callback function to handle Napari viewer window closing
   QApplication.quit()          
 
 def GetFusedN5Layout(self):        
   self.fusedn5button_mainlayout = QVBoxLayout(self)  
   self.second_window = QWidget() 
   self.second_window.show()
   # Set the main layout of the new window
   self.second_window.setLayout(self.fusedn5button_mainlayout)
   self.fusedn5button_mainlayout.setSpacing(40)
   self.second_window.move(20,200)
   self.second_window.setWindowTitle("FUSED N5 DATA")
   # defining first sublayout
   self.fusedn5button_sublayout1=QVBoxLayout(self)
   self.fusedn5button_sublayout1.setGeometry(QtCore.QRect(10,30,500,150))
   self.fusedn5button_sublayout1.setSpacing(40)  # Adjust the spacing value as needed
   self.fusedn5button_mainlayout.addLayout(self.fusedn5button_sublayout1)
      #defining2nd layout
   self.fusedn5button_sublayout2=QHBoxLayout(self)
   self.fusedn5button_sublayout2.setSpacing(40) 
   self.fusedn5button_sublayout2.setGeometry(QtCore.QRect(10, 150, 500, 200))
   self.fusedn5button_mainlayout.addLayout(self.fusedn5button_sublayout2)
            
    # Add FolderPath of n5 data to sublayout1
   self.slashidx = [n for (n, e) in enumerate(self.folderpath) if e == '/']
   self.labelFolderPath = QLabel(f"Folder Path=   ../... {self.folderpath[self.slashidx[-2]:]}", self)
   self.labelFolderPath.setFont(QFont('times',10))     
   self.fusedn5button_sublayout1.addWidget(self.labelFolderPath)
   self.labelFolderPath.setGeometry(1,5,30,5)
   self.labelFolderPath.setSizePolicy(PyQt5.QtWidgets.QSizePolicy.Preferred,PyQt5.QtWidgets.QSizePolicy.Preferred)
   #show len(setupids), no_of_channels,disp label to as for ref_ch to sublayout1 
   self.dashidx = [n for (n, e) in enumerate(self.folderpath) if e == '_']
   #self.No_of_Tiles=self.folderpath[self.dashidx[-1]+1:self.folderpath.find('tiles.n5')]
   self.setupids=[file for file in os.listdir(f"{self.folderpath}") if file.startswith('setup')] 
   self.setupids=natsorted(self.setupids)    
     # disp len setupid  
   self.setupid_label= QLabel(f"There are {len(self.setupids)} Setup Ids /Channels", self)   
   self.fusedn5button_mainlayout.addWidget(self.setupid_label)
   self.setupid_label.setFont(QFont('times',9))
   self.second_window.show()
    #asking what the ref chnnel is 
   self.Label_RefChannel= QLabel(f"Which is the reference channel?: ", self)
   self.Label_RefChannel.setFont(QFont('times',9))
   self.fusedn5button_sublayout2.addWidget(self.Label_RefChannel)
   # Grouping channel radio buttons
   self.channel_radio_group = QButtonGroup(self)
    # the loopy looop to display radiobuttons for channels 
   for self.ch in range (int(len(self.setupids))):
     self.radio_button_refch = QRadioButton(f"Channel{self.ch}", self)
     self.fusedn5button_sublayout2.addWidget(self.radio_button_refch)
     self.channel_radio_group.addButton(self.radio_button_refch)
     self.No_of_Tiles=1
     self.radio_button_refch.clicked.connect(functools.partial(self.radio_button_refch_click,self.ch,int(self.No_of_Tiles),self.setupids))
     self.radio_button_refch.setFont(QFont('times',9))     

 def GetTiledN5Layout(self):        
   self.tiledn5button_mainlayout = QVBoxLayout(self)  
   self.second_window = QWidget() 
   # Set the main layout of the new window
   self.second_window.setLayout(self.tiledn5button_mainlayout)
   self.tiledn5button_mainlayout.setSpacing(40)
   self.second_window.move(20,200)
   self.second_window.setWindowTitle("TILED N5 DATA")
   # defining first sublayout
   self.tiledn5button_sublayout1=QVBoxLayout(self)
   self.tiledn5button_sublayout1.setGeometry(QtCore.QRect(10,30,500,150))
   self.tiledn5button_sublayout1.setSpacing(40)  # Adjust the spacing value as needed
      #defining2nd layout
   self.tiledn5button_sublayout2=QHBoxLayout(self)
   self.tiledn5button_sublayout2.setSpacing(40) 
   self.tiledn5button_sublayout2.setGeometry(QtCore.QRect(10, 150, 500, 200))
     # adding 2 sublayouts to the main layout
   self.tiledn5button_mainlayout.addLayout(self.tiledn5button_sublayout1)
   self.tiledn5button_mainlayout.addLayout(self.tiledn5button_sublayout2)
   self.tiledn5button_sublayout2.setSizeConstraint(PyQt5.QtWidgets.QLayout.SetFixedSize)
    # Add FolderPath of n5 data to sublayout1
   self.slashidx = [n for (n, e) in enumerate(self.folderpath) if e == '/']
   self.labelFolderPath = QLabel(f"Folder Path=   ../../... {self.folderpath[self.slashidx[-2]:]}", self)
   self.labelFolderPath.setFont(QFont('times',10))     
   self.tiledn5button_sublayout1.addWidget(self.labelFolderPath)
   self.labelFolderPath.setGeometry(1,5,30,5)
   self.labelFolderPath.setSizePolicy(PyQt5.QtWidgets.QSizePolicy.Preferred,PyQt5.QtWidgets.QSizePolicy.Preferred)
   #show len(setupids), no_of_channels,disp label to as for ref_ch to sublayout1 
   self.dashidx = [n for (n, e) in enumerate(self.folderpath) if e == '_']
   self.No_of_Tiles=self.folderpath[self.dashidx[-1]+1:self.folderpath.find('tiles.n5')]
   self.setupids=[file for file in os.listdir(f"{self.folderpath}") if file.startswith('setup')] 
   self.setupids=natsorted(self.setupids)   
 
     # disp len setupid  
   self.setupid_label= QLabel(f"There are {len(self.setupids)} Setup Ids", self)   
   self.tiledn5button_sublayout1.addWidget(self.setupid_label)
   self.setupid_label.setFont(QFont('times',9))
   
   
     #disp no of chanels
   self.NoChannels_label = QLabel(f"There are {int(len(self.setupids) / int(self.No_of_Tiles))} channels here", self)
   self.NoChannels_label.setFont(QFont('times',9))
   self.tiledn5button_sublayout1.addWidget(self.NoChannels_label)
   #self.NoChannels_label.setGeometry(5,30,300,30)
   
   self.second_window.show()
    #asking what the ref chnnel is 
   self.Label_RefChannel= QLabel(f"Which is the reference channel?: ", self)
   self.Label_RefChannel.setFont(QFont('times',9))
   self.tiledn5button_sublayout2.addWidget(self.Label_RefChannel)
   # Grouping channel radio buttons
   self.channel_radio_group = QButtonGroup(self)
    # the loopy looop to display radiobuttons for channels 
   for self.ch in range (int(len(self.setupids) / int(self.No_of_Tiles))):
     self.radio_button_refch = QRadioButton(f"Channel{self.ch}", self)
     self.tiledn5button_sublayout2.addWidget(self.radio_button_refch)
     self.channel_radio_group.addButton(self.radio_button_refch)
     self.radio_button_refch.clicked.connect(functools.partial(self.radio_button_refch_click,self.ch,int(self.No_of_Tiles),self.setupids))
     self.radio_button_refch.setFont(QFont('times',9))   


    #adding sublayout3 in the function to refresh and take setupid input
 def radio_button_refch_click(self,ch,No_of_Tiles,setupids):      
   self.ref_channel=ch
   if hasattr(self, 'n5button_sublayout3'):
      self.clear_layout(self.n5button_sublayout3)
   if hasattr(self, 'n5button_sublayout4'):
      self.clear_layout(self.n5button_sublayout4)  
   if hasattr(self, 'n5button_sublayout5'):
      self.clear_layout(self.n5button_sublayout5)   
   if hasattr(self, 'n5button_sublayout6'):
      self.clear_layout(self.n5button_sublayout6) 
   if hasattr(self, 'n5button_sublayout7'):
      self.clear_layout(self.n5button_sublayout7) 
   if hasattr(self, 'n5button_sublayout8'):
      self.clear_layout(self.n5button_sublayout8)  
   if hasattr(self, 'n5button_sublayout9'):
     self.clear_layout(self.n5button_sublayout9) 
   if hasattr(self, 'n5button_sublayout10'):
     self.clear_layout(self.n5button_sublayout10)                          
   self.n5button_sublayout3=QHBoxLayout()   
   if hasattr(self, 'tiledn5button_mainlayout'):
     self.tiledn5button_mainlayout.addLayout(self.n5button_sublayout3)
   else:
     self.fusedn5button_mainlayout.addLayout(self.n5button_sublayout3)
   self.labelSetupID = QLabel("Setup ID:", self)
   self.labelSetupID.setFont(QFont('times',9))   
   self.n5button_sublayout3.addWidget(self.labelSetupID)
   # Grouping setup radio buttons
   self.radio_setupid_group = QButtonGroup(self)
   for self.s_id in range (No_of_Tiles):
     self.radio_SetupID = QRadioButton(f"{setupids[self.s_id+(ch*No_of_Tiles)]}", self)
     self.n5button_sublayout3.addWidget(self.radio_SetupID)
     self.radio_setupid_group.addButton(self.radio_SetupID)
     self.radio_SetupID.setFont(QFont('times',9))  
     self.radio_SetupID.clicked.connect(lambda checked, text=self.radio_SetupID.text(): self.getDownsampleID(text))

  
 def getDownsampleID(self,setupid):
    self.setupid=setupid
    if hasattr(self, 'n5button_sublayout4'):
      self.clear_layout(self.n5button_sublayout4)
    if hasattr(self, 'n5button_sublayout5'):
      self.clear_layout(self.n5button_sublayout5)  
    if hasattr(self, 'n5button_sublayout6'):
      self.clear_layout(self.n5button_sublayout6)   
    if hasattr(self, 'n5button_sublayout7'):
      self.clear_layout(self.n5button_sublayout7) 
    if hasattr(self, 'n5button_sublayout8'):
      self.clear_layout(self.n5button_sublayout8)   
    if hasattr(self, 'n5button_sublayout9'):
     self.clear_layout(self.n5button_sublayout9)   
    if hasattr(self, 'n5button_sublayout10'):
     self.clear_layout(self.n5button_sublayout10)       

    self.n5button_sublayout4=QHBoxLayout()   
    if hasattr(self, 'tiledn5button_mainlayout'):
      self.tiledn5button_mainlayout.addLayout(self.n5button_sublayout4)
    else:
      self.fusedn5button_mainlayout.addLayout(self.n5button_sublayout4)
    self.labeldownsampleID = QLabel("Select Downsample factor:", self)
    self.labeldownsampleID.setFont(QFont('times',9))   
    self.n5button_sublayout4.addWidget(self.labeldownsampleID)
    # Grouping setup radio buttons
    self.radio_DownsampleID_group = QButtonGroup(self)
    self.Downsample_dir=[file for file in os.listdir(f"{self.folderpath}/{self.setupid}/timepoint0") if file.startswith('s')] 
    for down_id in range (len(self.Downsample_dir)):
     self.radio_DownsampleID = QRadioButton(f"{self.Downsample_dir[down_id]}", self)
     self.n5button_sublayout4.addWidget(self.radio_DownsampleID)
     self.radio_DownsampleID_group.addButton(self.radio_DownsampleID)
     self.radio_DownsampleID.setFont(QFont('times',9))   
     self.radio_DownsampleID.clicked.connect(lambda checked, text=self.radio_DownsampleID.text(): self.napari_viewer_params1(text))
                                                                

 def napari_viewer_params1(self,downsampleid):
    self.Selected_DownsampleID=downsampleid
    if hasattr(self, 'n5button_sublayout5'):
      self.clear_layout(self.n5button_sublayout5)  
    if hasattr(self, 'n5button_sublayout6'): 
      self.clear_layout(self.n5button_sublayout6)   
    if hasattr(self, 'n5button_sublayout7'):
      self.clear_layout(self.n5button_sublayout7)  
    if hasattr(self, 'n5button_sublayout8'):
      self.clear_layout(self.n5button_sublayout8)   
    if hasattr(self, 'n5button_sublayout9'):
     self.clear_layout(self.n5button_sublayout9)  
    if hasattr(self, 'n5button_sublayout10'):
     self.clear_layout(self.n5button_sublayout10)  

    self.n5button_sublayout5=QHBoxLayout()   
    if hasattr(self, 'tiledn5button_mainlayout'):
      self.tiledn5button_mainlayout.addLayout(self.n5button_sublayout5)
    else:
      self.fusedn5button_mainlayout.addLayout(self.n5button_sublayout5)    
  
    self.labelnapari = QLabel("Viewing data in napari:", self)  
    self.labelnapari.setFont(QFont('times',9))   
    self.n5button_sublayout5.addWidget(self.labelnapari)
    self.radio_napariview_group = QButtonGroup(self)
    self.radio_napari_randomize = QRadioButton("Randomize and show single stack", self)
    self.n5button_sublayout5.addWidget(self.radio_napari_randomize)
    self.radio_napariview_group.addButton(self.radio_napari_randomize)
    self.radio_napari_randomize.setFont(QFont('times',9))   
    self.radio_napari_randomize.clicked.connect(self.show_radio_randomize)

    self.radio_napari_all_stacks = QRadioButton("Show all stacks to choose crop section", self)
    self.n5button_sublayout5.addWidget(self.radio_napari_all_stacks)
    self.radio_napariview_group.addButton(self.radio_napari_all_stacks)
    self.radio_napari_all_stacks.setFont(QFont('times',9))   
    self.radio_napari_all_stacks.clicked.connect(self.show_all_stacks)
    if not hasattr(self, 'napari_viewer'):
        self.napari_viewer = napari.Viewer()
        self.napari_viewer.window.set_geometry(1100,50,1400,1300)


 def show_all_stacks(self):
    if hasattr(self, 'n5button_sublayout6'):
      self.clear_layout(self.n5button_sublayout6)  
    if hasattr(self, 'n5button_sublayout7'):
      self.clear_layout(self.n5button_sublayout7) 
    if hasattr(self, 'n5button_sublayout8'):
      self.clear_layout(self.n5button_sublayout8) 
    if hasattr(self, 'n5button_sublayout9'):
      self.clear_layout(self.n5button_sublayout9)   
    if hasattr(self, 'n5button_sublayout10'):
      self.clear_layout(self.n5button_sublayout10)  
    f = zarr.open(self.folderpath, mode='r')
    self.data = f[f"{self.setupid}/timepoint0/{self.Selected_DownsampleID}"] 
    self.datalength=len(self.data)  
    lazy_stack = da.from_zarr(self.data)     
    self.napari_viewer.add_image(lazy_stack,name= f"{self.setupid}/timepoint0/{self.Selected_DownsampleID}", contrast_limits=[0,1500])
   
    self.n5button_sublayout6=QHBoxLayout() 
    if hasattr(self, 'tiledn5button_mainlayout'):
     self.tiledn5button_mainlayout.addLayout(self.n5button_sublayout6)
    else:
     self.fusedn5button_mainlayout.addLayout(self.n5button_sublayout6)  
    
    self.pushButton_select_stack=QPushButton("Select this stack to choose crop ROI",self)
    self.pushButton_select_stack.adjustSize()
    self.pushButton_select_stack.setFont(QFont('times',9))  
    self.n5button_sublayout6.addWidget(self.pushButton_select_stack)
    self.pushButton_select_stack.clicked.connect(self.selected_stack_toshow_in_napari) 
    self.pushButton_start_Cropping1=QPushButton("Start cropping",self)
    self.pushButton_start_Cropping1.adjustSize()
    self.pushButton_start_Cropping1.setFont(QFont('times',9))  
    self.n5button_sublayout6.addWidget(self.pushButton_start_Cropping1)
    self.pushButton_start_Cropping1.clicked.connect(self.Cropping_params1)

 def selected_stack_toshow_in_napari(self):
    self.image_layer=self.napari_viewer.layers.selection
    self.image_layer_name=self.image_layer.active.name
    self.image_layer_data = self.image_layer.active.data
    self.current_stack=self.napari_viewer.dims.current_step[0]
    self.img_stack = self.data[self.current_stack]
    print(str(self.current_stack))
    #active_stack_layer.data = active_stack
    active_stack_layer = self.napari_viewer.add_image(self.img_stack, name=f'Stack {self.current_stack}', visible=True, contrast_limits=[0,1500])

 def show_radio_randomize(self):
    if hasattr(self, 'n5button_sublayout6'):
      self.clear_layout(self.n5button_sublayout6)  
    if hasattr(self, 'n5button_sublayout7'):
      self.clear_layout(self.n5button_sublayout7) 
    if hasattr(self, 'n5button_sublayout8'):
      self.clear_layout(self.n5button_sublayout8) 
    if hasattr(self, 'n5button_sublayout9'):
      self.clear_layout(self.n5button_sublayout9)   
    if hasattr(self, 'n5button_sublayout10'):
      self.clear_layout(self.n5button_sublayout10)   

    self.n5button_sublayout6=QHBoxLayout() 
    if hasattr(self, 'tiledn5button_mainlayout'):
     self.tiledn5button_mainlayout.addLayout(self.n5button_sublayout6)
    else:
     self.fusedn5button_mainlayout.addLayout(self.n5button_sublayout6)    
    
    self.pushButton_stackRandomize=QPushButton("Generate random stack",self)
    self.pushButton_stackRandomize.adjustSize()
    self.pushButton_stackRandomize.setFont(QFont('times',9))  
    self.n5button_sublayout6.addWidget(self.pushButton_stackRandomize)
    self.pushButton_stackRandomize.clicked.connect(self.randomstackdisplay) 
    self.RandomStack_qline= QLineEdit()
    self.RandomStack_qline.setFont(QFont('times',9))  
    self.RandomStack_qline.setMaxLength(10)  
    self.n5button_sublayout6.addWidget(self.RandomStack_qline)
    self.pushButton_show_stack=QPushButton("Show stack in napari",self)
    self.pushButton_show_stack.adjustSize()
    self.pushButton_show_stack.setFont(QFont('times',9))  
    self.n5button_sublayout6.addWidget(self.pushButton_show_stack)
    self.pushButton_show_stack.clicked.connect(self.show_stack_in_napari) 
    self.pushButton_start_Cropping1=QPushButton("Start cropping",self)
    self.pushButton_start_Cropping1.adjustSize()
    self.pushButton_start_Cropping1.setFont(QFont('times',9))  
    self.n5button_sublayout6.addWidget(self.pushButton_start_Cropping1)
    self.pushButton_start_Cropping1.clicked.connect(self.Cropping_params1)

 def Cropping_params1(self):
    if hasattr(self, 'n5button_sublayout7'):
      self.clear_layout(self.n5button_sublayout7) 
    if hasattr(self, 'n5button_sublayout8'):
      self.clear_layout(self.n5button_sublayout8)  
    if hasattr(self, 'n5button_sublayout9'):
      self.clear_layout(self.n5button_sublayout9) 
    if hasattr(self, 'n5button_sublayout10'):
     self.clear_layout(self.n5button_sublayout10)   

    self.n5button_sublayout7=QHBoxLayout()   
    if hasattr(self, 'tiledn5button_mainlayout'):
     self.tiledn5button_mainlayout.addLayout(self.n5button_sublayout7)
    else:
     self.fusedn5button_mainlayout.addLayout(self.n5button_sublayout7)  
           
    self.label_setcropRange_X=QLabel('Set crop size in X')
    self.label_setcropRange_X.setFont(QFont('times',9))
    self.label_setcropRange_X.adjustSize()
    self.x_spinbox = QSpinBox()
    self.x_spinbox.setRange(1,self.img_stack.shape[1])
    self.x_spinbox.setValue(256)
    self.x_spinbox.setFont(QFont('times',9))

    self.label_setcropRange_Y=QLabel('Set crop size in Y')
    self.label_setcropRange_Y.setFont(QFont('times',9))  
    self.label_setcropRange_Y.adjustSize()      
    self.y_spinbox = QSpinBox()
    self.y_spinbox.setRange(1,self.img_stack.shape[0])
    self.y_spinbox.setValue(256)
    self.y_spinbox.setFont(QFont('times',9))

    self.label_setcropRange_Z=QLabel('Set crop stack size')
    self.label_setcropRange_Z.setFont(QFont('times',9))  
    self.label_setcropRange_Z.adjustSize()     
    self.z_spinbox = QSpinBox()
    self.z_spinbox.setRange(1,1000)
    self.z_spinbox.setValue(64)
    self.z_spinbox.setFont(QFont('times',9))
    self.n5button_sublayout7.addWidget(self.label_setcropRange_X)
    self.n5button_sublayout7.addWidget(self.x_spinbox)
    self.n5button_sublayout7.addWidget(self.label_setcropRange_Y)
    self.n5button_sublayout7.addWidget(self.y_spinbox)
    self.n5button_sublayout7.addWidget(self.label_setcropRange_Z)
    self.n5button_sublayout7.addWidget(self.z_spinbox)
    
    self.pushButton_select_cropROI=QPushButton("Select crop ROI",self)
    self.pushButton_select_cropROI.adjustSize()
    self.pushButton_select_cropROI.setFont(QFont('times',9))  
    self.n5button_sublayout7.addWidget(self.pushButton_select_cropROI)
    self.pushButton_select_cropROI.clicked.connect(self.selecting_Crop_ROI)
    self.n5button_sublayout7.setSpacing(10)

 def randomstackdisplay(self):
    #f= z5py.File(self.folderpath, "r") 
    f = zarr.open(self.folderpath, mode='r')
    self.data = f[f"{self.setupid}/timepoint0/{self.Selected_DownsampleID}"] 
    self.datalength=len(self.data)
    # Set the text to be displayed
    self.RandomStack_qline.setText(str(random.randint(0, len(self.data))))
    self.RandomStack_qline.setFont(QFont('times',9)) 
    self.RandomStack_qline.show()
    self.stack = int(self.RandomStack_qline.text())
    print(self.datalength,self.RandomStack_qline.text())
 
 def show_stack_in_napari(self):
    if not hasattr(self, 'data'):
      f = zarr.open(self.folderpath, mode='r')
      self.data = f[f"{self.setupid}/timepoint0/{self.Selected_DownsampleID}"] 
      self.datalength=len(self.data)
      self.stack = int(self.RandomStack_qline.text())
    #if not hasattr(self, 'image_added')
    print(self.datalength,self.RandomStack_qline.text())
    self.stack = int(self.RandomStack_qline.text())
    self.img_stack=self.data[self.stack]
    self.napari_viewer.add_image(self.img_stack, name=f'random stack {self.stack}',  contrast_limits=[0, 2000],)
    self.image_added = True 
   


 def selecting_Crop_ROI (self):
    self.shape_rect = np.array([[0, self.x_spinbox.value()], [self.y_spinbox.value(),self.x_spinbox.value()], [self.y_spinbox.value(),0], [0,0]])
    self.shapes_layer = self.napari_viewer.add_shapes(self.shape_rect,name='Shapes', shape_type='rectangle', edge_width=1,edge_color='coral')
    if hasattr(self, 'n5button_sublayout8'):
     self.clear_layout(self.n5button_sublayout8)   
    if hasattr(self, 'n5button_sublayout9'):
     self.clear_layout(self.n5button_sublayout9)
    if hasattr(self, 'n5button_sublayout10'):
     self.clear_layout(self.n5button_sublayout10)   

    self.n5button_sublayout8=QHBoxLayout()   
    if hasattr(self, 'tiledn5button_mainlayout'):
      self.tiledn5button_mainlayout.addLayout(self.n5button_sublayout8)
    else:
      self.fusedn5button_mainlayout.addLayout(self.n5button_sublayout8) 

    self.pushButton_outputdir=QPushButton("Select output Folder",self)
    self.pushButton_outputdir.adjustSize()
    self.pushButton_outputdir.setFont(QFont('times',9))  
    self.n5button_sublayout8.addWidget(self.pushButton_outputdir)
    self.pushButton_outputdir.clicked.connect(self.outputdir_func)  

 def outputdir_func(self):
    self.outputdir =PyQt5.QtWidgets.QFileDialog.getExistingDirectory(self, "Select output folder","D:\\Stardist", QFileDialog.ShowDirsOnly)
    print(self.outputdir)
    self.slashidx = [n for (n, e) in enumerate(self.outputdir) if e == '/']
    self.labelOutputdir = QLabel(f"Output Path=   ../../... {self.outputdir[self.slashidx[-2]:]}/", self)
    self.labelOutputdir.setFont(QFont('times',10))     
    self.n5button_sublayout8.addWidget(self.labelOutputdir)
    if hasattr(self, 'n5button_sublayout9'):
     self.clear_layout(self.n5button_sublayout9)
    if hasattr(self, 'n5button_sublayout10'):
     self.clear_layout(self.n5button_sublayout10) 

    self.n5button_sublayout9=QHBoxLayout()   
    if hasattr(self, 'tiledn5button_mainlayout'):
     self.tiledn5button_mainlayout.addLayout(self.n5button_sublayout9)
    else:
     self.fusedn5button_mainlayout.addLayout(self.n5button_sublayout9)  
   
    self.labelOutputFileName = QLabel("Output FileName: ", self)
    self.labelOutputFileName.setFont(QFont('times',10))     
    self.n5button_sublayout9.addWidget(self.labelOutputFileName)
    self.OutputfileName_qline= QLineEdit()
    self.OutputfileName_qline.setFont(QFont('times',9))  
    self.OutputfileName_qline.setMaxLength(30)    
    self.n5button_sublayout9.addWidget(self.OutputfileName_qline) 
    self.pushButton_crop=QPushButton("Crop",self)
    self.pushButton_crop.adjustSize()
    self.pushButton_crop.setFont(QFont('times',9))  
    self.n5button_sublayout9.addWidget(self.pushButton_crop)
    self.pushButton_crop.clicked.connect(self.Crop1)
    self.n5button_sublayout9.setSpacing(10)
    self.checkbox_otherchannels=QCheckBox("Crop other channels")
    self.n5button_sublayout9.addWidget(self.checkbox_otherchannels)
    self.checkbox_otherchannels.setFont(QFont('times',9)) 
    self.checkbox_otherchannels.clicked.connect(self.crop_from_other_channels_params)


 def Crop1(self):   
    print(self.napari_viewer.layers['Shapes'].data)
    self.crop_coordinates=self.napari_viewer.layers['Shapes'].data
    self.image_layer=self.napari_viewer.layers.selection
    self.crop_coordinates = np.concatenate(self.crop_coordinates, axis=0)
    self.image_layer_name=self.image_layer.active.name
    self.image_layer_data = self.image_layer.active.data
    self.image_layer_data = cv2.rectangle(self.image_layer_data, tuple(np.flip(self.crop_coordinates[3].astype(int))), tuple(np.flip(self.crop_coordinates[1].astype(int))), (255,255,255), 5) 
    #image = cv2.rectangle(image, start_point, end_point, color(in bgr), thickness(inpts)) 
    self.image_layer.active.data=self.image_layer_data
    self.image_layer.active.refresh()

    # Regular expression to find the stack number of the active image layer in napari
    pattern = r'\b(\d+)\b'  #this searches for the number blocks sandwiched between word blocks
    # Extracting the number using regular expression
    match = re.search(pattern, self.image_layer_name)
    # Converting the matched number to an integer
    if match:
      self.mid_of_crop_stack= int(match.group(1))
      print(self.mid_of_crop_stack)
    self.x1=self.crop_coordinates[3,1].astype(int)
    self.x2=self.crop_coordinates[1,1].astype(int)
    self.y1=self.crop_coordinates[3,0].astype(int)
    self.y2=self.crop_coordinates[1,0].astype(int)  
    self.z1=self.mid_of_crop_stack-int(self.z_spinbox.value()/2)  
    self.z2=self.mid_of_crop_stack+int(self.z_spinbox.value()/2)  
    if self.z1 <self.datalength:
      self.z1= self.mid_of_crop_stack
      self.z2= self.mid_of_crop_stack+int(self.z_spinbox.value())
    if self.z2>self.datalength:
      self.z1= self.mid_of_crop_stack-int(self.z_spinbox.value()) 
      self.z2= self.mid_of_crop_stack

    self.cropped_image=self.data[self.z1:self.z2,self.y1:self.y2,self.x1:self.x2]
    self.cropped_image_name=os.path.join(self.outputdir,self.OutputfileName_qline.text())  
    imageio.volsave(self.cropped_image_name,self.cropped_image)
    self.napari_viewer.add_image(self.cropped_image,name=f'{self.OutputfileName_qline.text()}')
    self.napari_viewer.layers.remove(self.shapes_layer)


 def crop_from_other_channels_params(self): 
     
    self.n5button_sublayout10=QVBoxLayout()   
    if hasattr(self, 'tiledn5button_mainlayout'):
     self.tiledn5button_mainlayout.addLayout(self.n5button_sublayout10)
    else:
     self.fusedn5button_mainlayout.addLayout(self.n5button_sublayout10)  
      
    self.n5button_sublayout10.setSpacing(10)
    self.group_box = QGroupBox("Channels", self)
    self.group_box.setFont(QFont('times',9)) 
    self.group_layout = QGridLayout()
    self.row=0
    self.check_button_ch_list=[]
    self.outputfileName_qline_list=[]
    # the loop to display checkboxes for channels
    self.num_channels= int(len(self.setupids) / int(self.No_of_Tiles))
    for self.ch in range (self.num_channels):
       if self.ch != self.ref_channel:
         # Create checkbox
         self.check_button_ch = QCheckBox(f"Channel {self.ch}", self)
         self.check_button_ch.setFont(QFont('times',9)) 
         self.group_layout.addWidget(self.check_button_ch,self.row,0)
         self.check_button_ch_list.append(self.check_button_ch)
        # Create QLabel for filename
         self.labelChFileName = QLabel("crop name: ")
         self.labelChFileName.setFont(QFont('times',9)) 
         self.group_layout.addWidget(self.labelChFileName,self.row,1)
         # Create QLineEdit for filename
         self.outputfileName_qline = QLineEdit(self)
         self.outputfileName_qline.setFont(QFont('times', 9))
         self.outputfileName_qline.setMaxLength(20)
         self.group_layout.addWidget(self.outputfileName_qline,self.row,2)
         self.outputfileName_qline_list.append(self.outputfileName_qline)
         self.row=self.row+1
         self.group_box.setLayout(self.group_layout)
         self.n5button_sublayout10.addWidget(self.group_box)
    self.pushbutton_crop_ch=QPushButton('Crop from these channels',self)
    self.n5button_sublayout10.addWidget(self.pushbutton_crop_ch)         
    self.pushbutton_crop_ch.setFont(QFont('times',9))
    self.pushbutton_crop_ch.clicked.connect(self.crop_from_other_channels)
         
 def crop_from_other_channels(self):
  for rb, le in zip(self.check_button_ch_list, self.outputfileName_qline_list):
    if rb.isChecked():
       channel_number = rb.text().split()[-1]
       crop_name = le.text()
       print(f"Channel {channel_number} is selected with crop name: {crop_name}")
       f = zarr.open(self.folderpath, mode='r')
       prefix, number = self.setupid.split("setup")
       self.ch_setupid = int(number) + (int(channel_number)* int(self.No_of_Tiles))
       self.chdata = f[f"setup{self.ch_setupid}/timepoint0/{self.Selected_DownsampleID}"] 
       self.cropped_ch_image=self.chdata[self.z1:self.z2,self.y1:self.y2,self.x1:self.x2]
       self.cropped_ch_image_name=os.path.join(self.outputdir,le.text())  
       imageio.volsave(self.cropped_ch_image_name,self.cropped_ch_image)
       #self.napari_viewer.add_image(self.cropped_image,name=f'{self.OutputfileName_qline.text()}')
       #self.napari_viewer.layers.remove(self.shapes_layer)
    msg = QMessageBox()
    msg.setText("Cropping done")
    msg.exec_()

 def fusedn5buttonclicked(self):
   self.folderpath = PyQt5.QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder of fused n5 data',"\\\\wfs-$$$$$$\\$$$$$$\\$$$\\", QFileDialog.ShowDirsOnly)
   print(self.folderpath)
   if hasattr(self, 'tiledn5button_mainlayout'):
     self.clear_layout(self.fusedn5button_mainlayout)   
   self.GetFusedN5Layout()



 def tiledn5buttonclicked(self):   
   self.folderpath = PyQt5.QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder of tiled n5 data","\\\\wfs-$$$$$$\\$$$$$$\\$$$\\", QFileDialog.ShowDirsOnly)
   
   if hasattr(self, 'tiledn5button_mainlayout'):
     self.clear_layout(self.tiledn5button_mainlayout)   
   self.GetTiledN5Layout()

   


def main():
   app = QApplication(sys.argv)
   window = Crop_n5()
   window.setGeometry(10, 50, 1300, 280)
   window.show()  
   sys.exit(app.exec_())

if __name__ == '__main__':
    main()