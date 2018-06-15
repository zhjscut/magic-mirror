const formatTime = date => {
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hour = date.getHours()
  const minute = date.getMinutes()
  const second = date.getSeconds()

  return [year, month, day].map(formatNumber).join('/') + ' ' + [hour, minute, second].map(formatNumber).join(':')
}

const formatNumber = n => {
  n = n.toString()
  return n[1] ? n : '0' + n
}
function play_music(that, music_path, music_name){
  // that是页面对象指针this，传入音乐路径和音乐名称即可播放，内含播放进度、时间总长以及一个可拖拽的进度条，需要与wxml文件配合
  wx.playBackgroundAudio({
    dataUrl: music_path,
    title: music_name,
      //  图片地址  
      // coverImgUrl: 'http://i.gtimg.cn/music/photo/mid_album_90/a/F/000QgFcm0v8WaF.jpg'
  })
  var backgroundAudioManager = wx.getBackgroundAudioManager()
  backgroundAudioManager.onTimeUpdate(function (callback) {
    that.setData({
      currentPositionNum: backgroundAudioManager.currentTime,
      currentPosition: parseInt(backgroundAudioManager.currentTime / 60) + ':' + parseInt(backgroundAudioManager.currentTime % 60),
      duration: parseInt(backgroundAudioManager.duration / 60) + ':' + parseInt(backgroundAudioManager.duration % 60),
      durationNum: backgroundAudioManager.duration,
    })
  })
  wx.getBackgroundAudioPlayerState({
    success: function (res) {
      // success  
      //duration  选定音频的长度（单位：s），只有在当前有音乐播放时返回  
      // console.log('duration:' + res.duration)
      if (res.status == 1) {
        that.setData({
          currentPosition: parseInt(res.currentPosition / 60) + ':' + (res.currentPosition % 60),
          currentPositionNum: res.currentPosition,
          duration: parseInt(res.duration / 60) + ':' + (res.duration % 60),
          durationNum: res.duration,
        })
      }
      // console.log('currentPosition:' + res.currentPosition)
      //status    播放状态（2：没有音乐在播放，1：播放中，0：暂停中）  
      // console.log('status:' + res.status)
      // console.log('downloadPercent:' + res.downloadPercent)
      //dataUrl   歌曲数据链接，只有在当前有音乐播放时返回   
      // console.log('dataUrl:' + res.dataUrl)
    },
  })
}


module.exports = {
  formatTime: formatTime,
  play_music: play_music
}
