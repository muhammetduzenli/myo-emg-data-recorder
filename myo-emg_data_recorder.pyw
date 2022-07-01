#!/usr/bin/env python
#--coding:utf-8-*-

"""
  MIT License

  Copyright (c) 2022 muhammetduzenli

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
"""

from time import time
from collections import deque
from threading import Lock

import myo

import os

from tkinter import *
from tkinter import ttk

class Gui(object):
  def __init__(self):
    self.record = False
    self.record_label = 'default_label'
    self.record_file_name = 'default_file'
    self.start_time = 0
    self.record_time_start = 0
    self.record_time = 20
    self.acceleration_data = deque(maxlen=1)
    self.gyroscope_data = deque(maxlen=1)
    self.orientation_data = deque(maxlen=1)
    self.timestamp_data = deque(maxlen=1)
    self.emg_data = deque(maxlen=1)
    self.record_text = ''
    pass
  
  def gui_config(self):
      self.title = self.mainWin.title("Myo Armband Emg Data Recorder")
      self.mainWin.geometry("400x200")
      self.mainWin.resizable(width = FALSE, height= FALSE)
      self.appWin = ttk.Frame(self.mainWin)
      pass
  
  def gui_widgets(self):

      # Record file name entry
      self.file_var = StringVar()
      self.file_var.trace('w',lambda name, index, mode, sv=self.file_var:self.set_file_name(self.file_var))
      self.entry_record_file = ttk.Entry(master=self.appWin, textvariable=self.file_var)
      self.entry_record_file.insert(0,'file-name')
      self.entry_record_file.grid(row=0,column=0,pady=10)
      self.entry_record_file.focus()

      # Record label name entry
      self.label_var = StringVar()
      self.label_var.trace('w',lambda name, index, mode, sv=self.label_var:self.set_label_name(self.label_var))
      self.entry_record_label = ttk.Entry(master=self.appWin, textvariable=self.label_var)
      self.entry_record_label.insert(0,'label-name')
      self.entry_record_label.grid(row=0,column=1,pady=10)

      # Record time slider
      self.record_time_slider = ttk.Scale(master=self.appWin,from_=1,to=100,value=20,command=self.slider_value_changed)
      self.record_time_slider.grid(row=1,column=0)

      # Record slider value text
      self.record_time_slider_text = ttk.Label(master=self.appWin, text="Record Time: 20s", foreground='black')
      self.record_time_slider_text.grid(row=1,column=1)

      # Myo Record Button
      self.button_myo_record_data = ttk.Button(text="Start Record", master=self.appWin, command=self.start_record_data) #show_emg_data #start_reading_emg_sensors
      self.button_myo_record_data.grid(row=3,column=0)

      # Myo Stop Record Button
      self.button_myo_data_record_stop = ttk.Button(text="Stop Record", master=self.appWin, command=self.stop_record_data, state=DISABLED)
      self.button_myo_data_record_stop.grid(row=4,column=0)

      # Record Options Checkbox
      self.a_cb_var = BooleanVar(False)
      self.checkbox_myo_acceleration = ttk.Checkbutton(text="Acceleration", master=self.appWin, onvalue=True, offvalue=False, width=20, variable=self.a_cb_var)
      self.checkbox_myo_acceleration.grid(row=3,column=1)

      self.g_cb_var = BooleanVar(False)
      self.checkbox_myo_gyroscope = ttk.Checkbutton(text="Gyroscope", master=self.appWin, onvalue=True, offvalue=False, width=20, variable=self.g_cb_var)
      self.checkbox_myo_gyroscope.grid(row=4,column=1)

      self.o_cb_var = BooleanVar(False)
      self.checkbox_myo_orientation = ttk.Checkbutton(text="Orientation", master=self.appWin, onvalue=True, offvalue=False, width=20, variable=self.o_cb_var)
      self.checkbox_myo_orientation.grid(row=5,column=1)

      # Record Status Label
      self.label_myo_record_status = ttk.Label(text="", master=self.appWin, foreground='black')
      self.label_myo_record_status.grid(row=6, columnspan=1)
    
      self.appWin.pack()

      pass

  def slider_value_changed(self,event):
    self.record_time = int(self.record_time_slider.get())
    self.record_time_slider_text.config(text= "Record Time: " + str(self.record_time) + "s")
    pass

  def set_file_name(self,sv):
    self.record_file_name = sv.get()
  
  def set_label_name(self,sv):
    self.record_label = sv.get()

  def record_data(self):
    if self.record:
      dif_time = time() - self.record_time_start
      if  dif_time < self.record_time:
        record_time = str(int(dif_time*1000))
        self.label_myo_record_status.config(text= str(int(dif_time*1000)) + "ms - Recording...", foreground= 'green')
        sensor_data = ''
        for i in range (8):
          sensor_data = sensor_data + ',' + str(self.emg_data[0][i])

        acceleration_data = ''
        if self.a_cb_var.get():
          acceleration_data = ','
          acceleration_data  = acceleration_data + str(self.acceleration_data[0]).split('(')[1].split(')')[0].replace(' ','')
        
        gyroscope_data = ''
        if self.g_cb_var.get():
          gyroscope_data = ','
          gyroscope_data = gyroscope_data + str(self.gyroscope_data[0]).split('(')[1].split(')')[0].replace(' ','')

        orientation_data = ''
        if self.o_cb_var.get():
          orientation_data = ','
          orientation_data = orientation_data + str(self.orientation_data[0]).split('(')[1].split(')')[0].replace(' ','')

        label = ',' + self.record_label + '\n'
        try:
          self.record_file.write(record_time + sensor_data + acceleration_data + gyroscope_data + orientation_data + label)
        except Exception:
          pass
        #print(record_time + sensor_data + acceleration_data + gyroscope_data + orientation_data + label)
      else:
        self.label_myo_record_status.config(text= "Recording done.", foreground='black')
        self.button_myo_record_data.state(["!disabled"])
        self.button_myo_data_record_stop.state(['disabled'])
        self.record = False
        self.record_file.close()
  
  def start_record_data(self):
    self.record_file = open( os.path.dirname(__file__) + '\\' + str(self.record_file_name) + '.csv','w')
    record_headers = 'timestamp,sensor1,sensor2,sensor3,sensor4,sensor5,sensor6,sensor7,sensor8'
    if self.a_cb_var.get():
      record_headers = record_headers + ',acc_x,acc_y,acc_z'
    if self.g_cb_var.get():
      record_headers = record_headers + ',gyro_x,gyro_y,gyro_z'
    if self.o_cb_var.get():
      record_headers = record_headers + ',ori_x,ori_y,ori_z,ori_w'
    
    record_headers = record_headers + ',label\n'

    self.record_file.write(record_headers)
    self.record = True
    self.button_myo_record_data.state(["disabled"])
    self.button_myo_data_record_stop.state(["!disabled"])
    self.record_time_start = time()
    pass

  def stop_record_data(self):
    self.button_myo_record_data.state(["!disabled"])
    self.button_myo_data_record_stop.state(['disabled'])
    self.label_myo_record_status.config(text= "Recording done.", foreground='black')
    self.record = False
    self.record_file.close()
    pass

  def main(self):
    self.mainWin = Tk()
    self.gui_config()
    self.gui_widgets()

