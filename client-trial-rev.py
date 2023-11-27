import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
from PIL import Image, ImageTk
from queue import Queue
import time
import subprocess

HOST = '127.0.0.1'
PORT = 9090

class Client:
    def __init__(self, host, port, username):
        self.HOST = host
        self.PORT = port
        self.username = username

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        self.receive_queue = Queue()
        self.users = set()
        self.user_messages = {}
        self.running = True

    def start(self):
        self.gui_done=False
        self.running=True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")

        self.chat_label = tkinter.Label(self.win, text=self.username, bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')

        self.msg_label = tkinter.Label(self.win, text="Chat:", bg="lightgray")
        self.msg_label.config(font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        emoji_data = [('emojis/u0001f44a.png', '\U0001F44A'), ('emojis/u0001f44c.png', '\U0001F44C'),
                    ('emojis/u0001f44d.png', '\U0001F44D'), ('emojis/u0001f495.png', '\U0001F495'),
                    ('emojis/u0001f496.png', '\U0001F496'), ('emojis/u0001f4a6.png', '\U0001F4A6'),
                    ('emojis/u0001f4a9.png', '\U0001F4A9'), ('emojis/u0001f4af.png', '\U0001F4AF'),
                    ('emojis/u0001f595.png', '\U0001F595'), ('emojis/u0001f600.png', '\U0001F600'),
                    ('emojis/u0001f602.png', '\U0001F602'), ('emojis/u0001f603.png', '\U0001F603'),
                    ('emojis/u0001f605.png', '\U0001F605'), ('emojis/u0001f606.png', '\U0001F606'),
                    ('emojis/u0001f608.png', '\U0001F608'), ('emojis/u0001f60d.png', '\U0001F60D'),
                    ('emojis/u0001f60e.png', '\U0001F60E'), ('emojis/u0001f60f.png', '\U0001F60F'),
                    ('emojis/u0001f610.png', '\U0001F610'), ('emojis/u0001f618.png', '\U0001F618'),
                    ('emojis/u0001f61b.png', '\U0001F61B'), ('emojis/u0001f61d.png', '\U0001F61D'),
                    ('emojis/u0001f621.png', '\U0001F621'), ('emojis/u0001f624.png', '\U0001F621'),
                    ('emojis/u0001f631.png', '\U0001F631'), ('emojis/u0001f632.png', '\U0001F632'),
                    ('emojis/u0001f634.png', '\U0001F634'), ('emojis/u0001f637.png', '\U0001F637'),
                    ('emojis/u0001f642.png', '\U0001F642'), ('emojis/u0001f64f.png', '\U0001F64F'),
                    ('emojis/u0001f920.png', '\U0001F920'), ('emojis/u0001f923.png', '\U0001F923'),
                    ('emojis/u0001f928.png', '\U0001F928')]

        emoji_x_pos = 490
        emoji_y_pos = 520
        for Emoji in emoji_data:
            emojis = Image.open(Emoji[0])
            emojis = emojis.resize((20, 20), Image.ANTIALIAS)
            emojis = ImageTk.PhotoImage(emojis)

            emoji_unicode = Emoji[1]
            emoji_label = tkinter.Label(self.win, image=emojis, text=emoji_unicode, bg="lightgray", cursor="hand2")
            emoji_label.image = emojis
            emoji_label.place(x=emoji_x_pos, y=emoji_y_pos)
            emoji_label.bind('<Button-1>', lambda x: self.insert_emoji(x))

            emoji_x_pos += 25
            cur_index = emoji_data.index(Emoji)
            if (cur_index + 1) % 6 == 0:
                emoji_y_pos += 25
                emoji_x_pos = 490

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(padx=20, pady=5)

        self.add_user_button = tkinter.Button(self.win, text="Add User", command=self.add_user)
        self.add_user_button.config(font=("Arial", 12))
        self.add_user_button.pack(padx=20, pady=5)

        self.text_area.tag_configure("sent_message", justify="right")
        self.text_area.tag_configure("received_message", justify="left")

        self.gui_done = True
        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        self.win.mainloop()
        while True:
                self.update_gui()
                self.win.update_idletasks()
                self.win.update()
                time.sleep(0.1)

    def insert_emoji(self, event):
        selected_emoji = event.widget.cget("text")
        self.input_area.insert(tkinter.END, selected_emoji)

    def write(self):
        message = f"{self.username} :\n{self.input_area.get('1.0', 'end')}"
        self.text_area.config(state='normal')
        self.text_area.insert('end', message + "\n", "sent_message")
        self.text_area.yview('end')
        self.text_area.config(state='disabled')
        self.sock.send(message.encode('utf-8'))

        self.user_messages.setdefault(self.username, []).append(message)
        self.input_area.delete('1.0', 'end')

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                if message == 'NICK':
                    self.sock.send(self.username.encode('utf-8'))
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', message + "\n", "received_message")
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')

                        sender = message.split(':')[0].strip()
                        self.users.add(sender)
                        self.user_messages.setdefault(sender, []).append(message)

                        self.receive_queue.put(message)

            except ConnectionAbortedError:
                break
            except:
                print("Error")
                self.sock.close()
                break


    def add_user(self):
        new_user = self.get_user_input("Add user", "Enter username:")
        if new_user:
            self.text_area.config(state='normal')
            self.text_area.insert('end', f"User '{new_user}' added.\n")
            self.text_area.yview('end')
            self.text_area.config(state='disabled')

            self.users.add(new_user)
            self.user_messages.setdefault(new_user, [])

            self.sock.send(f"ADD_USER {new_user}".encode('utf-8'))

            # Use subprocess.Popen to open a new window for the new user
            subprocess.Popen(['python', 'client-trial.py', new_user])
        else:
            print("Invalid username.")


    def open_new_gui(self, new_user):
        new_client = Client(self.HOST, self.PORT, new_user)
        new_client.start()

    def ask_user(self):
        try:
            new_user = self.get_user_input("Add user", "Enter username:")
            if new_user:
                self.text_area.config(state='normal')
                self.text_area.insert('end', f"User '{new_user}' added.\n")
                self.text_area.yview('end')
                self.text_area.config(state='disabled')
            else:
                print("Invalid username.")

        except Exception as e:
            print(f"Error adding user: {e}")

    def get_user_input(self, title, prompt):
        user_input = simpledialog.askstring(title, prompt, parent=self.win)
        return user_input

    def switch_user(self, username):
        self.text_area.config(state='normal')
        previous_text = self.text_area.get('1.0', 'end-1c')
        self.text_area.delete('1.0', 'end')
        self.text_area.insert('end', previous_text)

        messages = self.user_messages.get(username, [])

        for message in messages:
            self.text_area.insert('end', message)

        self.text_area.config(state='disabled')

    def update_gui(self):
        while not self.receive_queue.empty():
            message = self.receive_queue.get()
            self.text_area.config(state='normal')
            self.text_area.insert('end', message)
            self.text_area.yview('end')
            self.text_area.config(state='disabled')


if __name__ == "__main__":
    HOST = '127.0.0.1'
    PORT = 9090
    username = simpledialog.askstring("Nickname", "Please choose a nickname")
    client = Client(HOST, PORT, username)
    client.start()
