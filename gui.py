import os
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
from tkinter.filedialog import askdirectory
import base64
from pictures.python_logo import img as logo


def start():
	url = entry_url.get()
	path = entry_path.get()
	option = var_option_menu.get()
	scrolled_text.delete('1.0', END)
	scrolled_text.insert(INSERT, url)
	scrolled_text.insert(INSERT, '\n')
	scrolled_text.insert(INSERT, path)
	scrolled_text.insert(INSERT, '\n')
	scrolled_text.insert(INSERT, option)


def select_path():
	path_ = askdirectory()
	var_path_text.set(path_)


# 顶层窗口
top = Tk()  # 创建顶层窗口
top.title('知乎视频下载器')
top.geometry('600x400+400+120')  # 初始化窗口大小
top.resizable(False, False)  # 窗口长宽不可变


# 插入背景图片
tmp = open('tmp.gif', 'wb+')  # 临时文件用来保存gif文件
tmp.write(base64.b64decode(logo))
tmp.close()
image = Image.open('tmp.gif')
bg_img = ImageTk.PhotoImage(image)
label_img = Label(top, image=bg_img, cursor='spider')
os.remove('tmp.gif')

# 文章链接(Label+Entry)
label_url = Label(top, text='知乎文章链接', cursor='cross')
var_url_text = StringVar()
entry_url = Entry(top, relief=RAISED, fg='gray', bd=2, width=56, textvariable=var_url_text)

# 视频路径(Label+Entry)
label_path = Label(top, text='视频保存路径', cursor='cross')
var_path_text = StringVar()
entry_path = Entry(top, relief=RAISED, fg='gray', bd=2, width=56, textvariable=var_path_text)
button_choice = Button(top, relief=RAISED, text='打开', bd=1, width=5, height=1, command=select_path)

# 视频清晰度选择(Label+OptionMenu)
label_option = Label(top, text='视频质量', cursor='cross')
options = ['高清HD', '标清SD', '普清LD']
var_option_menu = StringVar()
var_option_menu.set(options[0])
option_menu = OptionMenu(top, var_option_menu, *options)

# 按钮控件
button_start = Button(top, text='开始', command=start, height=1, width=15, relief=RAISED, bd=4, activebackground='pink', activeforeground='white')
button_quit = Button(top, text='退出', command=top.quit, height=1, width=15, relief=RAISED, bd=4, activebackground='pink', activeforeground='white')

# 可滚动的多行文本区域
scrolled_text = ScrolledText(top, relief=GROOVE, bd=4, height=15, width=73, cursor='heart')

# place布局
label_img.place(relx=0.5, rely=0.08, anchor=CENTER)
label_url.place(relx=0.12, rely=0.17, anchor=CENTER)
entry_url.place(relx=0.54, rely=0.17, anchor=CENTER)
label_path.place(relx=0.12, rely=0.26, anchor=CENTER)
entry_path.place(relx=0.54, rely=0.26, anchor=CENTER)
button_choice.place(relx=0.92, rely=0.26, anchor=CENTER)
label_option.place(relx=0.14, rely=0.36, anchor=CENTER)
option_menu.place(relx=0.275, rely=0.36, anchor=CENTER)
button_start.place(relx=0.55, rely=0.36, anchor=CENTER)
button_quit.place(relx=0.81, rely=0.36, anchor=CENTER)
scrolled_text.place(relx=0.51, rely=0.7, anchor=CENTER)

# 输入框默认内容
var_url_text.set(r'https://www.zhihu.com/question/279405182/answer/410204397')
var_path_text.set(r'D:/zhihu_video')

# 运行这个GUI应用
top.mainloop()
