"""
2FSK调制解调算法
"""

import numpy as np
from scipy.signal import butter, filtfilt, hilbert
import matplotlib.pyplot as plt

def generate_pulse(framerate, frequency, volume, phrase, duration):
    """
    modulate的辅助函数
    描述: 生成单个脉冲信号
    参数: framerate为采样率, frequency为频率, volume为音量, phrase为起始相位, duration为持续时间
    返回值: 波形, 一维numpy数组
    """
    n_frames = round(duration * framerate)
    x = np.linspace(0, duration, num=n_frames)
    y = volume * np.sin(2 * np.pi * frequency * x + phrase)
    return y

def modulate(args, bits):
    """
    描述: FSK调制算法
    bits -> wave
    bits: 二进制字符串, 如'2201012'
    wave: 一维numpy数组
    """
    code0 = generate_pulse(args.framerate, args.frequency_0, args.volume, args.phrase, args.window)
    code1 = generate_pulse(args.framerate, args.frequency_1, args.volume, args.phrase, args.window)
    # code2 表示空白信号
    code2 = generate_pulse(args.framerate, 1, 0, args.phrase, args.window)
    wave = np.zeros(0)
    for bit in bits:
        if bit == '0':
            wave = np.append(wave, code0)
        elif bit == '1':
            wave = np.append(wave, code1)
        else:
            wave = np.append(wave, code2)
    return wave

def find_index(channel1, channel2, threshold):
    """
    描述: demodulate的辅助函数, 寻找抽样判决所需的最佳index
    channel1, channel2的波形都类似矩形波, 有上升沿和下降沿
    threshold是阈值, 通过寻找channel和threshold的前两个交点
    2个交点中间的位置就是最佳判决点
    """
    # 其实不需要判断channel2的交点
    # 因为前导码0101, 所以channel1一定先于channel2
    # 这里就假装这个先验未知
    cross_index = []
    # 找到channel1和threshold的前2个交点
    for i in range(len(channel1) - 1):
        if channel1[i] < threshold and channel1[i + 1] > threshold:
            cross_index.append(i)
            break
    for i in range(cross_index[0] + 1, len(channel1) - 1):
        if channel1[i] > threshold and channel1[i + 1] < threshold:
            cross_index.append(i)
            break
    # 找到channel2和threshold的前2个交点
    for i in range(len(channel2) - 1):
        if channel2[i] < threshold and channel2[i + 1] > threshold:
            cross_index.append(i)
            break
    for i in range(cross_index[2] + 1, len(channel2) - 1):
        if channel2[i] > threshold and channel2[i + 1] < threshold:
            cross_index.append(i)
            break
    # first_index = min(cross_index[0] + cross_index[1], cross_index[2] + cross_index[3]) // 2
    # 直接取channel1和channel2的2个上升沿
    first_index = (cross_index[0] + cross_index[2]) // 2
    return first_index

def demodulate(args, wave):
    """
    描述: FSK解调算法 - 相干检波 - 参考老师课件
    wave -> bits
    wave: 一维numpy数组 - 读取wav文件得到的音频波形
    bits: 二进制字符串, 如'22010122'
    """
    # 带通滤波（好像没有带通滤波, 直接相干效果也很好）
    # TODO: 将Wn写在args里
    b, a = butter(8, [7/48, 9/48], 'bandpass')
    band_wave1 = filtfilt(b, a, wave)
    b, a = butter(8, [11/48, 13/48], 'bandpass')
    band_wave2 = filtfilt(b, a, wave)

    # 相干
    t = np.linspace(0, len(wave) / args.framerate, len(wave), endpoint=False)
    down_wave1 = band_wave1 * np.sin(2 * np.pi * args.frequency_0 * t)
    down_wave2 = band_wave2 * np.sin(2 * np.pi * args.frequency_1 * t)

    # 低通滤波
    b, a = butter(8, 0.05, 'lowpass')
    channel1 = filtfilt(b, a, down_wave1)
    channel2 = filtfilt(b, a, down_wave2)
    
    channel1 = np.abs(channel1)
    channel2 = np.abs(channel2)

    # 抽样判决器
    width = round(args.framerate * args.window)
    result = []
    threshold = round(0.2 * (channel1.max() / 2 + channel2.max() / 2))
    first_index = find_index(channel1, channel2, threshold)
    index = first_index # 其实这里可以直接从first_index开始, 因为前面的信号都是空白信号
    # TODO: 单点判决 -> 区间判决
    while index <= len(channel1):
        sample1 = channel1[index]
        sample2 = channel2[index]
        if sample1 < 0.2 * threshold and sample2 < 0.2 * threshold:
            result.append(2)
        if sample1 > sample2:
            result.append(0)
        else:
            result.append(1)
        
        index += width
    result = ''.join(str(x) for x in result)

    if args.debug:
        plt.plot(channel1, label='Bit 0')
        plt.plot(channel2, label='Bit 1')
        plt.plot(threshold * np.ones(len(channel1)), label='Threshold')
        plt.plot(first_index, 2.5*threshold, 'o', color='red', label='First index')
        plt.title('Demodulation')
        plt.legend()
        plt.show()

    return result


# 朴素方法: 逐窗口FFT
def demodulate_plain(args, wave):
    """
    描述: FSK解调算法 - 朴素方法 - 逐窗口FFT
    wave -> bits
    wave: 一维numpy数组 - 读取wav文件得到的音频波形
    bits: 二进制字符串, 如'22010122'
    """
    pass



def demodulate_envelope(args, wave):
    """
    描述: FSK解调 - 包络检测
    wave -> bits
    wave: 一维numpy数组 - 读取wav文件得到的音频波形
    bits: 二进制字符串, 如'22010122'
    """
    # TODO: 预处理: 放大信号、滤波
    # 带通滤波（好像没有带通滤波, 直接相干效果也很好）
    # TODO: 将Wn写在args里
    b, a = butter(8, [7/48, 9/48], 'bandpass')
    band_wave1 = filtfilt(b, a, wave)
    b, a = butter(8, [11/48, 13/48], 'bandpass')
    band_wave2 = filtfilt(b, a, wave)

    # 提取包络 - Hilbert变换
    envelope1 = np.abs(hilbert(band_wave1))
    envelope2 = np.abs(hilbert(band_wave2))

    # 放大信号 TODO: 直接对max求归一化误差太大，选取阈值以上的平均值 或者 选取前几个最大值的平均值
    envelope1 = envelope1 / envelope1.max() * args.volume
    envelope2 = envelope2 / envelope2.max() * args.volume
    
    result = []
    width = round(args.framerate * args.window)
    threshold = 0.2 * args.volume
    first_index = find_index(envelope1, envelope2, threshold)
    # index = width // 2
    index = first_index
    while index <= len(envelope1):
        # TODO: 区间采样
        sample1 = envelope1[index]
        sample2 = envelope2[index]
        if sample1 < 0.2 * threshold and sample2 < 0.2 * threshold: # 空白信号
            result.append(2)
        elif sample1 > sample2:
            result.append(0)
        else:
            result.append(1)
        index += width
    
    result = ''.join(str(x) for x in result)

    if args.debug:
        plt.plot(envelope1, label='Bit 0')
        plt.plot(envelope2, label='Bit 1')
        plt.plot(threshold * np.ones(len(envelope1)), label='Threshold')
        plt.plot(first_index, threshold, 'o', color='red', label='First index')
        plt.title('Demodulation Envelope')
        plt.legend()
        plt.show()
        print('demodulate_envelope:', result)

    return result