[app]

# 应用标题
title = Lottery Analysis

# 包名（小写，无空格）
package.name = lotteryapp

# 包域名
package.domain = org.example

# 版本号
version = 1.0.0

# 源码目录
source.dir = .

# 包含的文件扩展名
source.include_exts = py,png,jpg,kv,atlas,json,txt

# 排除的文件/目录
source.exclude_exts = spec

# 依赖库（必须包含 requests 及其全部依赖）
requirements = python3,kivy,requests,urllib3,charset_normalizer,certifi,idna

# 图标（可选，如果有图标文件请取消注释）
# icon.filename = %(source.dir)s/icon.png

# 屏幕方向
orientation = portrait

# 是否全屏
fullscreen = 0

# Android API 版本
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33

# 关键：网络权限（你的应用需要联网获取数据）
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# 关键：允许明文 HTTP 流量（你的数据源是 http:// 而非 https://）
# 通过 p4a 额外参数实现
android.add_aars = 
android.add_jars = 

# 架构
android.archs = arm64-v8a, armeabi-v7a

# 日志级别
android.logcat_filters = *:S python:D

# 服务（不需要后台服务，留空）
services = 

# 构建模式
android.release_artifact = apk

[buildozer]

# 日志级别
log_level = 2

# 构建目录
build_dir = ./.buildozer

# 打包输出目录
bin_dir = ./bin
