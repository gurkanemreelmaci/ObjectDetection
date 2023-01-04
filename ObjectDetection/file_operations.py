import os
import time
import uuid
import cv2
import labelme
import tensorflow as tf
import json

def take_image():
    IMAGES_PATH = os.path.join('data', 'images')
    cap = cv2.VideoCapture(0)
    while (1):
        ret, frame = cap.read()
        imgname = os.path.join(IMAGES_PATH,f'{str(uuid.uuid1())}.jpg')
        if cv2.waitKey(1) & 0xFF == ord('t'):
            cv2.imwrite(imgname, frame)
            print('Collecting image ')
            time.sleep(0.5)
        cv2.imshow('frame', frame)
    
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def image_label():
    os.system('labelme')

def move_image(image_number,file_name):
    for folder in file_name:
        for file in os.listdir(os.path.join('data', folder)):
            print(file)

def move_label_file():
    for folder in ['train','test','val']:
        for file in os.listdir(os.path.join('data', folder, 'images')):
            
            filename = file.split('.')[0]+'.json'
            existing_filepath = os.path.join('data','labels', filename)
            if os.path.exists(existing_filepath): 
                new_filepath = os.path.join('data',folder,'labels',filename)
                print(new_filepath)
                os.replace(existing_filepath, new_filepath)      

def load_image(x): 
    byte_img = tf.io.read_file(x)
    img = tf.io.decode_jpeg(byte_img)
    return img

def load_labels(label_path):
    with open(label_path.numpy(), 'r', encoding = "utf-8") as f:
        label = json.load(f)
        
    return [label['class']], label['bbox']


#image_label()