import tkinter as tk
import tkinter.messagebox
from pkt import text2wave
from utils import init_args, save_wave
import os
import pyaudio
import wave

class Sender:
    def __init__(self, args):
        self.args = args


    def init_ui(self):
        """
        描述: 初始化gui
        """
        self.window = tk.Tk()
        self.label1 = tk.Label(self.window, text="输入文本")
        self.label1.grid(row=0, column=0, stick=tk.W, padx=10, pady=10)
        self.entry1 = tk.Entry(self.window, width=100)
        self.entry1.grid(row=0, column=1, stick=tk.W, pady=10)
        self.button1 = tk.Button(self.window, text='生成信号', command=self.gen_wave)
        self.button1.grid(row=2, column=1, stick=tk.W, pady=10)
        self.label2 = tk.Label(self.window, text="音频文件")
        self.label2.grid(row=3, column=0, stick=tk.W, padx=10, pady=10)
        self.entry2 = tk.Entry(self.window, width=20)
        self.entry2.grid(row=3, column=1, stick=tk.W, pady=10)
        self.buttion2 = tk.Button(self.window, text='播放信号', command=self.play_wave)
        self.buttion2.grid(row=4, column=1, stick=tk.W, pady=10)
        self.window.mainloop()

    def gen_wave(self):
        """
        描述: 生成声波信号
        """

        text = self.entry1.get()
        if len(text) == 0:
            tkinter.messagebox.showinfo('提示', '请输入文本')
            return
        
        wave = text2wave(self.args, text)
        save_wave(self.args, 'sender.wav', wave)

        self.entry2.delete(0, tk.END)
        self.entry2.insert(0, 'sender.wav')

        tkinter.messagebox.showinfo('提示', '信号已生成')


    def play_wave(self):
        """
        描述: 播放声波信号
        """
        filename = self.entry2.get()
        if len(filename) == 0:
            tkinter.messagebox.showinfo('提示', '请输入音频文件')
            return
        if filename[-4:] != '.wav':
            tkinter.messagebox.showinfo('提示', '请输入.wav文件')
            return
        if not os.path.exists(filename):
            tkinter.messagebox.showinfo('提示', '音频文件不存在')
            return
        
        chunk = 1024
        wf = wave.open(filename, 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(
            format = p.get_format_from_width(wf.getsampwidth()),
            channels = wf.getnchannels(),
            rate = wf.getframerate(),
            output = True
        )
        
        data = wf.readframes(chunk)
        while data != b'':
            stream.write(data)
            data = wf.readframes(chunk)
        
        stream.stop_stream()
        stream.close()
        p.terminate()


if __name__ == "__main__":
    args = init_args()
    sender = Sender(args)
    sender.init_ui()