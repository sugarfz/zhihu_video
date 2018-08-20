import os
import json
import requests
from requests import RequestException
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import askdirectory
from PIL import Image, ImageTk
import threading
import base64
from pictures.python_logo import img as logo


def is_valid(url, path):
	if url is '':
		print('请输入文章链接...')
		scrolled_text.insert(INSERT, '请输入文章链接...\n')
		scrolled_text.see(END)
		return None
	else:
		url_pattern = re.compile('^(https://www.zhihu.com/question/\d{8,9}/answer/\d{9})$', re.S)
		result = re.search(url_pattern, url)
		if result is None:
			print('错误的文章链接，请重新输入...')
			scrolled_text.insert(INSERT, '错误的文章链接，请重新输入...\n')
			scrolled_text.see(END)
			return None
		else:
			if path is '':
				print('请输入视频保存路径...')
				scrolled_text.insert(INSERT, '请输入视频保存路径...\n')
				scrolled_text.see(END)
				return None
			else:
				path_pattern = re.compile('(^[a-zA-Z]:/[0-9a-zA-Z_]+(/[0-9a-zA-Z_]+)*$)|(^[a-zA-Z]:/[0-9a-zA-Z_]*$)', re.S)
				result = re.search(path_pattern, path)
				if result is None:
					print('错误的文件路径，请重新输入...')
					scrolled_text.insert(INSERT, '错误的文件路径，请重新输入...\n')
					scrolled_text.see(END)
					return None
				else:
					return True


def get_page(url):
	try:
		headers = {
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36'
		}
		response = requests.get(url, headers=headers, timeout=30)
		if response.status_code == 200:
			return response.text
		print('链接访问失败，请重试...')
		scrolled_text.insert(INSERT, '链接访问失败，请重试...\n')
		scrolled_text.see(END)
		return None
	except RequestException:
		print('链接访问失败，请重试...')
		scrolled_text.insert(INSERT, '链接访问失败，请重试...\n')
		scrolled_text.see(END)
		return None


def parse_page(html):
	videos = re.findall(r'z-ico-video"></span>(.*?)</span>', html)
	if videos:
		insert_text = '共找到' + str(len(videos)) + '个视频\n'
		print(insert_text)
		scrolled_text.insert(INSERT, insert_text)
		scrolled_text.see(END)
		for video in videos:
			yield video
	else:
		print('未找到视频')
		scrolled_text.insert(INSERT, '未找到视频\n')
		scrolled_text.see(END)


def get_real_url(url, try_count=1):
	if try_count > 3:
		return None
	try:
		headers = {
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36'
		}
		response = requests.get(url, headers=headers, timeout=30)
		if response.status_code >= 400:
			return get_real_url(url, try_count+1)
		return response.url
	except RequestException:
			return get_real_url(url, try_count+1)


def get_m3u8_url(url, video_dpi):
	try:
		path_pattern = re.compile('(\d+)', re.S).search(url).group(1)
		get_play_url = 'https://lens.zhihu.com/api/videos/' + path_pattern
		headers = {
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36'
		}
		content = requests.get(get_play_url, headers=headers).text
		data = json.loads(content)  # 将json格式的字符串转化为字典
		if data and 'playlist' in data.keys():
			m3u8_url = data.get('playlist').get(video_dpi).get('play_url')
			return m3u8_url
	except Exception:
		return None


def get_m3u8_content(url, try_count=1):
	if try_count > 3:
		print('Get M3U8 Content Failed ', url)
		insert_text = 'Get M3U8 Content Failed ' + url + '\n'
		scrolled_text.insert(INSERT, insert_text)
		scrolled_text.see(END)
		return None
	headers = {
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36'
	}
	try:
		response = requests.get(url, headers=headers, timeout=30)
		if response.status_code == 200:
			return response.text
		return get_m3u8_content(url, try_count+1)
	except RequestException:
		return get_m3u8_content(url, try_count+1)


def get_ts(url, try_count=1):
	if try_count > 3:
		print('Get TS Failed ', url)
		insert_text = 'Get TS Failed ' + url + '\n'
		scrolled_text.insert(INSERT, insert_text)
		scrolled_text.see(END)
		return None
	headers = {
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36'
	}
	try:
		response = requests.get(url, headers=headers, timeout=30)
		if response.status_code == 200:
			return response
		return get_ts(url, try_count+1)
	except RequestException:
		return get_ts(url, try_count+1)


