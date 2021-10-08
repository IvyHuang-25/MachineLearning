# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 11:32:28 2021

@author: IvyHuang
"""

import numpy as np
import os
import pandas as pd
from scipy import signal

def bandpass_filter(data, low_freq=0.5, high_freq=42, sample_freq=160):
    Wn1 = 2 * low_freq / sample_freq
    Wn2 = 2 * high_freq / sample_freq
    b, a = signal.butter(8, [Wn1, Wn2], 'bandpass')
    filted_data = signal.filtfilt(b, a, data)
    
    return filted_data

def pre_process(origin_data):
    # 带通滤波
    bandpass_data = bandpass_filter(origin_data, low_freq=0.5, high_freq=42, sample_freq=160)
    
     # 分频带
    delta_data = bandpass_filter(bandpass_data, low_freq=0.5, high_freq=4)
    theta_data = bandpass_filter(bandpass_data, low_freq=4, high_freq=8)
    alpha_data = bandpass_filter(bandpass_data, low_freq=8, high_freq=13)
    beta_data = bandpass_filter(bandpass_data, low_freq=13, high_freq=30)
    gamma_data = bandpass_filter(bandpass_data, low_freq=30, high_freq=42)
    
    return [delta_data, theta_data, alpha_data, beta_data, gamma_data]
