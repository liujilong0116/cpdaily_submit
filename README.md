# cpdaily_submit
  今日校园自动提交每日打卡

## 说明
  之前打卡使用的是子墨大佬写的的代码（[ZimoLoveShuang/auto-submit](https://github.com/ZimoLoveShuang/auto-submit)），感谢大佬的开源。

  不过由于登录API偶尔崩溃，结合另一个代码写了这个，代码中包含登录的实现部分，只要手机能打卡，脚本就不会挂。

同时申明，该项目自用于学习交流，不可用于商业用途，若侵权请联系我删除。

## 需修改处
* **cpdaily_submit:**
    * 在代码的44-51行，为邮箱设置。若想加入邮箱提示功能，则可进行一下编辑，不需则跳过。
    * 此处我使用的是163邮箱，mail_user填入邮箱名称，mail_pass填入授权码（[获取方法](https://jingyan.baidu.com/article/adc815139f60c2f723bf7385.html) ，目前163邮箱界面有点改变，但获取授权码的方式不变），sender填入邮箱号。

* **config.yml:**
    * users中的--user按照注释修改好信息
    * cpdaily中的defaults为每天的打卡的问题。type为题目的类型：1为直接赋值的文本类型，2为单选，3为多选。若需要提交图片，参照子墨大佬的代码加个type：4。

## 使用方法
* **本地直接运行**

  将代码下载并修改好后，安装好所需要的包直接运行cpdaily_submit.py即可
  
* **云端系统运行**

  1.注册登录腾讯云函数，链接：[腾讯云函数](https://cloud.tencent.com/login?s_url=https%3A%2F%2Fconsole.cloud.tencent.com%2Fscf%2Findex%3Frid%3D1)
  
  2.点击左侧的'层'，点击新建，层名自己设定，提交方法选择dependency.zip,添加运行环境选择python3.6
  
  3.点击左侧的'函数服务'，点击新建，函数名称自己定，运行环境选择python3.6，创建方式选择空白函数，点击下一步；将cpdaily_submit.py里的代码复制到index.py中，在index.py下方右击新建文件，取名config.yml，将修改好的的config.yml复制进去。
  
  4.确认后则可在'函数服务'的'函数管理'的'函数代码'中，点击测试，执行摘要中显示绿色的success即成功。
  
  5.为了加入更多人，在'函数服务'的'函数管理'的'函数配置'中，将执行超时时间加大，提交一个人的信息大概是2s多，设置个60或者120都行。
  
  6.在'函数服务'的'触发管理'中，新建一个触发器，触发周期选择自定义。我们学校是每晚八点打卡，我设置的是
```	
0 1 20 * * * *
```
  这个的意思就是每天20:01执行函数。
  
## 其他
觉得好用的话不妨给个star/fork呗~
  
