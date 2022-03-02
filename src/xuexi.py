#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
学习强国脚本
作者：Yeat
时间：2020.3.24
"""
import os
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from config import USER_CONFIG, WEBSITE


VIDEO_HISTORY = set()
ARTICLE_HISTORY = set()


class Browser:
    """
    使用浏览器打开学习强国网站
    """

    def __init__(self, config, website):
        self.config = config
        self.website = website
        self.xpath = self.website["xpath"]
        self.driver = self._init_driver()

    def quit(self):
        """ 退出浏览器
        """
        self.driver.quit()
        return None

    def _init_driver(self):
        """实例化浏览器
        """
        # chrome配置
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--log-level=3')
        if self.config["chrome_mute"]:
            chrome_options.add_argument('--mute-audio')  # 关闭声音
        if self.config["hide_page"]:
            chrome_options.add_argument("--headless")  # 隐藏页面

        # 实例化浏览器
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=chrome_options)
        except Exception as e:
            logger.info("打开chrome浏览器失败")
            finish(None, 30, -1)
            return None

        return driver

    def login(self):
        """ 扫码登陆学习强国账号
        """
        # 加载登录页面
        # driver.get(self.website["url"]["login"]) # 直接加载登陆界面偶尔会显示系统维护BUG
        self.driver.get(self.website["url"]["main"])
        # 从主页面点击登陆
        self.click("login", "login_btn")
        # 移动页面到最下方，显示二维码
        try:
            locator = (By.XPATH, self.xpath["login"]["login_text"])
            WebDriverWait(self.driver, 60, 0.5).until(EC.presence_of_element_located(locator))
            js_code = "var q=document.documentElement.scrollTop=" + str(2500)
            self.driver.execute_script(js_code)
        except Exception as e:
            raise e

        # 等待用户扫码登录
        logger.info("请使用学习强国APP扫码登录")
        while True:
            try:
                text = self.driver.find_element(By.XPATH, self.xpath["login"]["login_success"]).text
                # text = self.driver.find_element_by_xpath(self.xpath["login"]["login_success"]).text
                # 扫码登陆成功
                if "欢迎您" in text:
                    if self.config["hide_page"]:
                        self.driver.minimize_window()
                    break
            except:
                pass
            finally:
                time.sleep(1)

        return None

    def click(self, key1, key2, index=-100, value=None, time_sleep=0.5, wait_time=60):
        """ 点击网页操作
        """
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
                # self.driver.find_element(By.XPATH, self.xpath[key1][key2])[index].click()
                self.driver.find_elements_by_xpath(self.xpath[key1][key2])[index].click()
                self.cur_page()
            except Exception as e:
                raise e
        time.sleep(time_sleep)

    def page_down(self, lenth=1000):
        """ 页面下滑
        """
        js_code = "var q=document.documentElement.scrollTop=" + str(lenth)
        self.driver.execute_script(js_code)

    def page_scroll(self, downward, wait_time):
        """ 页面随机滚动
        """
        sleep_all_time = 0
        if downward:
            length = random.randint(50, 250)
            while True:
                self.page_down(length)
                sleep_time = random.randint(2, 4)
                time.sleep(sleep_time)
                sleep_all_time += sleep_time
                length += random.randint(50, 250)
                if sleep_all_time > wait_time:
                    break
        else:
            while True:
                self.page_down(random.randint(100, 600))
                sleep_time = random.randint(2, 4)
                time.sleep(sleep_time)
                sleep_all_time += sleep_time
                if sleep_all_time > wait_time:
                    break
        return True

    def get_page(self, page_name, sleep_time=2, distance=0):
        """ 打开指定网页
        """
        self.driver.get(self.website["url"][page_name])
        time.sleep(sleep_time)
        self.page_down(distance)
        return True

    def get_text(self, key1, key2, index=-1, wait_time=60):
        """ 获取内容
        """
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
        return None

    def cur_page(self):
        """ 获取最新的窗口
        """
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[-1])
        if self.config["hide_page"]:
            self.driver.minimize_window()
        return None

    def back(self):
        """ 关闭当前页面，返回上一个页面
        """
        self.cur_page()
        self.driver.close()
        self.cur_page()


def get_random_num(start, end, history):
    """ 获取指定范围的随机数，并且在历史记录满时清空
    """
    if len(history) == int(end - start + 1):
        logger.info("history 已满。")
        history.clear()
    num = random.randint(start, end)
    while num in history:
        num = random.randint(start, end)
    return num


def get_my_points(browser):
    """ 获取积分情况
    """
    browser.get_page("my_points")
    logger.info("今日积分获取情况")
    read_point = browser.get_text("points", "read_points")
    video_point = browser.get_text("points", "video_points")
    logger.info("阅读积分：{0}".format(read_point))
    logger.info("视频积分：{0}".format(video_point))
    return {
        "read_point": int(read_point.split('/')[0][:-1]),
        "read_point_all": int(read_point.split('/')[1][:-1]),
        "video_point": int(video_point.split('/')[0][:-1]),
        "video_point_all": int(video_point.split('/')[1][:-1]),
    }


def read_one_article(browser):
    """ 阅读一篇文章
    """
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
    """ 阅读文章
    """
    logger.info("开始阅读文章，总共需要阅读{}篇".format(need_read_num))
    # 进入学习时评
    browser.get_page("main", sleep_time=5, distance=4000)
    time.sleep(4)
    browser.click("read", "shiping_title")
    while need_read_num:
        logger.info("尚需阅读{0}篇文章".format(need_read_num))
        read_one_article(browser)
        need_read_num -= 1
    browser.back()
    logger.info("阅读文章结束")
    return True


def flip_page(browser, page):
    """ 视频页面时，随机翻页
    """
    time.sleep(3)
    while int(browser.get_text("video", "active_btn")) < int(page):
        browser.click("video", "next_btn", index=-2)
        time.sleep(1)


def watch_one_video(browser):
    """ 观看一个视频
    """
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
    """ 观看视频
    """
    logger.info("开始观看视频，共需观看{}部".format(need_watch_num))
    # 进入学习电视台
    browser.get_page("main", 5)
    browser.click("video", "tv", time_sleep=3)  # 进入学习电视台
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
    """ 自动获取积分
    """
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


def finish(browser=None, remain_time=10, code=1):
    """ 任务完成，退出程序
    """
    logger.info("任务完成，程序将于{}秒后退出".format(remain_time))
    # 关闭浏览器
    if browser:
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
    """ 创建logger
    """
    # create logger
    logger_instance = logging.getLogger("xuexi")
    logger_instance.setLevel(logging.INFO)
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
    logger_instance.addHandler(console_handler)
    logger_instance.addHandler(file_handler)
    return logger_instance


def main():
    """ 主函数
    """
    # 登录
    browser = Browser(USER_CONFIG, WEBSITE)
    browser.login()
    # 自动获取积分
    auto_get_points(browser)
    # 退出程序
    finish(browser)


if __name__ == '__main__':
    logger = create_logger()
    main()
