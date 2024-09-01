# FudanCourtReservation

FudanCourtReservation 是一个用于自动预约复旦体育场馆（如羽毛球，网球等）的 Python 脚本。该项目于本人硕士期间完成，现已修改适用于新版本，但采用的是selenium模拟操作，如需使用该项目，请根据readme自行修改部分代码及处理可能的bug。另该项目仅供学习和技术交流，造成的一切后果自负。

## 特性

- 自动登录学校体育场馆预约系统
- 自动选择和预约场馆
- 支持多种场馆类型（羽毛球，网球等）
- 支持定时任务功能，自动在指定时间进行预约
- 支持多进程多线程
- 支持多用户
- 支持捡漏模式 (如有场地空余出来，立即预约)
- 支持预约成功自动发送邮件提醒
- 支持验证码识别平台接入，需自己注册账户和充值

## 安装

1. 克隆仓库：
    ```sh
    git clone https://github.com/MinhZou/FudanCourtReservation.git
    cd FudanCourtReservation
    ```

2. 安装依赖项：
    主要是selenium的配置，下方有说明

## 使用方法

1. 配置账号信息：

   修改 `config.json` 文件，填写你的ehall登录信息和预约选项。
   
   修改 `client.py` 中接码平台的信息

3. 运行脚本：(切勿直接运行，理解代码逻辑并修改之后再运行)
   
    ```sh
    python main.py
    ```

## 备注

本人因科研繁忙无时间继续更新，欢迎相互交流和贡献代码！

目前系统的验证提交环节的验证码通过方式：

![captcha_new](pic/captcha_new.png)

返回结果：行,159,105|千,250,77|里,55,80|跛,327,127

请求填充字段为排序后汉字的数字三位数横纵坐标的结合。


rsa_text可以直接从order_page页面获取

order_page_url = 'https://elife.fudan.edu.cn/public/front/loadOrderForm_ordinary.htm?serviceContent.id={}&serviceCategory.id={}&codeStr=&resourceIds={}&orderCounts=1'.format(self.content_id, self.category_id, resource_id)
                         
<input type="hidden" id="rsa_text_" name="rsa_text_" value="xxx">

chromedriver下载地址：

https://chromedriver.storage.googleapis.com/index.html

https://googlechromelabs.github.io/chrome-for-testing/#stable

2024年7月25日 更新说明：

该项目更新后可以重新正常运行，已测试通过，但采用的是selenium模拟浏览器操作，高峰期bug会增多，慎用，且文字识别错误率有点高，进行了手动调整和增加了retry次数修改。

2024年9月1日 更新说明：

原始代码使用的环境是 python 3.7.6 + selenium 4.1.3

更新后在 python 3.11.9 + selenium 4.31.1 也可测试通过

