"""
Model utilities for image de-raining
Extracted from the original training code
"""
import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import cv2

def to_frequency_domain(img_tensor, mode='real_imag'):
    """Convert image to frequency domain using FFT"""
    img_tensor = tf.cast(img_tensor, tf.complex64)
    fft = tf.signal.fft2d(tf.transpose(img_tensor, perm=[2, 0, 1]))
    real = tf.math.real(fft)
    imag = tf.math.imag(fft)
    if mode == 'real_imag':
        return tf.stack([real, imag], axis=-1)
    elif mode == 'mag_phase':
        mag = tf.math.sqrt(real**2 + imag**2)
        phase = tf.math.atan2(imag, real)
        return tf.stack([mag, phase], axis=-1)
    else:
        raise ValueError("Mode must be 'real_imag' or 'mag_phase'")

def from_frequency_domain(freq_tensor):
    """Convert from frequency domain back to image using IFFT"""
    h, w, c, _ = freq_tensor.shape
    freq_tensor = tf.transpose(freq_tensor, perm=[2, 0, 1, 3])
    real = freq_tensor[..., 0]
    imag = freq_tensor[..., 1]
    complex_tensor = tf.complex(real, imag)
    ifft = tf.signal.ifft2d(complex_tensor)
    ifft = tf.math.real(ifft)
    ifft = tf.transpose(ifft, perm=[1, 2, 0])
    return tf.clip_by_value(ifft, 0.0, 1.0)

def build_dnet(input_shape=(256, 256, 6)):
    """Build D-Net architecture"""
    inputs = tf.keras.Input(shape=input_shape)
    x = layers.Conv2D(64, 3, padding='same', activation='relu')(inputs)
    x = layers.Conv2D(128, 3, padding='same', activation='relu')(x)
    x = layers.Conv2D(256, 3, padding='same', activation='relu')(x)
    return models.Model(inputs, x, name='DNet')

def build_nnet(input_shape=(256, 256, 256)):
    """Build N-Net architecture"""
    inputs = tf.keras.Input(shape=input_shape)
    x = layers.Conv2D(128, 3, padding='same', activation='relu')(inputs)
    x = layers.Conv2D(64, 3, padding='same', activation='relu')(x)
    x = layers.Conv2D(3, 3, padding='same', activation='sigmoid')(x)
    return models.Model(inputs, x, name='NNet')

def build_derain_model():
    """Build the complete de-raining model"""
    input_freq = tf.keras.Input(shape=(256, 256, 6))
    dnet = build_dnet()
    nnet = build_nnet()
    features = dnet(input_freq)
    rain_map = nnet(features)
    return models.Model(inputs=input_freq, outputs=rain_map, name='DerainModel')

def sharpen_image(img):
    """Apply sharpening filter to image"""
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    img_uint8 = np.uint8(np.clip(img * 255, 0, 255))
    sharp = cv2.filter2D(img_uint8, -1, kernel)
    return np.clip(sharp / 255.0, 0, 1)

def enhance_output_image(img):
    """Enhance output image using CLAHE"""
    gamma = 1.1
    img_gamma = np.power(img, 1.0 / gamma)
    img_uint8 = np.uint8(np.clip(img_gamma * 255, 0, 255))
    lab = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    lab_clahe = cv2.merge([cl, a, b])
    final = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2RGB)
    return np.clip(final / 255.0, 0, 1)

