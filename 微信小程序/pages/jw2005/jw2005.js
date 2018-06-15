var util = require('../../utils/util.js');
Page({
  data: {
    username: '',
    password: '',
    content: '',
    answer: '',
    isLoading: false,
  },
  set_username: function (e) {
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
    var that = this;
    if (that.data.username == "" || that.data.password == "") {
      wx.showModal({
        title: '提示',
        content: "请输入用户名和密码"
      });
      return;
    }
    that.setData({ isLoading: true });
    wx.request({
      url: 'http://120.77.207.13:1115/jw2005',
      method: 'POST',
      header: {
        'content-type': 'application/json'
      },
      data: JSON.stringify({ "username": that.data.username, "password": that.data.password }),
      success: function (res) {
        if (res.data["isSuccess"]) {
          wx.setStorage({
            key: 'studentInfo',
            data: { "username": that.data.username, "password": that.data.password },
          })
          wx.navigateTo({
            url: '/pages/jw2005/function/function'
          });
        } else {
          wx.showModal({
            title: '登录失败',
            content: '请检查密码是否正确',
          });
        }
      },
      complete: function (res) {
        that.setData({ isLoading: false });
      }
    });
  }
})