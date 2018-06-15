Page({
  data: {
    focus: false,
    inputValue: '',
    clickdata: '',
    weatherdata: ''
  },
  
  bindKeyInput: function (e) {
    this.setData({
      inputValue: e.detail.value
    })
    wx.request({
      url: 'http://127.0.0.1:5000/receive',
      data: { clickdata: JSON.stringify(e.detail.value) },
      method: 'POST',
      header: { 'content-type': 'application/x-www-form-urlencoded' },
      success: function (data) { console.log('已经提交数据到数据库') }
    })
  },
  
/*
  bindKeyInput: function (e) {
    this.setData({
      inputValue: e.detail.value
    })
    wx.request({
      url: 'http://127.0.0.1:5000/receive',
      data: JSON.stringify(e.detail.value),
      method: 'POST',
      header: { 'content-type': 'application/x-www-form-urlencoded' },
      success: function (res) {
        console.log('submit success');
      },
      fail: function (res) {
        console.log('submit fail');
      },
      complete: function (res) {
        console.log('submit complete');
      }
    }) 
  },
*/ 
  clickButton: function loadXMLDoc() {  //向flask发送数据
    var inputValue
    wx.request({
      url: 'http://127.0.0.1:5000/receive',
      method: 'POST',
      header: {
        'content-type': 'application/x-www-form-urlencoded'
      },
      data: { clickdata: JSON.stringify('天路') },

      success: function (data) { console.log('已经提交数据到数据库') }
    })
  },
  
/*
  clickButton: function(e) {  //向flask发送数据
    wx.request({
      url: 'http://127.0.0.1:5000/receive',
      data: e.detail.value,
      method: 'POST',
      header: { 'content-type': 'application/x-www-form-urlencoded' },
      success: function (res) {
        console.log('submit success');
      },
      fail: function (res) {
        console.log('submit fail');
      },
      complete: function (res) {
        console.log('submit complete');
      }
    })  
  },
  */


  clickButton2: function loadXMLDoc(){  //获取flask数据
    var that = this
    var weather
    wx.request({
      url: 'http://127.0.0.1:5000/', //仅为示例，并非真实的接口地址
      data: {
        weather
      },
      header: {
        'content-type': 'application/json' // 默认值
      },
      success: function (res) {
        console.log(res.data);
        that.setData({
          weatherdata: res.data
        })
      }
      
    })
      
  }

})


