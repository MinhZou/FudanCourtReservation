# FudanCourtReservation

FudanCourtReservation 是一个用于自动预约复旦体育场馆（如羽毛球，网球等）的 Python 脚本。该项目于本人硕士期间完成，仅适用于老版本，现如需使用该项目，需要自行修改最终的验证提交环节代码及可能的bug。另该项目仅供学习和技术交流，造成的一切后果自负。

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

## 使用方法

1. 配置账号信息：
    修改 `config.json` 文件，填写你的ehall登录信息和预约选项。

2. 运行脚本：(切勿直接运行，理解代码逻辑并修改之后再运行)
   
    ```sh
    python main.py
    ```

## 备注

本人因科研繁忙无时间继续更新，欢迎相互交流和贡献代码！

目前系统的验证提交环节的验证码通过方式：

![captcha_new](pic/captcha_new.png)

返回结果：行,159,105|千,250,77|里,55,80|跛,327,127

请求填充字段为排序后汉字的数字三位数横纵坐标的结合。

chromedriver下载地址：

https://chromedriver.storage.googleapis.com/index.html

https://googlechromelabs.github.io/chrome-for-testing/#stable

## 许可证

本项目采用 MIT 许可证。

