var common = require('common.js') //require加载模块

Page({
  data: {
    weather: {}
  },
  onLoad: function () {
    var that = this;
    common.loadWeatherData(function (data) {
      that.setData({
        weather: data
      });
    });
  }
})