例子：
```
[2024-09-01 12:51:46,287 - root - INFO - 27484 - 17700] 成功填充账号和密码！！！
[2024-09-01 12:51:57,654 - root - INFO - 27484 - 17700] 成功获取cookie！！！
[2024-09-01 12:51:57,654 - root - INFO - 27484 - 17700] NSC_Xfc-DpoufouTxjudi-443=xxx; JSESSIONID=xxx; iPlanetDirectoryPro=xxx;
[2024-09-01 12:52:02,609 - root - INFO - 27484 - 17700] 已预定{}
[2024-09-01 12:52:02,616 - root - INFO - 27484 - 17700] 江湾体育馆排球场1号 2024-09-03 无场地可约
[2024-09-01 12:52:02,617 - root - INFO - 27484 - 26100] 获取ID中...
[2024-09-01 12:52:03,018 - root - INFO - 27484 - 7448] 获取ID中...
[2024-09-01 12:52:10,124 - root - INFO - 27484 - 17700] 已预定{}
[2024-09-01 12:52:10,129 - root - INFO - 27484 - 17700] 江湾体育馆排球场1号-2024-09-03 08:00 可约, ID为8aecc6ce8f7d1a2501902999fe1d1cde
[2024-09-01 12:52:10,129 - root - INFO - 27484 - 17700] 江湾体育馆排球场1号-2024-09-03 09:00 可约, ID为8aecc6ce8f7d1a2501902999fe1d1ce0
[2024-09-01 12:52:10,129 - root - INFO - 27484 - 17700] 江湾体育馆排球场1号-2024-09-03 10:00 可约, ID为8aecc6ce8f7d1a2501902999fe1d1ce2
[2024-09-01 12:52:10,130 - root - INFO - 27484 - 17700] 江湾体育馆排球场1号-2024-09-03 11:00 可约, ID为8aecc6ce8f7d1a2501902999fe1d1ce4
[2024-09-01 12:52:10,131 - root - INFO - 27484 - 17700] 江湾体育馆排球场1号-2024-09-03 12:00 可约, ID为8aecc6ce8f7d1a2501902999fe1d1ce6
[2024-09-01 12:52:10,131 - root - INFO - 27484 - 17700] 江湾体育馆排球场1号-2024-09-03 13:00 可约, ID为8aecc6ce8f7d1a2501902999fe1e1ce8
[2024-09-01 12:52:10,133 - root - INFO - 27484 - 17700] 正在预定江湾体育馆排球场1号-2024-09-03 09:00

DevTools listening on ws://127.0.0.1:8118/devtools/browser/01abf806-7eb1-4e97-b98e-aa9ceb714078
Successfully retrieved valid text: 斗志昂扬
Successfully retrieved captcha results: {'志': {'left': 198, 'top': 86}, '昂': {'left': 248, 'top': 69}, '扬': {'left': 114, 'top': 81}}
Verification failed!
Retrying...
Successfully retrieved valid text: 勤学苦练
Successfully retrieved captcha results: {'人': {'left': 273, 'top': 16}, '苦': {'left': 137, 'top': 70}, '练': {'left': 263, 'top': 102}, '勤': {'left': 181, 'top': 117}, '学': {'left': 45, 'top': 131}}
Verification passed!
[2024-09-01 12:52:38,005 - root - INFO - 27484 - 17700] 已预定{'09-03-09:00': '8aecc6ce90ae440c0191abed6ea7487a'}
[2024-09-01 12:52:38,010 - root - INFO - 27484 - 17700] {'09-03-09:00': '8aecc6ce90ae440c0191abed6ea7487a'}
[2024-09-01 12:52:38,010 - root - INFO - 27484 - 17700] 09-03-09:00
[2024-09-01 12:52:38,899 - root - INFO - 27484 - 17700] 邮件发送成功！
[2024-09-01 12:52:39,679 - root - INFO - 27484 - 17700] 已预定{'09-03-09:00': '8aecc6ce90ae440c0191abed6ea7487a'}
[2024-09-01 12:52:39,683 - root - INFO - 27484 - 17700] 江湾体育馆排球场1号-2024-09-03 08:00 可约, ID为8aecc6ce8f7d1a2501902999fe1d1cde
[2024-09-01 12:52:39,684 - root - INFO - 27484 - 17700] 江湾体育馆排球场1号-2024-09-03 09:00 可约, ID为8aecc6ce8f7d1a2501902999fe1d1ce0
[2024-09-01 12:52:39,684 - root - INFO - 27484 - 17700] 江湾体育馆排球场1号-2024-09-03 10:00 可约, ID为8aecc6ce8f7d1a2501902999fe1d1ce2
[2024-09-01 12:52:39,684 - root - INFO - 27484 - 17700] 江湾体育馆排球场1号-2024-09-03 11:00 可约, ID为8aecc6ce8f7d1a2501902999fe1d1ce4
[2024-09-01 12:52:39,685 - root - INFO - 27484 - 17700] 江湾体育馆排球场1号-2024-09-03 12:00 可约, ID为8aecc6ce8f7d1a2501902999fe1d1ce6
[2024-09-01 12:52:39,686 - root - INFO - 27484 - 17700] 江湾体育馆排球场1号-2024-09-03 13:00 可约, ID为8aecc6ce8f7d1a2501902999fe1e1ce8
[2024-09-01 12:52:39,687 - root - INFO - 27484 - 17700] 已经预定 江湾体育馆排球场1号-2024-09-03 09:00
```

## 许可证

本项目采用 MIT 许可证。

