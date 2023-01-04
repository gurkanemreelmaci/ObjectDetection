# Genel kütüphaneler ekleniyor
import cv2
import os
import random
import numpy as np
from matplotlib import pyplot as p

#  Tensorflow kütüphanesi ekleniyor
import tensorflow as tf

# resimlere benzersiz ad vermek için kullanılacak kütüphane ekleniyor
import uuid



# Veriler üzerinde işlem yapmada kullanılacak dosya yolları belirleniyor 
POS_PATH = os.path.join('data', 'positive')
NEG_PATH = os.path.join('data', 'negative')
ANC_PATH = os.path.join('data', 'anchor')

# dosyalar eğer oluşrurulmamaış ise oluşturuluyor
try:
    os.makedirs(POS_PATH)
except FileExistsError:
    print('dosya zaten var')

try:
    os.makedirs(NEG_PATH)
except FileExistsError:
    print('dosya zaten var')

try:
    os.makedirs(ANC_PATH)
except FileExistsError:
    print('dosya zaten var')



cap = cv2.VideoCapture(0)
while cap.isOpened(): 
    ret, frame = cap.read()
   
    # kamera ekran boyutu 250x250px olacak şekilde ayarlanıyor
    frame = frame[120:120+250,200:200+250, :]
    
    # eşleştirme amacıyla kullanılacak resimler alınıyor(anchor) 
    if cv2.waitKey(1) & 0XFF == ord('a'):
        # alınan resimlere benzersiz adlar oluşturuluyor
        imgname = os.path.join(ANC_PATH, '{}.jpg'.format(uuid.uuid1()))
        # kamera üzerinden veri okunuyor ve dosyaya kaydediiliyor
        cv2.imwrite(imgname, frame)
    
    # Collect positives
    if cv2.waitKey(1) & 0XFF == ord('p'):
        # Create the unique file path 
        imgname = os.path.join(POS_PATH, '{}.jpg'.format(uuid.uuid1()))
        # Write out positive image
        cv2.imwrite(imgname, frame)
    
    # Show image back to screen
    cv2.imshow('Image Collection', frame)
    
    # Breaking gracefully
    if cv2.waitKey(1) & 0XFF == ord('q'):
        break
        
# Release the webcam
cap.release()
# Close the image show frame
cv2.destroyAllWindows()