class EmgCollector(myo.DeviceListener):
  
  def __init__(self, n):
    self.n = n
    self.lock = Lock()
    self.start_time = 0
    self.app = Gui()

  def get_emg_data(self):
    with self.lock:
      return list(self.emg_data_queue)

  def on_connected(self, event):
    print("Myo connected...")
    self.app.label_myo_record_status.config(text="Myo Armband Status: Connected",foreground= 'green')
    self.myo_status = True
    event.device.stream_emg(True)

  def on_disconnected(self, event):
    print("Myo disconnected...")
    self.app.label_myo_record_status.config(text="Myo Armband Status: Disconnected",foreground= 'red')
    self.myo_status = False

  def on_emg(self, event):
    with self.lock:
      if self.start_time == 0:
        self.start_time = event.timestamp
        self.app.start_time = self.start_time
      
      self.app.timestamp_data.append(int((event.timestamp - self.start_time)/1000))
      self.app.emg_data.append(event.emg)

      self.app.record_text = str(self.app.timestamp_data[0]) + " " + str(event.emg)

      if self.app.a_cb_var.get():
        self.app.record_text = self.app.record_text + " " + str(self.app.acceleration_data[0])

      if self.app.g_cb_var.get():
        self.app.record_text = self.app.record_text + " " + str(self.app.gyroscope_data[0])

      if self.app.o_cb_var.get():
        self.app.record_text = self.app.record_text + " " + str(self.app.orientation_data[0])

      self.app.record_text = self.app.record_text + " " + self.app.record_label

      #print(self.app.record_text)
      self.app.record_data()
  
  def on_orientation(self, event):
    with self.lock:
      self.app.acceleration_data.append(str(event.acceleration))
      self.app.gyroscope_data.append(str(event.gyroscope))
      self.app.orientation_data.append(str(event.orientation)) 
  
  def main(self):
    self.app.main()
    myo.init(sdk_path= os.path.dirname(__file__) + '\\myo-sdk-win-0.9.0')
    hub = myo.Hub()
    with hub.run_in_background(self.on_event):
      mainloop()
      
def main():
    listener = EmgCollector(1)
    listener.main()


if __name__ == '__main__':
    main()