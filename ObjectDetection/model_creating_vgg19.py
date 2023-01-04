# Genel kütüphaneler ekleniyor
import cv2
import os
import random
import numpy as np
from matplotlib import pyplot as p
import file_operations as fp
import image_operation as ip
#  Tensorflow kütüphanesi ekleniyor
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, Dense, GlobalMaxPooling2D
from tensorflow.keras.applications import VGG19
from tensorflow.keras.models import load_model

from tensorflow.keras.layers import Layer, Conv2D, Dense, MaxPooling2D, Input, Flatten
import tensorflow as tf

# model eğitim işlemini yapacağımız class oluşturuluyor
class ObjectTracker(Model): 
    def __init__(self, tracker,  **kwargs): 
        super().__init__(**kwargs)
        self.model = tracker

    def compile(self, opt, classloss, localizationloss, accuracy, **kwargs):
        super().compile(**kwargs)
        self.closs = classloss
        self.lloss = localizationloss
        self.opt = opt
        self.accuracy = accuracy

    
    def train_step(self, batch, **kwargs): 
        
        X, y = batch
        
        with tf.GradientTape() as tape: 
            classes, coords = self.model(X, training=True)
            
            batch_classloss = self.closs(y[0], classes)
            batch_localizationloss = self.lloss(tf.cast(y[1], tf.float32), coords)
            batch_caccuracy = self.accuracy(y[0],classes)
            batch_laccuracy = self.accuracy(tf.cast(y[1], tf.float32), coords)
            total_loss = batch_localizationloss+0.5*batch_classloss
            total_accuracy = batch_caccuracy+batch_laccuracy
            
            grad = tape.gradient(total_loss, self.model.trainable_variables)
        
        opt.apply_gradients(zip(grad, self.model.trainable_variables))
        
        return {"total_loss":total_loss, "class_loss":batch_classloss, 
        "regress_loss":batch_localizationloss,"total_accuracy":total_accuracy}
    
    def test_step(self, batch, **kwargs): 
        X, y = batch
        
        classes, coords = self.model(X, training=False)
        
        batch_classloss = self.closs(y[0], classes)
        batch_localizationloss = self.lloss(tf.cast(y[1], tf.float32), coords)
        total_loss = batch_localizationloss+0.5*batch_classloss
        
        return {"total_loss":total_loss, "class_loss":batch_classloss, "regress_loss":batch_localizationloss}
        
    def call(self, X, **kwargs): 
        return self.model(X, **kwargs)

# modelin oluşturulduğu fonksiyon oluşturluyor
def build_model(): 
    input_layer = Input(shape=(120,120,3))
    
    vgg = VGG19(include_top=False)(input_layer)

    # Temel tanımlama eşlemesi 
    f1 = GlobalMaxPooling2D()(vgg)
    class1 = Dense(2048, activation='relu')(f1)
    class2 = Dense(1, activation='sigmoid')(class1)
    
    # kordinat eşlemesi
    f2 = GlobalMaxPooling2D()(vgg)
    regress1 = Dense(2048, activation='relu')(f2)
    regress2 = Dense(4, activation='sigmoid')(regress1)
    
    objecttracker = Model(inputs=input_layer, outputs=[class2, regress2])
    return objecttracker


# cordinat üzerinde kayıp hesaplayan fonksiyon
def localization_loss(y_true, yhat):            
    delta_coord = tf.reduce_sum(tf.square(y_true[:,:2] - yhat[:,:2]))
                  
    h_true = y_true[:,3] - y_true[:,1] 
    w_true = y_true[:,2] - y_true[:,0] 

    h_pred = yhat[:,3] - yhat[:,1] 
    w_pred = yhat[:,2] - yhat[:,0] 
    
    delta_size = tf.reduce_sum(tf.square(w_true - w_pred) + tf.square(h_true-h_pred))
    
    return (delta_coord + delta_size)/1



# uygulama gpu da çalışmak için ayarlanıyor
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus: 
    tf.config.experimental.set_memory_growth(gpu, True)

fp.move_label_file()

augmentor = ip.prepare_albumentations()
ip.run_albumentations(augmentor)

# veri seti dosya üzerinden okunuyor ve hazırlanıyor
train_images = tf.data.Dataset.list_files('aug_data\\train\\images\\*.jpg',
 shuffle=False)
train_images = train_images.map(fp.load_image)
train_images = train_images.map(lambda x: tf.image.resize(x, (120,120)))
train_images = train_images.map(lambda x: x/255)

test_images = tf.data.Dataset.list_files('aug_data\\test\\images\\*.jpg', shuffle=False)
test_images = test_images.map(fp.load_image)
test_images = test_images.map(lambda x: tf.image.resize(x, (120,120)))
test_images = test_images.map(lambda x: x/255)

val_images = tf.data.Dataset.list_files('aug_data\\val\\images\\*.jpg', shuffle=False)
val_images = val_images.map(fp.load_image)
val_images = val_images.map(lambda x: tf.image.resize(x, (120,120)))
val_images = val_images.map(lambda x: x/255)

# veri seti üzerinde tanımlanacak nesnelerin konumlarını bulunduran 'label' yapısı json formatından okunuyor ve oluşturuluyor

train_labels = tf.data.Dataset.list_files('aug_data\\train\\labels\\*.json',
 shuffle=False)
train_labels = train_labels.map(lambda x: tf.py_function(fp.load_labels, [x],
 [tf.uint8, tf.float16]))

test_labels = tf.data.Dataset.list_files('aug_data\\test\\labels\\*.json', shuffle=False)
test_labels = test_labels.map(lambda x: tf.py_function(fp.load_labels, [x], [tf.uint8, tf.float16]))

val_labels = tf.data.Dataset.list_files('aug_data\\val\\labels\\*.json', shuffle=False)
val_labels = val_labels.map(lambda x: tf.py_function(fp.load_labels, [x], [tf.uint8, tf.float16]))

# veri setinin veriler ve labellardan oluşan son hali oluşturuluyor

train = tf.data.Dataset.zip((train_images, train_labels))
train = train.shuffle(5000)
train = train.batch(8)
train = train.prefetch(4)

test = tf.data.Dataset.zip((test_images, test_labels))
test = test.shuffle(1300)
test = test.batch(8)
test = test.prefetch(4)

val = tf.data.Dataset.zip((val_images, val_labels))
val = val.shuffle(1000)
val = val.batch(8)
val = val.prefetch(4)

# egitimde kullanılacak model oluşturuluyor
vgg = VGG19(include_top=False)
objecttracker = build_model()

# eğitimde kullanılacak optimizasyon ve kayıp 'loss' degerleri oluşturuluyor

batches_per_epoch = len(train)
lr_decay = (1./0.75 -1)/batches_per_epoch
opt = tf.keras.optimizers.Adam(learning_rate=0.0001, decay=lr_decay)

classloss = tf.keras.losses.CategoricalCrossentropy()
regressloss = localization_loss

model = ObjectTracker(objecttracker)

model.compile(opt, classloss, regressloss, tf.keras.metrics.Accuracy())

logdir='logs_vgg19'

tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=logdir)

hist = model.fit(train, epochs=10, validation_data=val, callbacks=[tensorboard_callback])

objecttracker.save('objecttracker_vgg19.h5')

