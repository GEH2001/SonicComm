## 实现思路

给定英文文本，转换为二进制数据比特流

封装为蓝牙包：前导码+数据长度+数据

数据较长则多个蓝牙包，多个蓝牙包之间加空白信号

采用FSK编码，将蓝牙包转换为声波信号，发送声波信号

## 文件目录
- fsk.py        2FSK调制解调算法
- pkt.py        蓝牙包编码解码
- sender.py     发送方
- receiver.py   接收方


## FSK解调
- 相干检波法，受噪声影响大
- 包络检测法，抗噪能力强

## 前导码

- 通过相关性检测前导码

[FFT计算循环互相关](https://zhuanlan.zhihu.com/p/476147772)

`np.correlate`计算互相关性

FFT计算循环互相关的效率最高

- 在解调后的信号中匹配前导码

我在实现的过程中并没有采用相关性检测的方式，因为我认为不可靠

我的处理方法是，直接对接收到的wav音频进行解调，在得到的01信号中完全匹配前导码

## 文件说明
以下文件是我在测试过程中录制的一些音频文件，将对应文件名输入到接收端，点击解码信号即可看到解调结果
- receiver2.wav (码元50ms) : This is a packet. This is another packet.
- receiver3.wav (码元50ms) : This is a packet. This is another packet.
- receiver4.wav (码元50ms 无遮100cm) : hello world, this is a packet! This is another packet. hello world, this is a packet! This is another packet
- receiver4.wav (码元50ms 遮挡50cm) : hello world, this is a packet! This is another packet. hello world, this is a packet! This is another packet

## BUG
- 空白信号必须统一置为 0 或 1 或 2，否则会干扰前导码的检测，比如空白信号恰好是 01，那么导致前导码匹配出错
- 采样点的选择很有技巧，想办法选在最中间
- find_preamble 找到一个前导码以后start应该+20，否则，如果有一个01序列长于前导码，会多次被匹配
- find_preamble 更新 start 按照包大小来更新，上一个前导码距离下一个前导码的距离很长