from flask import Flask, request, render_template, url_for
from urllib.request import urlopen
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from pyaudio import PyAudio,paInt16
import os
from aip import AipSpeech
import ffmpy #视频音频转码模块
from urllib.request import urlopen
import re
from pydub import AudioSegment
from bs4 import BeautifulSoup
import urllib
import time
import requests
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from skimage import io
import matplotlib.pyplot as plt
import json


accept_tos = BooleanField('I accept the TOS', [validators.Required()])
# app = Flask(__name__)
app = Flask(__name__, static_folder='', static_url_path='') #设置默认路径

class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    email = TextField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

filename_music = 'music.mp3'
chunk=2048 #好像是分段记录时每次记录的点数
def play(filename): #可以播放mp3,wav,amr,mp4; pcm还不行，要额外指定sample_width 现在是单线程的，后面要研究一下如何变成多线程的，不然这个助理就用不了了
    try:
        sound = AudioSegment.from_file(filename, format=str.split(filename,'.')[1])
    except:
#         print('该wav文件缺少RIFF头')
        filename_answer = 'tmp.' + str.split(filename,'.')[1]
#         filename_answer = 'tmp.wav'
        if os.path.exists(filename_answer):
            os.remove(filename_answer)
        ff = ffmpy.FFmpeg(
        inputs={filename: None},
        outputs={filename_answer: None}
        )
        ff.run() #美中不足的时没有学会怎么执行覆盖文件操作，文件存在时写入操作会被直接跳过，故现在只能暂时在转码播放后直接将其移除
        sound = AudioSegment.from_file(filename_answer, format=str.split(filename_answer,'.')[1])
    p=PyAudio()
    stream=p.open(format=p.get_format_from_width(sound.sample_width),channels= \
        sound.channels,rate=sound.frame_rate,output=True)
    i=0
    while True:
        data = sound.raw_data[i*chunk : (i+1)*chunk]
        if data==b'':break
        stream.write(data) #这一行是播放语音
        i = i + 1
    stream.close()
    p.terminate()

def listen_music(keyword):
# keyword = input("请输入想要听的歌曲：")
    keyword = '把你写进我的歌里'
    url = "http://songsearch.kugou.com/song_search_v2?callback=jQuery1124006980366032059648_1518578518932&keyword="+keyword+"&page=1&pagesize=30&userid=-1&clientver=&platform=WebFilter&tag=em&filter=2&iscorrection=1&privilege_filter=0&_=1518578518934"
    content = requests.get(url)
    if re.findall('"FileHash":"(.*?)"',content.text) == []:
        message_answer = '没有搜索到对应的歌曲'
        result_tts = client.synthesis(message_answer, 'zh', 1, {'vol': 5, 'per': 0})
        with open(filename_answer, 'wb') as f:
            f.write(result_tts)
        play(filename_answer)
    else:
        filehash = re.findall('"FileHash":"(.*?)"',content.text)[0]
        songname = re.findall('"SongName":"(.*?)"',content.text)[0].replace("<\\/em>","").replace("<em>","") #即将播放的歌曲名
        hash_url = "http://www.kugou.com/yy/index.php?r=play/getdata&hash="+filehash
        hash_content = requests.get(hash_url)
        play_url = re.findall('"play_url":"(.*?)"',hash_content.text)
        play_url = ' '.join(play_url)
        real_download_url = play_url.replace("\\","")
        print("客官，请稍等一下，好音乐马上呈上！")
        # with open(songname+".mp3","wb")as fp:
        with open(filename_music,"wb")as fp:
            fp.write(requests.get(real_download_url).content)
        print('下载完成，敬请收听！')
        play(filename_music)
    return 1
# @app.route('/')
@app.route('/',methods=['GET','POST'])

def home():
    # print(url_for('static', filename='res/sheeta.jpg')) #url_for函数用于生成对服务器上某个资源的URL
    # return render_template('E:\我的东西\新建文件夹\文件\课件\信工课件\电子系统综合设计\半成品\代码文件\Flask.html')
    return render_template('mine.html') #直接在这里返回一大坨html语句是很不美观且费时的，因此flask提供了render_template方法，使用已有的html文件作为模板
