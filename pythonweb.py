#!/usr/bin/python 
# -*- coding: utf-8 -*-

from flask import Flask
from flask import request
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import urllib
import json
import re
import base64
from werkzeug.utils import secure_filename  
import os
from ffmpy import FFmpeg
from aip import AipSpeech
import sys
sys.path.append('./object')
import mobilenet
import zhengfang_crawler


def get_music_path(keyword):
    url = "http://songsearch.kugou.com/song_search_v2?callback=jQuery1124006980366032059648_1518578518932&keyword="+str(keyword)+"&page=1&pagesize=30&userid=-1&clientver=&platform=WebFilter&tag=em&filter=2&iscorrection=1&privilege_filter=0&_=1518578518934"
    content = requests.get(url)
    if re.findall('"FileHash":"(.*?)"',content.text) == []:
        music_path = '没有搜索到对应的歌曲'
        songname = '无'
#         message_answer = '没有搜索到对应的歌曲'
#         result_tts = client.synthesis(message_answer, 'zh', 1, {'vol': 5, 'per': 0})
#         with open(filename_answer, 'wb') as f:
#             f.write(result_tts)
    else:
        filehash = re.findall('"FileHash":"(.*?)"',content.text)[0]
        songname = re.findall('"SongName":"(.*?)"',content.text)[0].replace("<\\/em>","").replace("<em>","") #即将播放的歌曲名
        hash_url = "http://www.kugou.com/yy/index.php?r=play/getdata&hash="+filehash
        hash_content = requests.get(hash_url)
        play_url = re.findall('"play_url":"(.*?)"',hash_content.text)
        play_url = ' '.join(play_url)
        real_download_url = play_url.replace("\\","")
        music_path = real_download_url
#         print("客官，请稍等一下，好音乐马上呈上！")
        # with open(songname+".mp3","wb")as fp:
#         with open(filename_music,"wb")as fp:
#             fp.write(requests.get(real_download_url).content)
#         print('下载完成，敬请收听！')
#         play(filename_music)
    return music_path, songname



# For a given file, return whether it's an allowed type or not
def allowed_file(filename):  
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# 读取文件
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()     
    
APP_ID = '11169887'
API_KEY = 'TQypLIsDnr4XwzfyKGLqMsfD'
SECRET_KEY = 'bc5efee36b796c2b467dba12c2a080b0'    
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY) 

    
    
    
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'  
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif', 'mp3'])


@app.route('/', methods =['GET','POST'])
def hello_world():

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
    req = urllib.request.Request(url='http://www.weather.com.cn/weather/101010100.shtml', headers=headers)
    resp = urlopen(req)

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


    return weather #json.dumps(weather)


@app.route('/receive', methods=['GET','POST'])
def receive():

    postdata = request.values.get('clickdata')

    print(json.loads(postdata))  # 注意这里哈

    #postdata = json.loads(postdata)  # 注意这里哈，变回DICT格式，亲切ing

    return "46575"

@app.route('/music', methods=['GET','POST'])
def listen_music():
    try:
        upload_file = request.files['file']
        print('收到录音文件')
        if upload_file and allowed_file(upload_file.filename):
            filename = 'from_music.mp3'
            save_filename = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
            print(save_filename)
            upload_file.save(save_filename)
            output_filename = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], 'decoded.wav') #各个模块做转码得到的文件可以放在同一个文件上
            if os.path.exists(output_filename): #ffmpy.FFmpeg对象用于音视频转码，如果输出文件名已存在，那么run()方法将报错，因此run之前应先检查输出文件是否存在，若存在应先移除
                os.remove(output_filename)
            from ffmpy import FFmpeg
            ff = FFmpeg(
               inputs={save_filename: None},
               outputs={output_filename: None}
            )
            ff.run()
            #语音转文字
            result_stt = client.asr(get_file_content(output_filename), 'wav', 8000, {'dev_pid': '1537'})
            if result_stt['err_msg'] != 'success.':
                music_name = '没有识别到内容' 
                music_path = ''
            else:
                music_name_request = result_stt['result'][0].replace('，','') #str类型即可
                print(music_name_request)
                music_path, music_name = get_music_path(music_name_request) #music_path是json格式的音频url，可以直接返回
    except: #可能是手动输入的请求数据        
        music_name_request = json.loads( request.values.get('music_name') )
        music_path, music_name = get_music_path(music_name_request)
#         postdata = json.loads(postdata)  # 注意这里哈，变回DICT格式，亲切ing
    finally: 
        result = {'music_path': music_path, 'music_name': music_name}
        print(result)
        print(json.dumps(result))
        return json.dumps(result)


@app.route('/file', methods=['GET','POST'])
def collect_file():
    upload_file = request.files['file']
    if upload_file and allowed_file(upload_file.filename):
        filename = secure_filename(upload_file.filename)
#         upload_file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
        upload_file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
        return 'hello, '+request.form.get('name', 'little apple')+'. success'
    else:
        return 'hello, '+request.form.get('name', 'little apple')+'. failed'
    
    file = request.get_data()
    file = request.files['file']
    print(file)

    return 'done.'

@app.route('/upload', methods=['POST'])
def upload():  
    upload_file = request.files['file']
    if upload_file and allowed_file(upload_file.filename):
        filename = secure_filename(upload_file.filename)
#         upload_file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
        upload_file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
        return 'hello, '+request.form.get('name', 'little apple')+'. success'
    else:
        return 'hello, '+request.form.get('name', 'little apple')+'. failed'

@app.route('/jw2005', methods=['POST'])
def login():  
    json_data = request.get_json()
    username = json_data['username']
    password = json_data['password']
    crawler = zhengfang_crawler.ZhengfangCrawler(username, password)
    isSuccess, _ = crawler._login()
    res = json.dumps({"isSuccess": isSuccess})
    return res  

@app.route('/jw2005/query_score', methods=['POST'])
def query_scores():
    json_data = request.get_json()
    username = json_data['username']
    password = json_data['password']
    crawler = zhengfang_crawler.ZhengfangCrawler(username, password)
    res = crawler.get_scores() 
    res = json.dumps(res)
    return res  



@app.route('/object', methods=['POST'])
def objects():  
    upload_file = request.files['file']
    if upload_file and allowed_file(upload_file.filename):
        filename = secure_filename(upload_file.filename)
        upload_file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
        res = mobilenet.predict(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
        res = json.dumps(res)
        return res
    else:
        return 'hello, '+request.form.get('name', 'little apple')+'. failed'
    
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6007, debug=True) #6007端口，浏览器要访问1115端口