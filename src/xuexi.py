#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import os
import sys
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import *

VIDEO_HISTORY = set()
ARTICLE_HISTORY = set()


class Browser:
    def __init__(self, config, website):
        self.config = config
        self.website = website
        self.xpath = self.website["xpath"]
        self.driver = self._login()

    def quit(self):
        self.driver.quit()

    def _login(self):
        # chrome配置
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--log-level=3')
        if self.config["chrome_mute"]:
            chrome_options.add_argument('--mute-audio')  # 关闭声音
        if self.config["hide_page"]:
            chrome_options.add_argument("--headless")  # 隐藏页面
        # 执行exe文件时，chrome驱动在本层目录；执行源代码时，chrome驱动在上层目录
        chrome_driver = os.path.join(os.getcwd(), "chromedriver\chromedriver.exe")  # chromedriver的路径
        if not os.path.exists(chrome_driver):
            chrome_driver = os.path.join(os.getcwd(), "..\chromedriver\chromedriver.exe")  # 执行源码时，驱动在上层目录
            if not os.path.exists(chrome_driver):
                logger.info("无法找到chromedriver.exe驱动文件，请确保xuexi.exe文件与chromedriver文件夹在同一目录下")
                finish(browser, 30, -1)
        # 实例化浏览器
        try:
            driver = webdriver.Chrome(executable_path=chrome_driver, chrome_options=chrome_options)
        except Exception as e:
            logger.info("打开chrome浏览器失败，请确保已安装谷歌浏览器chrome，并且版本为最新版 74\n{}".format(e))
            finish(browser, 30, -1)
            return
        # 加载登录页面
        driver.get(self.website["url"]["login"])
        # 移动页面到最下方，显示二维码
        try:
            locator = (By.XPATH, self.xpath["login"]["login_text"])
            WebDriverWait(driver, 60, 0.5).until(EC.presence_of_element_located(locator))
            js = "var q=document.documentElement.scrollTop=" + str(3000)
            driver.execute_script(js)
        except Exception as e:
            raise e

        # 等待用户扫码登录
        logger.info("请使用学习强国APP扫码登录")
        while True:
            try:
                text = driver.find_element_by_xpath(self.xpath["login"]["success"]).text
                # 扫码登陆成功
                if "学习积分" in text:
                    if self.config["hide_page"]:
                        driver.minimize_window()
                    break
            except:
                pass
            finally:
                time.sleep(1)

        return driver

    def click(self, key1, key2, index=-100, value=None, time_sleep=0.5, wait_time=60):
        if index < -99:
            try:
                locator = (By.XPATH, self.xpath[key1][key2].format(value))
                WebDriverWait(self.driver, wait_time, 0.5).until(EC.presence_of_element_located(locator)).click()
                self.cur_page()
            except Exception as e:
                raise e
        else:
            try:
                locator = (By.XPATH, self.xpath[key1][key2].format(value))
                WebDriverWait(self.driver, wait_time, 0.5).until(EC.presence_of_element_located(locator))
                self.driver.find_elements_by_xpath(self.xpath[key1][key2])[index].click()
                self.cur_page()
            except Exception as e:
                raise e
        time.sleep(time_sleep)

    def page_down(self, lenth=1000):
        js = "var q=document.documentElement.scrollTop=" + str(lenth)
        self.driver.execute_script(js)

    def page_scroll(self, downward, wait_time):
        # 页面滚动即是有效阅读。等待时间，页面下滑距离都是随机值
        sleep_all_time = 0
        if downward:
            length = random.randint(50, 250)
            while True:
                self.page_down(length)
                sleep_time = random.randint(5, 15)
                time.sleep(sleep_time)
                sleep_all_time += sleep_time
                length += random.randint(50, 250)
                if sleep_all_time > wait_time:
                    break
        else:
            while True:
                self.page_down(random.randint(100, 600))
                sleep_time = random.randint(5, 15)
                time.sleep(sleep_time)
                sleep_all_time += sleep_time
                if sleep_all_time > wait_time:
                    break
        return True

    def get_page(self, page_name, sleep_time=2, distance=0):
        self.driver.get(self.website["url"][page_name])
        time.sleep(sleep_time)
        self.page_down(distance)

    def get_text(self, key1, key2, index=-1, wait_time=60):
        if not wait_time:
            if index < 0:
                return self.driver.find_element_by_xpath(self.xpath[key1][key2]).text
            else:
                return self.driver.find_elements_by_xpath(self.xpath[key1][key2])[index].text
        else:
            locator = (By.XPATH, self.xpath[key1][key2])
            if index < 0:
                return WebDriverWait(self.driver, wait_time, 0.5).until(EC.presence_of_element_located(locator)).text
            elif index >= 0:
                return WebDriverWait(self.driver, wait_time, 0.5).until(EC.presence_of_all_elements_located(locator))[
                    index].text

    def cur_page(self):
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[-1])
        if self.config["hide_page"]:
            self.driver.minimize_window()

    def back(self):
        self.cur_page()
        self.driver.close()
        self.cur_page()


