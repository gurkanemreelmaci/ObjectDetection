# arayüz kütüphanesi ve özellikleri ekleniyor

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.logger import Logger
#diğer kütüphaneler

import cv2
import tensorflow as tf
import tensorflow.python as tfpy 
from layers import L1Dist
import os
import numpy as np
import torch
import requests
from datetime import datetime
import urllib3
import time
# uygulama ve layoutlar oluşturuluyor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {'accept': 'text/plain','Content-Type': 'application/json'}
url = 'https://localhost:7262/api/ObjectDetection'

class CamApp(App):

    def build(self):
        # ana uygulama yapısı
        self.web_cam = Image(size_hint =(1,.8))
        self.button = Button(text = "Start",on_press=self.activate, size_hint=(1,.1))
        self.button1 = Button(text = "Stop",on_press=self.deactivate, size_hint=(1,.1))
        self.detection_status = Label(text ="Detection is not working",size_hint=(1,.1))

        # uygulama itemleri oluşturuluyor
        layout = BoxLayout(orientation = 'vertical')
        layout.add_widget(self.web_cam)
        layout.add_widget(self.button)
        layout.add_widget(self.button1)
        layout.add_widget(self.detection_status)

        self.activate_status = 0

        
        # model keras ile yükleniyor
        self.model = tf.keras.models.load_model('objecttracker_vgg19_1.h5')
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update,1.0/33.0)

        return layout

    def update(self,*args):

        #kamera üzerinden okuma yapılıyor
        ret, frame = self.capture.read()
        frame =frame[50:500, 50:500,:]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resized = tf.image.resize(rgb, (120,120))

        today = datetime.now()
        datetime.strftime(today, '%d/%B/%Y %X')
        
        if(self.activate_status):
            
            yhat = self.model.predict(np.expand_dims(resized/255,0))
            sample_coords = yhat[1][0]
            print(yhat[0])
            if yhat[0] > 0.9999: 
                cv2.rectangle(frame,tuple(np.multiply(sample_coords[:2],
                 [450,450]).astype(int)), 
                        tuple(np.multiply(sample_coords[2:], 
                        [450,450]).astype(int)),
                    (   255,0,0), 2)               
    
                # Nesne adı oluşturuluyor
                cv2.putText(frame, 'Yasakli Madde', tuple(np.add
                   (np.multiply(sample_coords[:2], [450,450]).astype(int),[0,-1])),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
                #api bağlantı ve veri gonderme aşaması
                params={"id":0,"objectName":"yasaklı madde" ,"description":"lab 1",
                     "type": "sıvı","date": str(today) }

                # r = requests.post(url = url, headers=headers, json = params,verify=False)
                # print(r.status_code)
                # print(r.json())
        #Flip
        buf = cv2.flip(frame,0).tostring()
        img_texture = Texture.create(size =(frame.shape[1],frame.shape[0]),colorfmt ='bgr')
        img_texture.blit_buffer(buf,colorfmt ='bgr', bufferfmt = 'ubyte')
        self.web_cam.texture = img_texture

        


        # resim  dosyadan alınıyor ve 100*100px olacak şekilde yeniden düzenleniyor
    def preprocess(self,file_path):
    
        byte_img = tf.io.read_file(file_path)
        img = tf.io.decode_jpeg(byte_img)

        img = tf.image.resize(img, (100,100))
        img = img / 255.0

        return img


    #eşleştirme fonksiyonu
    def deactivate(self,model):
        self.activate_status = 0
        self.detection_status.text = 'Detection is not working'

    def activate(self, model):
            self.activate_status = 1
            self.detection_status.text = 'Detection is working'



if __name__ == '__main__':
    CamApp().run()
