var dateTimePicker = require('../../../../utils/dateTimePicker.js');

Page({
  data: {
    show: false,//控制下拉列表的显示隐藏，false隐藏、true显示
    show_xq: false,
    show_jslb: false,
    selectData: ['1', '2', '3', '4', '5', '6'],//下拉列表的数据
    xqData: ['北校区', '南校区'],
    jslbData: ['多媒体教室', '制图室'],
    index: 0, //选择的下拉列表下标
    index_xq: 1,
    index_jslb: 1,
    multiIndex: [0, 0, 0, 0],
    start_week: 1,
    start_day_index: 0,
    weeks: dateTimePicker.get_weeks(1, 20),
    days: dateTimePicker.get_days(),
    warning: '',
  },
  // 点击下拉显示框
  selectTap_xq() {
    this.setData({
      show_xq: !this.data.show_xq //!表示取反
    });
  },
  selectTap_jslb() {
    this.setData({
      show_jslb: !this.data.show_jslb
    });
  },
  // 点击下拉列表
  optionTap_xq(e) {
    let Index_xq = e.currentTarget.dataset.index;//获取点击的下拉列表的下标
    this.setData({
      index_xq: Index_xq,
      show_xq: !this.data.show_xq
    });
  },
  optionTap_jslb(e) {
    let Index_jslb = e.currentTarget.dataset.index;//获取点击的下拉列表的下标
    this.setData({
      index_jslb: Index_jslb,
      show_jslb: !this.data.show_jslb
    });
  },
  bindMultiPickerChange: function (e) {
    var value = e.detail.value
    console.log('picker发送选择改变，携带值为', e.detail.value)
    if (e.detail.value[1] == 0 && e.detail.value[3] < this.data.start_day_index){
      this.setData({
        warning: '只可以看到本日及之后的空教室情况哦~',
        multiIndex: [0, 0, 0, 1],
      })
    }
    else{
      this.setData({
        warning: '',
        multiIndex: e.detail.value,
      })
    }
    // this.setData({
    //   multiIndex: e.detail.value,
    // })
  },  
  onLoad: function (options) {
    var that = this
    // var dateArray = [
    //   [{ id: 0, name: '第' }], this.data.weeks, [{ id: 0, name: '周  周' }], this.data.days
    // ]
    // that.setData({
    //   dateArray: dateArray
    // })
    wx.request({
      url: 'http://120.77.207.13:1115/jw2005/empty_classroom',
      method: 'POST',
      header: {
        'content-type': 'application/x-www-form-urlencoded'
      },
      data: { initial: JSON.stringify('0')},
      success: function (res) {
        console.log(res.data)
        var dateArray = [
          [{ id: 0, name: '第' }], dateTimePicker.get_weeks(parseInt(res.data['week']), 20), [{ id: 0, name: '周  周' }], dateTimePicker.get_days()
        ]
        that.setData({
          start_week: res.data['week'],
          start_day_index: parseInt(res.data['day']),
          weeks: dateTimePicker.get_weeks(parseInt(res.data['week']), 20),
          dateArray: dateArray,
          multiIndex: [0, 0, 0, parseInt(res.data['day'])],
        })
      }
    })
  },
  search: function(){
    wx.request({
      url: 'http://120.77.207.13:1115/jw2005/empty_classroom',
      method: 'POST',
      header: {
        'content-type': 'application/x-www-form-urlencoded'
      },
      // 未完待续
      data: { initial: JSON.stringify('1')},
      success: function (res) {
        console.log(res.data)
        var dateArray = [
          [{ id: 0, name: '第' }], dateTimePicker.get_weeks(parseInt(res.data['week']), 20), [{ id: 0, name: '周  周' }], dateTimePicker.get_days()
        ]
        that.setData({
          start_week: res.data['week'],
          start_day_index: parseInt(res.data['day']),
          weeks: dateTimePicker.get_weeks(parseInt(res.data['week']), 20),
          dateArray: dateArray,
          multiIndex: [0, 0, 0, parseInt(res.data['day'])],
        })
      }
    })
  },
})