def hello_world():
    resp = urlopen('http://www.weather.com.cn/weather/101010100.shtml')
    soup = BeautifulSoup(resp, 'html.parser')
    tagDate = soup.find('ul', class_="t clearfix")
    dates = tagDate.h1.string

    tagToday = soup.find('p', class_="tem")
    try:
        temperatureHigh = tagToday.span.string
    except AttributeError as e:
        temperatureHigh = tagToday.find_next('p', class_="tem").span.string

    temperatureLow = tagToday.i.string
    weather = soup.find('p', class_="wea").string

    tagWind = soup.find('p', class_="win")
    winL = tagWind.i.string
    weatherdata=('dates','temperatureLow','temperatureHigh','winL','weather')

    return weather

@app.route('/navigator')
def about():
    #c = input("请输入：")
    #keyword = urllib.parse.quote(c)

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    req = urllib.request.Request(url="http://www.dianping.com/search/keyword/4/0_9%E6%97%A5%E6%96%99", headers=headers)
    response = urlopen(req)

    # header = {}
    # header[
    #    'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0'
    # req = request.Request(url, headers=header)
    # response = request.urlopen(req)
    # url = 'https://www.dianping.com/search/keyword/4/0_' + keyword

    soup = BeautifulSoup(response, 'html.parser')
    links = soup.find_all('h4')
    for link in links[2:5]:
        print(link.get_text())

    return link.get_text()

@app.route('/music',methods=['GET','POST'])
def listen_music():
# keyword = input("请输入想要听的歌曲：")
#     keyword=request.form["keyword"]
#     if request.value is not None:
    if 1:
        # postdata = request.values.get('clickdata')
        # print(json.loads(postdata))
        keyword = '把你写进我的歌里'
        # print(keyword)
        url = "http://songsearch.kugou.com/song_search_v2?callback=jQuery1124006980366032059648_1518578518932&keyword="+keyword+"&page=1&pagesize=30&userid=-1&clientver=&platform=WebFilter&tag=em&filter=2&iscorrection=1&privilege_filter=0&_=1518578518934"
        content = requests.get(url)
        if re.findall('"FileHash":"(.*?)"',content.text) == []:
            message_answer = '没有搜索到对应的歌曲'
            result_tts = client.synthesis(message_answer, 'zh', 1, {'vol': 5, 'per': 0})
            with open(filename_answer, 'wb') as f:
                f.write(result_tts)
            play(filename_answer)
        else:
            filehash = re.findall('"FileHash":"(.*?)"',content.text)[0]
            songname = re.findall('"SongName":"(.*?)"',content.text)[0].replace("<\\/em>","").replace("<em>","") #即将播放的歌曲名
            hash_url = "http://www.kugou.com/yy/index.php?r=play/getdata&hash="+filehash
            hash_content = requests.get(hash_url)
            play_url = re.findall('"play_url":"(.*?)"',hash_content.text)
            play_url = ' '.join(play_url)
            real_download_url = play_url.replace("\\","")
            print("客官，请稍等一下，好音乐马上呈上！")
            # with open(songname+".mp3","wb")as fp:
            with open(filename_music,"wb")as fp:
                fp.write(requests.get(real_download_url).content)
            print('下载完成，敬请收听！')

    return render_template("mine.html")

@app.route('/register', methods=['GET', 'POST'])
# def register():
#     print (request.headers)
#     print (request.form)
#     print (request.form['name'])
#     print (request.form.get('name'))
#     print (request.form.getlist('name'))
#     print (request.form.get('nickname', default='little apple'))
#     return 'welcome'
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        # user = User(form.username.data, form.email.data,
        #             form.password.data)
        # db_session.add(user)
        # flash('Thanks for registering')
        # return redirect(url_for('login'))
        return '感谢光临~'
    # return render_template('register.html', form=form)
    return '您的操作不对哦~'
if __name__ == '__main__':
    app.run(debug=True)