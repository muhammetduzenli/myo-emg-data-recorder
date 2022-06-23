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
    self.sensorGraphs = []
    self.emg_data = []
    self.timestamp_array = []
    self.sensors_arrays = [[],[],[],[],[],[],[],[]]
    self.record = False
    self.record_label = 'default_label'
    self.record_file_name = 'default_file'
    self.start_time = 0
    self.record_time_start = 0
    self.record_time = 2
    pass
  
  def gui_config(self):
      self.title = self.mainWin.title("Myo Armband Emg Data Recorder")
      self.mainWin.geometry("400x100")
      self.mainWin.resizable(width = FALSE, height= FALSE)
      self.appWin = ttk.Frame(self.mainWin)
      pass
  
  def gui_widgets(self):

      # Record file name entry
      self.entry_record_file = ttk.Entry(master=self.appWin)
      self.entry_record_file.insert(0,'file-name')
      self.entry_record_file.grid(row=0,column=0,pady=10)
      self.entry_record_file.focus()

      # Record label name entry
      self.entry_record_label = ttk.Entry(master=self.appWin)
      self.entry_record_label.insert(0,'label-name')
      self.entry_record_label.grid(row=0,column=1,pady=10)

      # Record time slider
      self.record_time_slider = ttk.Scale(master=self.appWin,from_=1,to=100,value=20,command=self.slider_value_changed)
      self.record_time_slider.grid(row=1,column=0)

      # Record slider value text
      self.record_time_slider_text = ttk.Label(master=self.appWin, text="Record Time: 20s", foreground='black')
      self.record_time_slider_text.grid(row=1,column=1)

      # Myo Emg Read Button
      self.button_myo_emg_recording = ttk.Button(text="Start Recording", master=self.appWin, command=self.record_emg_data) #show_emg_data #start_reading_emg_sensors
      self.button_myo_emg_recording.grid(row=2,column=0)

      # Record Status Label
      self.label_myo_record_status = ttk.Label(text="", master=self.appWin, foreground='black')
      self.label_myo_record_status.grid(row=2,column=1)
    
      self.appWin.pack()

      pass

  def slider_value_changed(self,event):
    self.record_time = int(self.record_time_slider.get())
    self.record_time_slider_text.config(text= "Record Time: " + str(self.record_time) + "s")
    pass

  def set_emg_data(self, emg_data):

    self.emg_data = emg_data
    if self.record:
      dif_time = time() - self.record_time_start
      if  dif_time < self.record_time:
        record_time = str(int(dif_time*1000))
        sensor_data = ''
      
        for i in range (8):
          sensor_data = sensor_data + ',' + str(self.emg_data[0][1][i])
        
        label = ',' + str(self.emg_data[0][2]) + '\n'

        self.label_myo_record_status.config(text= str(int(dif_time*1000)) + "ms - Recording...")
        #print(str(int(dif_time*1000)) + " - Kayıt devam ediyor...")
        self.record_file.write(record_time + sensor_data + label)
      else:
        self.label_myo_record_status.config(text= "Recording done.")
        self.button_myo_emg_recording.state(["!disabled"])
        self.record = False
        self.record_file.close()
  def record_emg_data(self):
    self.record_file = open( os.path.dirname(__file__) + '\\' + str(self.record_file_name) + '.csv','w')
    self.record_file.write('timestamp,sensor1,sensor2,sensor3,sensor4,sensor5,sensor6,sensor7,sensor8,label\n')
    self.record = True
    self.button_myo_emg_recording.state(["disabled"])
    self.record_time_start = time()
    pass

  def main(self):
    self.mainWin = Tk()
    self.gui_config()
    self.gui_widgets()

class EmgCollector(myo.DeviceListener):
  
  def __init__(self, n):
    self.n = n
    self.lock = Lock()
    self.emg_data_queue = deque(maxlen=n)
    self.start_time = 0
    self.app = Gui()

  def get_emg_data(self):
    with self.lock:
      return list(self.emg_data_queue)

  def on_connected(self, event):
    print("Myo connected...")
    self.app.label_myo_status.config(text="Myo Armband Status: Connected",foreground= 'green')
    self.myo_status = True
    event.device.stream_emg(True)

  def on_disconnected(self, event):
    print("Myo disconnected...")
    self.app.label_myo_status.config(text="Myo Armband Status: Disconnected",foreground= 'red')
    self.myo_status = False

  def on_emg(self, event):
    with self.lock:
      if self.start_time == 0:
        self.start_time = event.timestamp
        self.app.start_time = self.start_time
      self.emg_data_queue.append((event.timestamp,event.emg,self.app.record_label))
      self.app.set_emg_data(list(self.emg_data_queue))
  
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