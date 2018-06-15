var util = require('../../utils/util.js'); 
Page({
  data:{
    username: '',
    password: '',
    content: '',
    answer: '',
  },
  set_username: function(e){
    this.setData({
      username: e.detail.value
    })
  },
  set_password: function (e) {
    this.setData({
      password: e.detail.value
    })
  },
  login: function (e) {
    var that = this
    /*
     wx.request({
       url: 'http://120.77.207.13:1115/jw2005',
       method: 'POST',
       header: {
         'content-type': 'application/x-www-form-urlencoded'
       },
       data: { username: JSON.stringify(that.data.username), password: JSON.stringify(that.data.password)},
       success: function (res) {
         console.log(res.data)
         // console.log(res.data['music_path'])
         that.setData({
           music_path: res.data
         })
       }
     })
     */
    wx.navigateTo({
      url: '/pages/jw2005/function/function'
    })
  } 
})