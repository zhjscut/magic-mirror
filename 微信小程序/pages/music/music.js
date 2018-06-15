// pages/music/music.js
var util = require('../../utils/util.js'); 
const recorderManager = wx.getRecorderManager();
const innerAudioContext = wx.createInnerAudioContext();
Page({
  data:{
    music_name: '',
    music_path: '',   
    music_name_return: '',
    content: '',
    replay_path: '',
    audio_answer_path: '',
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
          url: 'http://120.77.207.13:1115/music', 
          // url: 'http://127.0.0.1:6007/music', 
          filePath: that.data.src,
          name: "file",
          formData: {
            "user": "test"
          },
          success: function (res) {
            console.log('上传成功')
            var data = JSON.parse(res.data) //貌似uploadFile跟request还不太一样，request现在有自动parse，而uploadFile还没有，所以要自己补上
            console.log(data)
            console.log(data['music_path'], data['music_name'])
            that.setData({
              music_path: data['music_path'],
              music_name_return: data['music_name'],
              content: data['content'],
              replay_path: data['replay_path'],
            })      
            util.play_music(that, data['music_path'], data['music_name'])      
          }
        })
        uploadTask.onProgressUpdate(function(res) {
          console.log('上传进度', res.progress)
          console.log('已经上传的数据长度', res.totalBytesSent)
          console.log('预期需要上传的数据总长度', res.totalBytesExpectedToSend)
        })
    });

    innerAudioContext.onError((res) => {
      console.log("播放录音失败！")
    })

  },
  listenerButtonPlay:function(){
    var that = this
    util.play_music(that, this.data.music_path, this.data.music_name)
  },

  listenerButtonStop:function(){
    wx.stopBackgroundAudio({
    })
  },

  listenerButtonPause:function(){
    wx.pauseBackgroundAudio({ 
    });
  },
  searchButton: function loadXMLDoc() {  //向flask发送数据    
    if (this.data.music_name == '')
      {
        console.log('歌曲名不能为空！')
        return
      }
    var music_name = this.data.music_name
    var that = this
    wx.request({
      url: 'http://120.77.207.13:1115/music',
      // url: 'http://127.0.0.1:6007/music',
      method: 'POST',
      header: {
        'content-type': 'application/x-www-form-urlencoded'
      },
      data: { music_name: JSON.stringify(music_name), name: JSON.stringify('aaa')},
      success: function (res) { 
        console.log('您提交的歌曲名为：', music_name, '已经提交数据到数据库') 
        console.log(res.data)
        that.setData({
          music_path: res.data['music_path'],
          music_name_return: res.data['music_name']
        })
        util.play_music(that, res.data['music_path'], res.data['music_name'])
      }
    })
  },
  set_music_name: function (e) {
    this.setData({
      music_name: e.detail.value
    })    
  },
  music_pause: function (e){
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
      music_name_return: ''
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
    console.log(that.data.replay_path)
    util.play_music(that, that.data.replay_path, '')
    // const downloadTask = wx.downloadFile({
    //   url: that.data.replay_path,
    //   // data: {path: 'static/uploads', filename: 'audio_answer.wav'},
    //   success: function (res) {
    //     util.play_music(that, res.tempFilePath, 'answer')
    //     // wx.playVoice({
    //       // filePath: res.tempFilePath
    //     // })
    //   },
    //   fail: function(){
    //     console.log('下载失败')
    //   }
    // })
    // downloadTask.onProgressUpdate((res) => {
    //   console.log('下载进度', res.progress)
    //   console.log('已经下载的数据长度', res.totalBytesWritten)
    //   console.log('预期需要下载的数据总长度', res.totalBytesExpectedToWrite)
    // })
  },
  testButton: function(){
    var that = this
    console.log(that.data.replay_path)
    util.play_music(that, that.data.replay_path, '')

  },
  // download: function(){
  //   wx.request({
  //     // url: 'http://120.77.207.13:1115/download1',
  //     url: 'http://120.77.207.13:1115/download/filename=decoded.wav',
  //     method: 'GET',
  //     // method: 'POST', 
  //     header: {
  //       'content-type': 'application/x-www-form-urlencoded'
  //     },
  //     // data: {path: JSON.stringify('static/uploads/'), filename: JSON.stringify('decoded.wav')},
  //     success: function(res){
  //       console.log(res.data)
  //     }
  //   })
  // },
})
