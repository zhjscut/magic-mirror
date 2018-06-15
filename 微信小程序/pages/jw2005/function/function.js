Page({
  data:{
    name: '张浩健',
    content: '',
    answer: '',
  },
  empty_classroom: function(e){
    wx.navigateTo({
      url: '/pages/jw2005/function/empty_classroom/empty_classroom'
    })
  },
  exam_score: function (e) {
    wx.navigateTo({
      url: '/pages/jw2005/function/exam_score/exam_score'
    })
  },
  school_timetable: function (e) {
    wx.navigateTo({
      url: '/pages/jw2005/function/school_timetable/school_timetable'
    })
  }
})