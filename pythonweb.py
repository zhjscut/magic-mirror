#!/usr/bin/python 
# -*- coding: utf-8 -*-

from flask import Flask, request, send_from_directory, url_for
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
import time
import sys
sys.path.append('./object')
import mobilenet
import zhengfang_crawler
import magic_mirror_voice


# For a given file, return whether it's an allowed type or not
def allowed_file(filename):  
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


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
#         print(url_for('.static/uploads/',_external=True,filename='from_music.mp3'))

        upload_file = request.files['file']
        if upload_file and allowed_file(upload_file.filename):
            filename = 'from_music.mp3'
            save_filename = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
            upload_file.save(save_filename)
            output_filename = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], 'decoded.wav') #各个模块做转码得到的文件可以放在同一个文件上
            if os.path.exists(output_filename): #ffmpy.FFmpeg对象用于音视频转码，如果输出文件名已存在，那么run()方法将报错，因此run之前应先检查输出文件是否存在，若存在应先移除
                os.remove(output_filename)
#            在ffmpeg里对应的设置方式分别是：   -ar rate 设置采样率    -ac channels 设置声道数
            ff = FFmpeg(
               inputs={save_filename: None},
               outputs={output_filename: None}
            )
            ff.run()
            #语音转文字
            result_stt = client.asr(magic_mirror_voice.get_file_content(output_filename), 'wav', 8000, {'dev_pid': '1537'})
            if result_stt['err_msg'] != 'success.':
                music_name = ''
                music_path = ''
                content = '没有识别到内容'
            else:
                music_name_request = result_stt['result'][0].replace('，','') #str类型即可
                content = music_name_request
                music_path, music_name = magic_mirror_voice.get_music_path(music_name_request) #music_path是json格式的音频url，可以直接返回
            replay_filename = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) 
#             replay_path = 'http://120.77.207.13:1115/replay/filename=decoded_' + replay_filename + '.wav'
            replay_path = 'http://127.0.0.1:6007/replay/filename=decoded_' + replay_filename + '.wav'
            print(replay_path)
            result = {'music_path': music_path, 'music_name': music_name, 'content': content, 'replay_path': replay_path}
    except Exception as e:#可能是手动输入的请求数据   
        print('异常信息 in listen_music() try：', e)
        music_name_request = json.loads( request.values.get('music_name') )
        music_path, music_name = magic_mirror_voice.get_music_path(music_name_request)
        result = {'music_path': music_path, 'music_name': music_name}

    finally: 
        print(type(music_name))
        print(result)
        print(json.dumps(result))
        return json.dumps(result)

@app.route('/chat', methods=['GET','POST'])
def chat():
    try:
        upload_file = request.files['file']
        if upload_file and allowed_file(upload_file.filename):
            filename = 'from_chat.mp3'
            save_filename = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
            upload_file.save(save_filename)
            output_filename = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], 'decoded.wav') #各个模块做转码得到的文件可以放在同一个文件上
            if os.path.exists(output_filename): #ffmpy.FFmpeg对象用于音视频转码，如果输出文件名已存在，那么run()方法将报错，因此run之前应先检查输出文件是否存在，若存在应先移除
                os.remove(output_filename)
    #            在ffmpeg里对应的设置方式分别是：   -ar rate 设置采样率    -ac channels 设置声道数
            ff = FFmpeg(
               inputs={save_filename: None},
               outputs={output_filename: None}
            )
            ff.run()
            #语音转文字
            result_stt = client.asr(magic_mirror_voice.get_file_content(output_filename), 'wav', 8000, {'dev_pid': '1537'})  
            if result_stt['err_msg'] != 'success.':
                result_word = '你怎么不说话'
                result_image = ''
                result_voice = ''
                content = '没有识别到内容'
            else:            
                result_word, result_image = magic_mirror_voice.get_result_chat(result_stt['result'][0]) #获得图灵机器人的回复，可能包含文字和图片信息
            result_tts = client.synthesis(result_word, 'zh', 1, {'vol': 5, 'per': 4}) #把文字回复转成语音回复
            answer_filename = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], 'answer.wav')
            if not isinstance(result_tts, dict):
                with open(answer_filename, 'wb') as f:
                    f.write(result_tts)    
            result_voice_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) 