def download_m3u8(m3u8_url, video_url, video_count, path, video_dpi_str):
	print('准备下载 ', video_url)
	insert_text = '准备下载 ' + video_url + '\n'
	scrolled_text.insert(INSERT, insert_text)
	scrolled_text.see(END)
	download_path = path + '/'
	try:
		all_content = get_m3u8_content(m3u8_url)
		file_line = all_content.split('\n')  # 读取文件里的每一行
		# 通过判断文件头来确定是否是M3U8文件
		if file_line[0] != '#EXTM3U':
			raise BaseException('非M3U8链接')
		else:
			unknow = True  # 用来判断是否找到了下载的地址
			threads = []  # 定义线程池
			for index, line in enumerate(file_line):
				if "EXTINF" in line:
					unknow = False
					c_fule_name = str(file_line[index + 1]).split('?', 1)[0]
					source_path = c_fule_name.split('-', 1)[0]  # 区分不同源的视频流
					th = threading.Thread(target=download_ts, args=(m3u8_url, file_line, c_fule_name, download_path, index,))
					threads.append(th)
			if unknow:
				raise BaseException('未找到对应的下载链接')
			else:
				for t in threads:  # 启动线程
					t.start()
				for t in threads:  # 等待子线程结束
					t.join()
				print('下载完成，正在合并视频流...')
				scrolled_text.insert(INSERT, '下载完成，正在合并视频流...\n')
				scrolled_text.see(END)
				merge_file(download_path, source_path, video_count, video_dpi_str)
	except Exception:
		return None


def download_ts(m3u8_url, file_line, c_fule_name, download_path, index):
	# 拼出ts片段的URL
	pd_url = m3u8_url.rsplit('/', 1)[0] + '/' + file_line[index + 1]  # rsplit从字符串最后面开始分割
	response = get_ts(pd_url)
	if response:
		if not os.path.exists(download_path):
			os.mkdir(download_path)
		with open(download_path + c_fule_name, 'wb') as f:
			f.write(response.content)
			f.close()
		print('正在下载 ', c_fule_name)
		insert_text = '正在下载 ' + c_fule_name + '\n'
		scrolled_text.insert(INSERT, insert_text)
		scrolled_text.see(END)


def merge_file(download_path, source_path, video_count, video_dpi_str):
	os.chdir(download_path)  # 修改当前工作目录
	video_name = 'video' + str(video_count) + '_' + video_dpi_str + '_' + source_path + '.mp4'
	merge_cmd = 'copy /b ' + source_path + '*.ts ' + video_name
	del_cmd = 'del /Q ' + source_path + '*.ts'
	os.system(merge_cmd)
	os.system(del_cmd)
	print('合并完成，请欣赏 ', video_name)
	insert_text = '合并完成，请欣赏 ' + video_name + '\n\n'
	scrolled_text.insert(INSERT, insert_text)
	scrolled_text.see(END)


def run(url, path, video_dpi):
	video_count = 0
	video_dpi_str = video_dpi[-2:].lower()
	if is_valid(url, path):  # 判断url的有效性
		# 改变输入框文本颜色
		entry_url['fg'] = 'black'
		entry_path['fg'] = 'black'
		html = get_page(url)
		if html:
			video_urls = parse_page(html)
			for video_url in video_urls:
				if video_url:
					real_url = get_real_url(video_url)
					if real_url:
						m3u8_url = get_m3u8_url(real_url, video_dpi_str)
						if m3u8_url:
							video_count += 1
							download_m3u8(m3u8_url, video_url, video_count, path, video_dpi_str)


'''+++++++++++++++++++++++++++++++++++++GUI++++++++++++++++++++++++++++++++++++++++'''


def start():
	url = entry_url.get()
	path = entry_path.get()
	video_dpi = var_option_menu.get()
	scrolled_text.delete('1.0', END)
	th = threading.Thread(target=run, args=(url, path, video_dpi))
	th.setDaemon(True)
	th.start()


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
