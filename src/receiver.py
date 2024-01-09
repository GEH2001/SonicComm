import tkinter as tk
import tkinter.messagebox

from pkt import wave2text
from utils import init_args, load_wave, record_wave

class Receiver:
    def __init__(self, args):
        self.args = args
    
    def init_ui(self):
        self.window = tk.Tk()
        self.label1 = tk.Label(self.window, text="录音时长")
        self.label1.grid(row=0, column=0, stick=tk.W, padx=10, pady=10)
        self.entry1 = tk.Entry(self.window, width=20)
        self.entry1.grid(row=0, column=1, stick=tk.W, pady=10)
        self.button1 = tk.Button(self.window, text='开始录音', command=self.record)
        self.button1.grid(row=1, column=1, stick=tk.W, pady=10)
        self.label2 = tk.Label(self.window, text="音频文件")
        self.label2.grid(row=2, column=0, stick=tk.W, padx=10, pady=10)
        self.entry2 = tk.Entry(self.window, width=20)
        self.entry2.grid(row=2, column=1, stick=tk.W, pady=10)
        self.button2 = tk.Button(self.window, text='解码信号', command=self.decode)
        self.button2.grid(row=3, column=1, stick=tk.W, pady=10)
        self.label3 = tk.Label(self.window, text="解码结果")
        self.label3.grid(row=4, column=0, stick=tk.W, padx=10, pady=10)
        self.entry3 = tk.Entry(self.window, width=100)
        self.entry3.grid(row=4, column=1, stick=tk.W, pady=10)
        self.window.mainloop()

    def record(self):
        """
        描述: 录音
        """
        duration = self.entry1.get()
        if len(duration) == 0:
            tkinter.messagebox.showinfo('提示', '请输入录音时长')
            return
        duration = int(duration)
        if duration <= 0:
            tkinter.messagebox.showinfo('提示', '录音时长必须大于0')
            return
        record_wave('receiver.wav', duration)
        self.entry2.delete(0, tk.END)
        self.entry2.insert(0, 'receiver.wav')
        tkinter.messagebox.showinfo('提示', '录音完成')

    def decode(self):
        """
        描述: 解码声波信号
        """
        filename = self.entry2.get()
        if len(filename) == 0:
            tkinter.messagebox.showinfo('提示', '请输入音频文件')
            return
        if filename[-4:] != '.wav':
            tkinter.messagebox.showinfo('提示', '请输入wav格式的音频文件')
            return
        wave = load_wave(filename)
        text = wave2text(self.args, wave)
        self.entry3.delete(0, tk.END)
        self.entry3.insert(0, text)
        tkinter.messagebox.showinfo('提示', '信号已解码')
    

if __name__ == '__main__':
    args = init_args()
    receiver = Receiver(args)
    receiver.init_ui()