#             result_voice = 'http://120.77.207.13:1115/replay/filename=answer_' + result_voice_time                    
            result_voice = 'http://127.0.0.1:6007/replay/filename=answer_' + result_voice_time + '.wav'
            
    except Exception as e:#可能是手动输入的请求数据   
        print('异常信息 in listen_music() try：', e)
        content = '' #无语音输入，识别结果为空
        chatting_word = json.loads( request.values.get('chatting_word') )
        result_word, result_image = magic_mirror_voice.get_result_chat(chatting_word) #获得图灵机器人的回复，可能包含文字和图片信息
        result_tts = client.synthesis(result_word, 'zh', 1, {'vol': 5, 'per': 4}) #把文字回复转成语音回复
        answer_filename = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], 'answer.wav')
        if not isinstance(result_tts, dict):
            with open(answer_filename, 'wb') as f:
                f.write(result_tts)   
        result_voice_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) 
#             result_voice = 'http://120.77.207.13:1115/replay/filename=answer_' + result_voice_time                    
        result_voice = 'http://127.0.0.1:6007/replay/filename=answer_' + result_voice_time + '.wav'   

    result = {'result_word': result_word, 'result_image': result_image, 'result_voice': result_voice, 'content': content}
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
def object():  
    upload_file = request.files['file']
    if upload_file and allowed_file(upload_file.filename):
        filename = secure_filename(upload_file.filename)
        upload_file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
        res = mobilenet.predict(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
        res = json.dumps(res)
        return res
    else:
        return 'hello, '+request.form.get('name', 'little apple')+'. failed'

# get方法：查询当前路径下的所有文件
@app.route('/getfiles', methods=['get','post'])
def getfiles():
    fpath = request.values.get('fpath', '') #获取用户输入的目录
    fpath = json.loads(fpath) #解JSON
    if os.path.isdir(os.path.join(app.root_path, fpath)):
        filelist = os.listdir(fpath)
        files = [file for file in filelist if os.path.isfile(os.path.join(fpath, file))]
    return '{"files":"%s"}' % files    

#get方法：指定目录下载文件
@app.route('/download', methods=['get','post'])
def download(path):
    print(request.values)
    fpath = request.values.get('path', '') #获取文件路径
    fpath = json.loads(fpath) #解JSON
    fname = request.values.get('filename', '')  #获取文件名
    fname = json.loads(fname) 
    print(fname, fpath)
    print(os.path.isdir(os.path.join(app.root_path, fpath)))
    print(os.path.isfile(os.path.join(fpath,fname)))
    print(os.path.join(app.root_path, fpath))
    print(os.path.join(fpath,fname))
    if fname.strip() and fpath.strip():

        if os.path.isfile(os.path.join(fpath,fname)) and os.path.isdir(os.path.join(app.root_path, fpath)):
            return send_from_directory(fpath, fname, as_attachment=True) #返回要下载的文件内容给客户端
        else:
            return '{"msg":"参数不正确"}'
    else:
        return '{"msg":"请输入参数"}'
    
@app.route('/replay/<filename>')
def show_user_profile(filename):
    # 合法参数形如filename=1.wav
    try:
        fname = filename.split('=')[1]
#         print(filename.split('=')[0])
#         print(fname.split('.')[0])
#         print(fname.split('.')[1])
        if filename.split('=')[0] == 'filename' and (fname.split('.')[1] == 'wav' or fname.split('.')[1] == 'mp3') and ('answer' in fname.split('.') [0] or 'decoded' in fname.split('.')[0]):
            filepath = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
            if 'answer' in fname.split('.')[0]:
                filename_type = 'answer'
            elif 'decoded' in fname.split('.')[0]:
                filename_type = 'decoded'
            input_filename = filepath + filename_type +'.wav' #因为手机端播放不了wav文件，所以要转成mp3文件
            output_filename = filepath + filename_type + '.mp3'
            print(output_filename)
            if os.path.exists(output_filename):
                os.remove(output_filename)
            ff = FFmpeg(
               inputs={input_filename: None},
               outputs={output_filename: None}
             )
            ff.run()
            return send_from_directory(filepath, filename_type+'.mp3', as_attachment=True) #返回要下载的文件内容给客户端
        else:
            return json.dumps({'answer': 'Illegal parameter format'})
    except:
        return json.dumps({'answer': 'Illegal parameter format'})

@app.route('/test/<filename>')
def test(filename):
    # show the user profile for that user
    fname = filename.split('=')[1]
    print(fname)
    return filename
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6007, debug=True) #6007端口，浏览器要访问1115端口