def get_random_num(start, end, history):
    if len(history) == int(end - start + 1):
        logger.info("history 已满。")
        history.clear()
    num = random.randint(start, end)
    while num in history:
        num = random.randint(start, end)
    return num


def get_my_points(browser):
    browser.get_page("my_points")
    logger.info("今日积分获取情况")
    read_point = browser.get_text("points", "read_points")
    video_point = browser.get_text("points", "video_points")
    logger.info("阅读积分：{0}".format(read_point))
    logger.info("视频积分：{0}".format(video_point))
    return {
        "read_point": int(read_point.split('/')[0][0]),
        "read_point_all": int(read_point.split('/')[1][0]),
        "video_point": int(video_point.split('/')[0][0]),
        "video_point_all": int(video_point.split('/')[1][0]),
    }


def read_one_article(browser):
    # 获取一篇未读过的文章
    random_num = get_random_num(1, 20, ARTICLE_HISTORY)
    ARTICLE_HISTORY.add(random_num)
    logger.info("阅读历史：{}".format(ARTICLE_HISTORY))
    # 读文章
    browser.click("read", "comment", value=str(random_num))
    browser.page_scroll(downward=True, wait_time=browser.config["read_time"])
    browser.back()
    return True


def read_article(browser, need_read_num):
    logger.info("开始阅读文章，总共需要阅读{}篇".format(need_read_num))
    # 进入学习时评
    browser.get_page("main", sleep_time=5, distance=1500)
    browser.click("read", "shiping_title")
    while need_read_num:
        logger.info("尚需阅读{0}篇文章".format(need_read_num))
        read_one_article(browser)
        need_read_num -= 1
    browser.back()
    logger.info("阅读文章结束")
    return True


def flip_page(browser, page):
    time.sleep(3)
    while int(browser.get_text("video", "active_btn")) < int(page):
        browser.click("video", "next_btn", index=-2)
        time.sleep(1)


def watch_one_video(browser):
    # 获取未观看过的视频
    random_num = get_random_num(0, 19, VIDEO_HISTORY)
    VIDEO_HISTORY.add(random_num)
    logger.info("视频历史：{}".format(VIDEO_HISTORY))
    # 看视频
    browser.click("video", "one_video", index=random_num)
    browser.page_scroll(downward=False, wait_time=browser.config["video_time"])
    browser.back()
    return True


def watch_video(browser, need_watch_num):
    logger.info("开始观看视频，共需观看{}部".format(need_watch_num))
    # 进入学习电视台
    browser.get_page("main", 5)
    browser.click("video", "tv", time_sleep=3)
    browser.click("video", "videos", time_sleep=3)
    # 随机翻几页
    page = random.randint(1, 11)
    flip_page(browser, page)
    while need_watch_num:
        logger.info("尚需观看视频{0}部".format(need_watch_num))
        watch_one_video(browser)
        need_watch_num -= 1
    browser.back()
    logger.info("观看视频结束")
    return True


def auto_get_points(browser):
    # 获取当前积分情况
    my_points = get_my_points(browser)

    # 读文章 2分钟1篇
    while my_points["read_point"] < my_points["read_point_all"]:
        read_article(browser, my_points["read_point_all"] - my_points["read_point"])
        my_points = get_my_points(browser)

    # 看视频 3分钟1部
    while my_points["video_point"] < my_points["video_point_all"]:
        watch_video(browser, my_points["video_point_all"] - my_points["video_point"])
        my_points = get_my_points(browser)

    return True


def finish(browser, remain_time=10, code=1):
    logger.info("任务完成，程序将于{}秒后退出".format(remain_time))
    # 关闭浏览器
    browser.quit()
    # 退出倒计时
    time_slice = remain_time // 10
    while remain_time > 0:
        logger.info("程序将于{}秒后退出".format(remain_time))
        time.sleep(time_slice)
        remain_time -= time_slice
    # 关闭程序
    exit(code)


def create_logger():
    # create logger
    logger = logging.getLogger("xuexi")
    logger.setLevel(logging.INFO)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # create console handler and set level to info
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    # create file handler and set level to info
    file_handler = logging.FileHandler("log.log", "w")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


if __name__ == '__main__':
    logger = create_logger()
    # 登录
    browser = Browser(USER_CONFIG, WEBSITE)
    # 自动获取积分
    auto_get_points(browser)
    # 退出程序
    finish(browser)
