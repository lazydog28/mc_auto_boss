import os
import tkinter as tk
import multiprocessing
from config import config, root_path
import pystray
from pystray import MenuItem as item
from PIL import Image

class LogWindow:
    def __init__(self, queue):
        self.queue = queue
        self.root = tk.Tk()
        self.root.title("Rin Rin MC Log Window")
        self.root.geometry(config.MaskWindowViewerSize)
        self.root.overrideredirect(True)  # 去除窗口边框和标题栏
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", config.MaskWindowViewerDiaphanous / 100)  # 设置窗口透明度

        self.title_bar = tk.Frame(self.root, bg='#f8b400', relief='raised', bd=0, highlightthickness=0)
        self.title_bar.place(x=0, y=0, relwidth=1, height=50)

        gui_path = os.path.join(root_path, "template", "gui")
        icon_path = os.path.join(gui_path, "mask_window_viewer_title_icon_32x32.png")

        self.icon_image = tk.PhotoImage(file=icon_path)
        self.icon_label = tk.Label(self.title_bar, image=self.icon_image, bg='#f8b400')
        self.icon_label.pack(side=tk.LEFT, padx=5)

        self.title_label = tk.Label(self.title_bar, text="Rin Rin MC Log Window", bg='#f8b400', fg='#FFFFFF', font=('Comic Sans MS', 15, 'bold'))
        self.title_label.pack(side=tk.LEFT, padx=5)

        self.minimize_button = tk.Button(self.title_bar, text='-', command=self.minimize_window, bg='#f8b400', fg='#FFFFFF', bd=0, highlightthickness=0, font=('Comic Sans MS', 12, 'bold'))
        self.minimize_button.pack(side=tk.RIGHT, padx=5)

        self.close_button = tk.Button(self.title_bar, text='x', command=self.hide, bg='#f8b400', fg='#FFFFFF', bd=0, highlightthickness=0, font=('Comic Sans MS', 12, 'bold'))
        self.close_button.pack(side=tk.RIGHT, padx=5)

        self.title_bar.bind('<Button-1>', self.click_title_bar)
        self.title_bar.bind('<B1-Motion>', self.drag_title_bar)

        self.content_frame = tk.Frame(self.root, bg='white')
        self.content_frame.place(x=0, y=50, relwidth=1, relheight=1)

        self.canvas = tk.Canvas(self.content_frame, bg="#FEFEFE", highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.configure(bg='#FEFEFE')

        self.root.wm_attributes("-transparentcolor", "#FEFEFE")

        self.text = tk.Text(self.canvas, wrap='word', bg='#FEFEFE', fg=f'{config.MaskWindowViewerTextColor}', font=('Microsoft YaHei', config.MaskWindowViewerTextSize, 'bold'), bd=0, highlightthickness=0)
        self.text.pack(expand=True, fill='both')
        self.text.configure(insertbackground=f'{config.MaskWindowViewerTextColor}')  # 设置光标颜色
        self.log_lines = []
        self.content_frame.after(100, self.process_queue)
        self.is_visible = True

        self.tray_icon = pystray.Icon("Rin Rin MC Log Window")
        self.tray_icon.menu = pystray.Menu(
            item('Show', self.show_from_tray),
            item('Quit', self.exit_from_tray)
        )
        self.tray_icon.icon = Image.open(icon_path)
        self.tray_icon.run_detached()

    def click_title_bar(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def drag_title_bar(self, event):
        x = event.x_root - self.offset_x
        y = event.y_root - self.offset_y
        self.root.geometry(f'+{x}+{y}')

    def minimize_window(self):
        self.root.withdraw()

    def show_from_tray(self, icon, item):
        self.root.deiconify()

    def exit_from_tray(self, icon, item):
        self.tray_icon.stop()
        self.root.quit()

    def check_display_change_command(self):
        global log_window_display_run
        if log_window_display_run.value:
            self.toggle_visibility()
            log_window_display_run.value = False

    def process_queue(self):
        self.check_display_change_command()
        while not self.queue.empty():
            content = self.queue.get()
            if content == 'exit':
                self.exit()
                return
            self.log_lines.append(content)
            if len(self.log_lines) > 1000:  # 限制日志内容长度
                self.log_lines = self.log_lines[-1000:]
            self.text.delete(1.0, tk.END)
            self.text.insert(tk.END, "\n".join(self.log_lines))
            self.text.see(tk.END)
        self.content_frame.after(100, self.process_queue)

    def show(self):
        self.root.deiconify()  # 显示窗口
        self.is_visible = True

    def hide(self):
        self.root.withdraw()  # 隐藏窗口
        self.is_visible = False

    def toggle_visibility(self, event=None):
        if self.is_visible:
            self.hide()
        else:
            self.show()

    def exit(self, event=None):
        self.tray_icon.stop()
        self.root.quit()

    def run(self):
        self.root.mainloop()

log_window_display_run = None

def start_log_window(queue, log_window_display):
    global log_window_display_run
    log_window = LogWindow(queue)
    log_window_display_run = log_window_display
    log_window.run()