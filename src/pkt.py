"""
蓝牙包(Packet)格式: 前导码(20bit) + 数据长度(8bit) + 数据段( <= 240bit )
"""

from fsk import demodulate_envelope, modulate, demodulate
import numpy as np


# ----------------- 蓝牙包编码 ------------------

def text2bits(text):
    """
    encode_packet()的辅助函数
    text -> bits
    char(ASCII) -> 8bit(2进制)
    如：'H' -> '01001000'
    """
    bits = ''.join(format(ord(char), '08b') for char in text)
    return bits

def encode_packet(args, text):
    """
    text2packets()的辅助函数
    描述: 将文本编码为蓝牙包: 前导码(20bit) + 数据长度(8bit) + 数据段( <= 240bit )
    text -> packet (bits)
    文本最多只能有 240/8 = 30 个字符
    参数: args为全局参数, text为文本, 如'Hello, world!'
    """
    assert len(text) <= args.payload_length // 8, 'Text is too long!'
    bits = text2bits(text)
    length = len(bits)
    length_bits = format(length, '08b')
    packet = args.preamble + length_bits + bits

    if args.debug:
        print('encode_packet:', f'{text},', packet)

    return packet

def text2packets(args, text):
    """
    描述: 将文本分割为多个蓝牙包
    text -> packets [packet1, packet2, ...]
    如果文本长度超过30个字符, 则分割为多个蓝牙包
    """
    max_letters = args.payload_length // 8  # 最多30个字母
    texts = [text[i : i + max_letters] for i in range(0, len(text), max_letters)]
    packets = [encode_packet(args, text) for text in texts]
    
    if args.debug:
        print('text2packets:', texts)

    return packets

def packets2wave(args, packets):
    """
    描述: 将多个蓝牙包调制为音频波形, 包与包之间添加空白信号
    packets [packet1, packet2, ...] -> wave
    """
    blank_bits = '2' * args.interval_length   # 24个bit的空白信号, 25ms * 24 = 0.6s
    blank_wave = modulate(args, blank_bits)
    wave = blank_wave
    for packet in packets:
        packet_wave = modulate(args, packet)
        wave = np.concatenate((wave, packet_wave, blank_wave))
    return wave

# main function
def text2wave(args, text):
    """
    描述: 将文本编码为音频波形
    text -> wave
    """
    packets = text2packets(args, text)
    wave = packets2wave(args, packets)
    return wave

# ----------------- 蓝牙包解码 ------------------

def bits2text(bits):
    """
    bits -> text
    """
    # text = ''.join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8))
    text = ''
    for i in range(0, len(bits), 8):
        try:
            c = chr(int(bits[i:i+8], 2))
            text += c
        except:
            text += '#'
    return text

def decode_packet(args, packet):
    """
    packets2text()的辅助函数
    描述: 将蓝牙包解码为文本
    packet (bits) -> text
    packet: 前导码(20bit) + 数据长度(8bit) + 数据段( <= 240bit ) + 冗余信息(2222)
    packet的前一段是标准的蓝牙包, 后一段是空白信号
    """
    preamble = packet[0 : len(args.preamble)]
    assert preamble == args.preamble, 'Preamble is wrong!'
    length_bits = packet[len(args.preamble) : len(args.preamble) + args.header_length]
    length = int(length_bits, 2)
    bits = packet[len(args.preamble) + args.header_length : len(args.preamble) + args.header_length + length]
    text = bits2text(bits)

    if args.debug:
        print('decode_packet:', text)

    return text

def packets2text(args, packets):
    """
    packets [packet1, packet2, ...] -> text
    """
    text = ''.join(decode_packet(args, packet) for packet in packets)
    return text

def find_preamble(args, bits):
    """
    wave2packets()的辅助函数
    描述: 从bits中找到前导码的起始位置
    bits -> index
    """
    indices = []
    start = 0
    while True:
        index = bits.find(args.preamble, start)
        if index == -1:
            break
        indices.append(index)
        # start = index + 1
        # start = index + len(args.preamble)
        start = index + len(args.preamble) + args.header_length + args.payload_length
    
    if args.debug:
        print('find_preamble:', indices)

    return indices

def wave2packets(args, wave):
    """
    描述: 将音频波形解调为多个蓝牙包
    wave -> packets [packet1, packet2, ...]
    通过匹配前导码, 将音频波形分割为多个蓝牙包
    """
    packets = []
    # bits = demodulate(args, wave)
    bits = demodulate_envelope(args, wave)
    indices = find_preamble(args, bits)
    if indices == []:
        return packets
    start = indices[0]
    for index in indices[1:]:
        packet = bits[start : index]
        packets.append(packet)
        start = index
    packets.append(bits[start : ])

    if args.debug:
        print('bits:', bits)
        print('packets:', packets)

    return packets

# main function
def wave2text(args, wave):
    """
    描述: 将音频波形解码为文本
    wave -> text
    """
    packets = wave2packets(args, wave)
    text = packets2text(args, packets)
    return text





if __name__ == '__main__':
    from utils import init_args, save_wave, load_wave, plot_wave
    args = init_args()
    # text = 'hello world, this is a packet! This is another packet'
    # wave = text2wave(args, text)
    # save_wave(args, 'test.wav', wave)

    # exit(0)

    wave = load_wave('receiver.wav')

    # demodulate_envelope(args, wave)
    text = wave2text(args, wave)
    print(text)
