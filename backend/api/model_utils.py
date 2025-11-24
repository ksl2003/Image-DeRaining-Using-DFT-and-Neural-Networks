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

def blend_luminance_with_original_colors(original_img, derained_img):
    """
    Combine the luminance (Y) from the de-rained image with the 
    chrominance (UV) from the original image.
    Applies Bilateral Filter to remove noise/grain.
    Strictly preserves original image brightness.
    
    Args:
        original_img: Original rainy image (numpy array, 0-1 float or 0-255 uint8)
        derained_img: De-rained image (numpy array, 0-1 float)
    Returns:
        Final image (numpy array, 0-1 float)
    """
    # Ensure inputs are uint8 for OpenCV conversion
    if original_img.dtype != np.uint8:
        orig = np.uint8(np.clip(original_img * 255, 0, 255))
    else:
        orig = original_img
        
    if derained_img.dtype != np.uint8:
        derained = np.uint8(np.clip(derained_img * 255, 0, 255))
    else:
        derained = derained_img

    # Convert to YUV color space
    orig_yuv = cv2.cvtColor(orig, cv2.COLOR_RGB2YUV)
    derained_yuv = cv2.cvtColor(derained, cv2.COLOR_RGB2YUV)

    # Split channels
    y_orig, u_orig, v_orig = cv2.split(orig_yuv)
    y_derained, u_derained, v_derained = cv2.split(derained_yuv)

    # 1. Use Y channel from de-rained image
    final_y = y_derained

    # 2. Apply Bilateral Filter to remove noise/grain while preserving edges
    # d=5: Diameter of each pixel neighborhood
    # sigmaColor=75: Filter sigma in the color space
    # sigmaSpace=75: Filter sigma in the coordinate space
    final_y = cv2.bilateralFilter(final_y, 5, 75, 75)

    # 3. Match Brightness strictly to Original Image
    mean_y_orig = np.mean(y_orig)
    mean_y_final = np.mean(final_y)
    diff = mean_y_orig - mean_y_final
    
    # Add difference (using float to avoid overflow)
    final_y = final_y.astype(np.float32) + diff
    final_y = np.clip(final_y, 0, 255).astype(np.uint8)

    # 4. Use U and V channels from ORIGINAL image
    final_u = u_orig
    final_v = v_orig

    # Merge channels
    final_yuv = cv2.merge([final_y, final_u, final_v])

    # Convert back to RGB
    final_rgb = cv2.cvtColor(final_yuv, cv2.COLOR_YUV2RGB)
    
    return np.clip(final_rgb / 255.0, 0, 1)

