__author__ = 'istimaldar'
import tkinter as tk
import os
import com_pair
import sys


class MainWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.nameFrame = tk.Frame(self)
        self.nameFrame.pack(side=tk.TOP, fill=tk.X)
        self.nameLabel = tk.Label(self.nameFrame, text="Имя: ")
        self.nameLabel.pack(side=tk.LEFT)
        self.nameField = tk.Entry(self.nameFrame)
        self.nameField.pack(side=tk.RIGHT, fill=tk.X, expand=tk.TRUE)

        self.portLabel = tk.Label(self, text="Выберите порт для записи: ")
        self.portLabel.pack(side=tk.TOP, fill=tk.Y)

        self.history = tk.Listbox(self)
        self.history.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.BOTH)

        self.sendButton = tk.Button(self, text="Подключиться", command=self.connect)
        self.sendButton.pack(side=tk.BOTTOM, fill=tk.X)

        self.messageFrame = tk.Frame(self)
        self.messageLabel = tk.Label(self.messageFrame, text="Сообщение: ")
        self.messageLabel.pack(side=tk.LEFT)
        self.messageField = tk.Entry(self.messageFrame)
        self.messageField.pack(side=tk.RIGHT, fill=tk.X)

        self.find_ports()

        self.pair = None

        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.mainloop()

    def find_ports(self):
        for port in os.listdir("/dev/"):
            if "tnt" in port:
                self.history.insert(0, port)

    def connect(self):
        self.pair = com_pair.PairOfPorts("/dev/" + self.history.get(self.history.curselection()[0]), self.read)
        self.history.delete(0, tk.END)
        self.portLabel.pack_forget()
        self.messageFrame.pack(side=tk.BOTTOM, fill=tk.X)
        self.sendButton.config(text="Отправить", command=self.send_message)

    def send_message(self):
        self.history.insert(tk.END, self.nameField.get() + ": " + self.messageField.get())
        self.pair.write(self.nameField.get() + ": " + self.messageField.get())
        self.messageField.delete(0, tk.END)

    def read(self, string):
        self.history.insert(tk.END, string)

    def on_exit(self):
        if self.pair:
            self.pair.stop()
        sys.exit()

if __name__ == "__main__":
    MainWindow()