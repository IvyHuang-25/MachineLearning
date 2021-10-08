# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 16:58:09 2021

@author: IvyHuang
"""

import math
import cmath
import numpy as np
import pandas as pd
from scipy import fftpack
from scipy import interpolate
import matplotlib.pyplot as plt

'''
    1、获取极值点索引：extreme_index函数用于获取信号函数的极大值、极值点索引
                     便于后续得到极值点包络
'''
def extreme_index(data):
    max_index = []
    min_index = []
    
    dx = np.zeros(len(data))
    dx[:-1] = np.diff(data) # 前n-1个元素：沿着指定轴计算第N维的离散差值
                            #             即后一个元素-前一个元素
    dx[-1] = dx[-2]
    dx = np.sign(dx) # 负数为-1， 0为0， 正数为1
    d2x = np.zeros(len(data))
    d2x[1:] = np.diff(dx)
    d2x[0] = d2x[1]
    for i in np.arange(1, len(d2x)-1):
        if d2x[i] == -2: # 即-2=-1-1
            max_index.append(i)
        if d2x[i] == 2:
            min_index.append(i)
    return max_index, min_index


'''
    2、获取极值点包络：get_envelope函数用来获取信号极值包络。
                      因无法判定信号函数端点是否为极值点，这里采用border_type='OMIT'的方式，即忽略端点，不将其纳入极值包络的构造中。
'''
def get_envelope(data, border_type='OMIT', interpolation='cubic'):
    imf = {'x': data['x'], 'y_pri': data['y'], 'y_new': data['y']}
    if interpolation == 'cubic':
        if border_type == 'OMIT':
            max_index, min_index = extreme_index(data['y'])
            if len(max_index)>3 and len(min_index)>3:
                cubic_max = interpolate.interp1d(np.array(data['x'])[max_index], np.array(data['y'])[max_index], kind='cubic')
                cubic_min = interpolate.interp1d(np.array(data['x'])[min_index], np.array(data['y'])[min_index], kind='cubic')
                
                data_x_temp_start = data['x'][max_index[0]:] if max_index[0]>min_index[0] else data['x'][min_index[0]:]
                data_x_temp_end = data['x'][:max_index[-1]+1] if max_index[-1]<min_index[-1] else data['x'][:min_index[-1]+1]
                data_x_temp = list(set(data_x_temp_start).intersection(set(data_x_temp_end))) # 取交集
                data_x_temp.sort() # x序列递增
                
                envelope_max = cubic_max(data_x_temp)
                envelope_min = cubic_min(data_x_temp) 
                envelope_ave = 0.5*(envelope_max + envelope_min)
                t = pd.DataFrame({'x':data['x'], 'y':data['y']})
                temp = t[t['x'] >= data_x_temp[0]]
                final = temp[temp['x'] <= data_x_temp[len(data_x_temp)-1]]
                data_y_temp = final['y']
                imf_temp = data_y_temp - envelope_ave
                imf['x'] = np.array(data_x_temp)
                imf['y_pri'] = data_y_temp
                imf['y_new'] = imf_temp
                return imf
            else:
                return 1


'''
    3、获取特定的IMF：get_IMF函数用来获取特定的IMF，即对应于实现一次EMD过程
'''
def get_IMF(data, sift_mode='Cauthy', border_type='OMIT', interpolation='cubic', imf_num=2):
    data_temp = {}
    data_new = {}
    
    if sift_mode == 'Cauthy':
        threshold = 0.8 # Huang参考值0.2-0.3，根据信号具体情况进行相应修改
        thre = 2 * threshold
        data_temp = data
        while thre > threshold: # 获取第一个IMF分量，sift_mode进行控制.循环次数若过多，很容易导致极值点个数太少，无法求包络。需要修改相关函数
            imf = get_envelope(data_temp, border_type=border_type,interpolation=interpolation)
            if imf == 1: # 极点个数不满足要求
                return data_temp, 1 # 返回上一个筛选(sift_mode)过程的IMF与特征反馈信号
            else:
                top = sum((imf['y_pri'] - imf['y_new'])**2)
                bottom = sum((imf['y_pri'])**2)
                data_temp = {'x': imf['x'], 'y': imf['y_new']}
                thre = top / bottom
    
    if sift_mode == 'Fixed': # 以固定次数作为筛选终止条件
        data_temp = data
        while imf_num > 0 :
            imf = get_envelope(data_temp, border_type=border_type, interpolation=interpolation)
            if imf == 1:
                return data_temp, 1
            else:
                data_temp = {'x': imf['x'], 'y': imf['y_new']}
                data_new = {'x': imf['x'], 'y': imf['y_pri']-imf['y_new']}
                imf_num -= 1
    return data_temp, data_new

'''
    4、对信号进行EMD分解，得到一系列子信号(即IMF)：对信号进行EMD分解，由depose_mode控制分解终止条件，并给出筛选模式、端点处理与插值方法的设置入口。
                                             函数返回IMF个数以及IMF数据(字典形式)
'''
def get_EMD(data, depose_mode='Monotonic', sift_mode='Cauthy', border_type='OMIT', interpolation='cubic', emd_num=5, imf_num=2):
    num = 0
    imf_set = {}
    
    if depose_mode == 'Monotinic':  #以IMF极值点数目作为分解终止条件（数学上具有一般性），包含了Huang的单调函数情形。
        mono = 0
        data_temp = data
        while True:
            num += 1
            imf_temp, data_new = get_IMF(data_temp, sift_mode=sift_mode, border_type=border_type, interpolation=interpolation, imf_num=imf_num)
            imf_set[num] = {'x' + str(num): imf_temp['x'], 'y' + str(num): imf_temp['y']}
            if data_new == 1: # 达到终止条件，退出驯悍
                break
            else:
                data_temp = data_new
    
    if depose_mode == 'Fixed':  #以固定次数作为分解终止条件，仍需添加IMF极值点数目限制
        data_temp = data
        if emd_num == 1:
            imf_temp, data_new = get_IMF(data_temp, sift_mode=sift_mode, border_type=border_type, interpolation=interpolation, imf_num=imf_num)
            imf_set[1] = {'x1': imf_temp['x'], 'y1': imf_temp['y']}
        else:
            while emd_num > 0:
                num += 1
                imf_temp, data_new = get_IMF(data_temp, sift_mode=sift_mode, border_type=border_type, interpolation=interpolation, imf_num=imf_num)
                if emd_num > 1:
                    imf_set[num] = {'x'+str(num): imf_temp['x'], 'y'+str(num): imf_temp['y']}
                else:
                    imf_set[num] = {'x'+str(num): data_temp['x'], 'y'+str(num): data_temp['y']}
                if data_new == 1: # 退出循环
                    break
                else:
                    data_temp = data_new
                    emd_num -= 1
    return num, imf_set
    
    
