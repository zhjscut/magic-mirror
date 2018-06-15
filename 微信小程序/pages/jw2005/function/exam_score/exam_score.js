var order = ['red', 'yellow', 'blue', 'green', 'red']
Page({
  data: {
    toView: 'red',
    scrollTop: 100,
    listData: [],
  },
  upper: function (e) {
    console.log(e)
  },
  lower: function (e) {
    console.log(e)
  },
  scroll: function (e) {
    console.log(e)
  },
  tap: function (e) {
    for (var i = 0; i < order.length; ++i) {
      if (order[i] === this.data.toView) {
        this.setData({
          toView: order[i + 1]
        })
        break
      }
    }
  },
  tapMove: function (e) {
    this.setData({
      scrollTop: this.data.scrollTop + 10
    })
  },
  onLoad: function () {
    var that = this;
    var query_data;
    wx.getStorage({
      key: 'studentInfo',
      success: function(res) {
        wx.request({
          // url: "http://localhost:6007/jw2005/query_score",
          url: "http://120.77.207.13:1115/jw2005/query_score",
          data: JSON.stringify(res.data),
          header: { "content-type": "application/json" },
          method: "POST",
          success: function (res) {
            console.log(res.data);
            that.setData({ listData: res.data });
          },
          fail: function (res) {
            console.log('Failed to post username and passowrd.');
          },
        });

      },
    });
  }
})