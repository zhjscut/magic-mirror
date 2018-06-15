// pages/music/music.js
var util = require('../../utils/util.js');
const recorderManager = wx.getRecorderManager();
const innerAudioContext = wx.createInnerAudioContext();
Page({
  data: {
    chatting_word: '',
    content: '',
    result_word: '',
    result_image: '',
    result_voice: '',
    replay_path: '',
    currentPosition: '--:--', //显示 将currentProcessNum处理成时间形式展示
    currentPositionNum: 0, //赋值 
    duration: '--:--',
    totalProcess: '--:--',
    totalProcessNum: 1,
    seek: -1,
    canSlider: false,    //是否可以滑动，防止加载音乐时 用户滑动进度条
    test: '',
    voice_src: '',
    content: '',
    answer: '',
  },
  onReady: function (e) {
    // 使用 wx.createAudioContext 获取 audio 上下文 context
    // this.audioCtx = wx.createAudioContext('myaudio') //通过audio标签的id找到音频控件
  },
  onLoad: function (options) {
    var that = this;
    recorderManager.onError(function () {
      console.log("录音失败！")
    });
    recorderManager.onStop(function (res) {
      that.setData({
        src: res.tempFilePath
      })
      console.log(res.tempFilePath)
      console.log("录音完成！")
      // 把含有歌名的音频文件上传到服务器进行识别
      const uploadTask = wx.uploadFile({
        url: 'http://120.77.207.13:1115/chat',
        // url: 'http://127.0.0.1:6007/chat',        
        filePath: that.data.src,
        name: "file",
        formData: {
          "user": "test"
        },
        success: function (res) {
          console.log('上传成功')
          var data = JSON.parse(res.data) //貌似uploadFile跟request还不太一样，request现在有自动parse，而uploadFile还没有，所以要自己补上
          console.log(data)
          that.setData({
            result_word: data['result_word'],
            result_image: data['result_image'],
            result_voice: data['result_voice'],
            content: data['content'],
          })
          util.play_music(that, data['result_voice'], '')
        }
      })
      uploadTask.onProgressUpdate(function (res) {
        console.log('上传进度', res.progress)
        console.log('已经上传的数据长度', res.totalBytesSent)
        console.log('预期需要上传的数据总长度', res.totalBytesExpectedToSend)
      })
    });

    innerAudioContext.onError((res) => {
      console.log("播放录音失败！")
    })

  },
  listenerButtonPlay: function () {
    var that = this
    util.play_music(that, this.data.music_path, this.data.chatting_word)
  },

  listenerButtonStop: function () {
    wx.stopBackgroundAudio({
    })
  },

  listenerButtonPause: function () {
    wx.pauseBackgroundAudio({
    });
  },
  searchButton: function loadXMLDoc() {  //向flask发送数据    
    if (this.data.chatting_word == '') {
      console.log('输入不能为空！')
      return
    }
    var chatting_word = this.data.chatting_word
    var that = this
    wx.request({
      url: 'http://120.77.207.13:1115/chat',
      // url: 'http://127.0.0.1:6007/chat',
      method: 'POST',
      header: {
        'content-type': 'application/x-www-form-urlencoded'
      },
      data: { chatting_word: JSON.stringify(chatting_word)},
      success: function (res) {
        console.log(chatting_word),
        console.log(res.data)
        that.setData({
          result_word: res.data['result_word'],
          result_image: res.data['result_image'],
          result_voice: res.data['result_voice'],      
          content: res.data['content'],          
        })
        util.play_music(that, res.data['result_voice'], '')
      }
    })
  },
  set_chatting_word: function (e) {
    this.setData({
      chatting_word: e.detail.value
    })
  },
  music_pause: function (e) {
    console.log('暂停')
  },
  slidechange: function (e) {
    var that = this
    // this.setData({
    // currentProcessNum: e.detail.value      
    // })
    wx.seekBackgroundAudio({
      position: e.detail.value
    })
    wx.getBackgroundAudioPlayerState({
      success: function (res) {
        that.setData({
          currentPosition: parseInt(res.currentPosition / 60) + ':' + (res.currentPosition % 60),
          currentPositionNum: res.currentPosition,
          duration: parseInt(res.duration / 60) + ':' + (res.duration % 60),
          durationNum: res.duration,
        })
      }
    })
  },

  record_start: function () {
    var that = this;
    const options = {
      duration: 10000,//指定录音的时长，单位 ms
      sampleRate: 8000,//采样率
      numberOfChannels: 1,//录音通道数
      encodeBitRate: 32000,//编码码率
      format: 'mp3',//音频格式，有效值 aac/mp3
      frameSize: 50,//指定帧大小，单位 KB
    }
    that.setData({
      chatting_word_return: ''
    })
    wx.stopBackgroundAudio({
    })
    recorderManager.start(options);
  },


  record_end: function () {
    recorderManager.stop()
  },

  replay: function () {
    var that = this
    console.log(this.data.replay_path)
    // wx.playBackgroundAudio({
    //   dataUrl: this.data.replay_path,
    // }) 
    const downloadTask = wx.downloadFile({
      url: that.data.replay_path,
      // data: {path: 'static/uploads', filename: 'audio_answer.wav'},
      success: function (res) {
        util.play_music(that, res.tempFilePath, 'answer')
        // wx.playVoice({
        // filePath: res.tempFilePath
        // })
      },
      fail: function () {
        console.log('下载失败')
      }
    })
    downloadTask.onProgressUpdate((res) => {
      console.log('下载进度', res.progress)
      console.log('已经下载的数据长度', res.totalBytesWritten)
      console.log('预期需要下载的数据总长度', res.totalBytesExpectedToWrite)
    })
  },
  testButton: function () {
    var that = this
    console.log(that.data.replay_path)
    util.play_music(that, that.data.replay_path, '')

  },
})
