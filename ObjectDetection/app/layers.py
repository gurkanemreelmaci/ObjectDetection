# özel olarak oluşturduğumuz layer katmanı


# kütüphanel ekleniyor

import tensorflow as tf
from tensorflow.python.keras.layers import Layer

# model için oluşturduğumuz l1 distance katmanı oluştururuluyor

class L1Dist(Layer):
    
    # Init method - inheritance
    def __init__(self, **kwargs):
        super().__init__()
       
    # Magic happens here - similarity calculation
    def call(self, input_embedding, validation_embedding):
        return tf.math.abs(input_embedding - validation_embedding)


