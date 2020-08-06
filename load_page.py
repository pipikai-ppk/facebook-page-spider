import json
import os
import re
import time
from helium import *
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 自己登录facebook的账号邮箱和密码
YOUR_EMAIL = '!!!YOUR_EMAIL!!!'
YOUR_PASSWORD = '!!!YOUR_PASSWORD!!!'

POSTS_SELECTOR = '[class="_427x"] .userContentWrapper'
COMMENTABLE_SELECTOR = POSTS_SELECTOR + ' .commentable_item'
CMTS = type('Enum', (), {
	'MOST_RELEVANT': 'RANKED_THREADED',  
	'NEWEST': 'RECENT_ACTIVITY', 
	'ALL_COMMENTS': 'RANKED_UNFILTERED'
})


def load_more_posts():
	js_script = 'window.scrollTo(0, document.body.scrollHeight)'
	driver.execute_script(js_script)
	while find_all(S('.async_saving [role="progressbar"]')) != []: pass

def click_multiple_button(selector):
	js_script = "document.querySelectorAll('" + selector + "').forEach(btn => btn.click())"
	driver.execute_script(js_script)
	while find_all(S(COMMENTABLE_SELECTOR + ' [role="progressbar"]')) != []: pass

def filter_comments(by):
	if by == CMTS.MOST_RELEVANT: return
	click_multiple_button('[data-ordering="RANKED_THREADED"]')
	click_multiple_button('[data-ordering="'+ by + '"]')

def driver_init():
	print('开始模拟首次登陆')
	global driver
	# 2.模拟登陆
	options = ChromeOptions()
	# 2.1.添加代理（根据自己电脑的代理设置）
	options.add_argument('--proxy-server=socks5://localhost:1087')
	# 2.2.消除chrome跳窗
	prefs = {
	'profile.default_content_setting_values' :
	    {
	    'notifications' : 2
	     }
	}
	options.add_experimental_option('prefs',prefs)
	# 2.3.启动chromedriver浏览器
	driver = start_chrome("www.facebook.com", headless=False, options=options)

	# 2.4.登录facebook
	# username
	email_element = WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.ID, "email")))
	email_element.clear()
	email_element.send_keys(YOUR_EMAIL)
	driver.implicitly_wait(1)
	# password
	password_element = WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.ID, "pass")))
	password_element.clear()
	password_element.send_keys(YOUR_PASSWORD)
	driver.implicitly_wait(1)
	# click
	login_element = WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.ID, "loginbutton")))
	login_element.click()
	time.sleep(1)

	print('完成首次登陆！')


def start(
	url= '', 
	scroll_down=0, 
	filter_cmts_by=CMTS.MOST_RELEVANT, 
	view_more_cmts=0, 
	view_more_replies=0,
	crawl_count=0
):
	
	# 如果爬取第一个人，需要先模拟登陆facebook
	if crawl_count == 0:
		driver_init()

	print('Go to page', url)
	
	# 跳转到指定页面
	driver.get(url)
	time.sleep(2)
	
	print('Load more posts and check for Not Now button')
	load_more_posts()

	btnNotNow = find_all(S('#expanding_cta_close_button'))
	if btnNotNow != []:
		print('Click Not Now button')
		click(btnNotNow[0].web_element.text)

	for i in range(scroll_down - 1):
		print('Load more posts times', i + 2, '/', scroll_down)
		load_more_posts()

	print('Filter comments by', filter_cmts_by)
	filter_comments(filter_cmts_by)

	for i in range(view_more_cmts):
		print('Click View more comments buttons times', i + 1, '/', view_more_cmts)
		click_multiple_button(COMMENTABLE_SELECTOR + ' ._7a94 ._4sxc')

	for i in range(view_more_replies):
		print('Click Replies buttons times', i + 1, '/', view_more_replies)
		click_multiple_button(COMMENTABLE_SELECTOR + ' ._7a9h ._4sxc')

	print('Click See more buttons of comments')
	click_multiple_button(COMMENTABLE_SELECTOR + ' .fss')

def stop_and_save(fileName, listPosts):
	print('Save crawled data...')
	with open(fileName, 'a', encoding='utf-8') as file:
		json.dump(listPosts, file, ensure_ascii=False, indent=4)
	