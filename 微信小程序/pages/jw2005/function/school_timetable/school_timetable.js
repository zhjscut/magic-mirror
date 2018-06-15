var order = ['red', 'yellow', 'blue', 'green', 'red']
Page({
  data: {
    toView: 'red',
    scrollTop: 100,
    listData: [
      { "code": "01", "text": "text1", "type": "type1", "other": "other1" },
      { "code": "02", "text": "text2", "type": "type2", "other": "other2" },
      { "code": "03", "text": "text3", "type": "type3", "other": "other3" },
      { "code": "04", "text": "text4", "type": "type4", "other": "other4" },
      { "code": "05", "text": "text5", "type": "type5", "other": "other5" },
      { "code": "06", "text": "text6", "type": "type6", "other": "other6" },
      { "code": "07", "text": "text7", "type": "type7", "other": "other7" }
    ],
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
    console.log('onLoad')
  } 
})