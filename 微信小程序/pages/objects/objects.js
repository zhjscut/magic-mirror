// pages/objects/objects.js

var descriptionTitle = '说明';
var descriptionContent = '上传一张图片，看看 AI 能不能认出来！本算法使用两种算法，分别是 Kaiming He 于 2015 年提出来的 ResNetV2 和 Google 于 2017 年提出的 MobleNet。'
Page({
  data: {
    tempFilePaths: '',
    imwidth: 0,
    imheight: 0,
    title: descriptionTitle,
    content: descriptionContent,
    isChooseHidden: false,
    isIdentifyHidden: true
  },
  onLoad: function () {
  },
  chooseAImage: function () {
    var that = this;
    wx.chooseImage({
      count: 1, // 默认9  
      sizeType: ['original', 'compressed'], // 可以指定是原图还是压缩图，默认二者都有  
      sourceType: ['album', 'camera'], // 可以指定来源是相册还是相机，默认二者都有  
      success: function (res) {
        wx.getImageInfo({
          src: res.tempFilePaths[0],
          success: function (res) {
            imwidth: res.width;
            imheight: res.height;
            that.setData({ isChooseHidden: true, isIdentifyHidden: false});
          }
        })
        // 返回选定照片的本地文件路径列表，tempFilePath可以作为img标签的src属性显示图片  
        that.setData({
          tempFilePaths: res.tempFilePaths,
        })
      }
    }) // end wx.chooseImage
  }, // end chooseAImage
  identifyImage: function(){
    var that = this;
    console.log(that.data.tempFilePaths[0]);
    wx.uploadFile({
      url: 'http://120.77.207.13:1115/object',
      filePath: that.data.tempFilePaths[0],
      name: 'file',
      formData: {
        'User': 'test'
      },
      success: function(res){
        var data = JSON.parse(res.data);
        console.log(data);
        var res = "";
        var topi;
        for(var i=0; i<5; i++){
          topi = "top" + (i + 1);
          res = res + "Rank " + (i+1) + " " + data[topi]["label"] + " " + data[topi]["confidence"] + '\n';
        }

        that.setData({
          content: res, title: "结果", isChooseHidden: false, isIdentifyHidden: true});
        console.log(res);
      }, //end success
      fail: function(res){
        that.setData({title: descriptionTitle, content: descriptionContent, isChooseHidden: false, isIdentifyHidden :true, tempFilePaths: ''});
      }
    })
  }
})  