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


# 读取文件
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()     


def get_result_chat(result_stt):
    ses = requests.Session()
    turing_url = 'http://openapi.tuling123.com/openapi/api/v2'
    header1 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
            }  
    data =  {
                "reqType":0,
                "perception": {
                    "inputText": {
                        "text": result_stt
                    },
                    "selfInfo": {
                        "location": {
                            "city": "广州",
                            "province": "广东",
                        }
                    }
                },
                "userInfo": {
                    "apiKey": "afdc9e3dff3b4cb4b5a3df6fed37c7bc",
                    "userId": "123456"
                }
            }
    response = ses.post(turing_url, headers = header1, data=json.dumps(data)) #要求是json格式，所以要先转成json
    result_chat = json.loads(response.text) #返回的是dict的json形式，因此无需解析，只要将json转回到python对象即可

    result_word = ''
    result_image = ''
    for i in range(len(result_chat['results'])):
        resultType = result_chat['results'][i]['resultType']
        if resultType == 'text':
            result_word = result_chat['results'][i]['values'][resultType]
            print(result_chat['results'][i]['values'][resultType])
        else: #好像只有text和image两种类型
            result_image = result_chat['results'][i]['values'][resultType]
            print(result_image)    
    return result_word, result_image

