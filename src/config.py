#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""配置文件：
    1. 用户可选配置
    2. 网站url及xpath
"""

# 用户可选配置
USER_CONFIG = {
    "chrome_mute": True,  # 浏览器静音
    "hide_page": False,  # 浏览器隐藏，浏览器如果隐藏则不算有效阅读，不建议修改
    "read_time": 130,  # 一篇文章的阅读时间，不建议修改
    "video_time": 185,  # 一部视频的观看时间，不建议修改
}

WEBSITE = {
    "url": {
        "main": r"https://www.xuexi.cn/",
        "login": r"https://pc.xuexi.cn/points/login.html",
        "my_points": r"https://pc.xuexi.cn/points/my-points.html",
    },
    "xpath": {
        "login": {
            "login_btn": '//*[@id="root"]/div/header/div[2]/div[2]/a[2]',
            "login_text": '//*[@class="ddlogintext"]',
            "success": '//*[@id="app"]/div/div[2]/div/div/div[1]/div/a[3]/div/div[2]/div[1]/span',
            "login_success": '//*[@id="root"]/div/header/div[2]/div[2]/span/span',
        },
        "points": {
            # 文章个数够，时长肯定够，故文章以个数为准；视频个数够，时长却不一定够，故视频以时长为准
            # 时长积分判断
            # "read_points": '//*[@id="app"]/div/div[2]/div/div[3]/div[2]/div[4]/div[2]/div[1]/div[2]',
            "video_points": '//*[@id="app"]/div/div[2]/div/div[3]/div[2]/div[5]/div[2]/div[1]/div[2]',
            # 个数积分判断
            "read_points": '//*[@id="app"]/div/div[2]/div/div[3]/div[2]/div[2]/div[2]/div[1]/div[2]',
            # "video_points": '//*[@id="app"]/div/div[2]/div/div[3]/div[2]/div[3]/div[2]/div[1]/div[2]',
        },
        "read": {
            "shiping_title": '//*[@data-data-id="shiping-title"]/div/div[2]/span',
            # "comment": '//*[@data-data-id="textListGrid"]/div/div/div/div[{}]/div/div/div/span',
            "comment": '//*[@id="root"]/div/div/section/div/div/div/div/div/section/div/div/div/div[1]/div/section/div/div/div/div/div/section/div/div/div/div/div[3]/section/div/div/div/div/div/section/div/div/div[1]/div/div[{}]',
        },
        "video": {
            "active_btn": '//*[@class="btn active"]',
            "next_btn": '//*[@class="btn"]',
            "tv": '//*[@id="root"]/div/header/div[2]/div[1]/div[2]/a[2]',
            # "videos": '//*[@id="dcd4"]/div/div/div/div/div/section/div[2]',
            "videos": '//*[@id="dcd4"]/div/div/div/div/div/div/section/div[2]',
            "one_video": '//*[@class="Pic"]',
        }
    },
}
