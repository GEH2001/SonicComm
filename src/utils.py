import argparse
from scipy.io import wavfile
import matplotlib.pyplot as plt
import numpy as np

def init_args():
    """
    加载全局参数
    返回: args
    """
    parser = argparse.ArgumentParser(description='FSK Modulation')
    
    # 0 1 信号的频率
    parser.add_argument("--frequency_0", type=int, default=4000, help="Frequency of 0")
    parser.add_argument("--frequency_1", type=int, default=6000, help="Frequency of 1")

    # 采样率, 振幅, 初始相位, 窗口长度
    parser.add_argument("--framerate", type=int, default=48000, help="Framerate")
    parser.add_argument("--volume", type=float, default=30000.0, help="Volume")
    parser.add_argument("--phrase", type=int, default=0)
    parser.add_argument("--window", type=float, default=5e-2, help="Window length")   # 码元 25ms
    
    # 蓝牙包
    parser.add_argument("--header_length", type=int, default=8, help="Length of header")    # header长度为8bit, 用于表示数据段的长度, 最大值255
    parser.add_argument("--payload_length", type=int, default=240, help="Length of payload")  # 数据段最多240个bit, 即30个字母 11110000
    parser.add_argument("--interval_length", type=int, default=48)  # 蓝牙包之间的空白间隔长度, 48个bit

    # 调试模式
    parser.add_argument("--debug", type=bool, default=False, help="Debug mode")

    args = parser.parse_args()
    
    # 前导码
    args.preamble = '01' * 10
    

    return args





def load_wave(filename):
    """
    读取音频文件, 单声道
    """
    sample_rate, wave = wavfile.read(filename)
    print('sample_rate:', sample_rate)
    return wave


def plot_wave(wave):
    """
    描述: 绘制波形
    参数: wave为一维numpy数组
    """
    
    plt.plot(wave)
    plt.show()


def save_wave(args, filename, wave):
    """
    保存波形
    """
    wavfile.write(filename, args.framerate, wave.astype(np.int16))


def record_wave(filename, duration):
    """
    描述: 录制音频
    参数: filename为文件名, duration为录制时长
    """
    import pyaudio
    import wave

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 48000
    RECORD_SECONDS = duration
    WAVE_OUTPUT_FILENAME = filename

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):  # 48000 / 1024 * 5 = 2343
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # 保存录音文件
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)   # 1
    wf.setsampwidth(p.get_sample_size(FORMAT))   # 2
    wf.setframerate(RATE)   # 48000
    wf.writeframes(b''.join(frames))
    wf.close()


if __name__ == '__main__':
    record_wave('record.wav', 17)