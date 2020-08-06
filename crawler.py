import load_page
import re
import numpy as np
import pandas as pd

# 读取facebook目标人物id列表: id_list
id_list = []
data = pd.read_csv('facebook_id.txt', header=None)
for ii in data.index:
    id_list.append(str(data.loc[ii].values[0]))
print(id_list)
id_list_length = len(id_list)

crawl_count = 0

# 开始爬取所有id_list中的用户数据
for user_id in id_list:
	USER_ID = user_id
	PAGE_URL = 'https://www.facebook.com/profile.php?id=' + user_id
	SCROLL_DOWN = 3

	FILTER_CMTS_BY = load_page.CMTS.MOST_RELEVANT
	VIEW_MORE_CMTS = 0
	VIEW_MORE_REPLIES = 0

	def get_child_attribute(element, selector, attr):
		try: 
			element = element.find_element_by_css_selector(selector)
			return str(element.get_attribute(attr))
		except: return ''
		
	def get_comment_info(comment):
		cmt_url = get_child_attribute(comment, '._3mf5', 'href')
		cmt_id = cmt_url.split('=')[-1]

		if cmt_id == None:
			cmt_id = comment.get_attribute('data-ft').split(':"')[-1][:-2]
			user_url = user_id = user_name = 'Acc clone'
		else:
			user_url = cmt_url.split('?')[0]
			user_id = user_url.split('https://www.facebook.com/')[-1].replace('/', '')
			user_name = get_child_attribute(comment, '._6qw4', 'innerText')

		utime = get_child_attribute(comment, 'abbr', 'data-utime')
		text = get_child_attribute(comment, '._3l3x ', 'textContent')

		return {
			'id': cmt_id,
			'utime': utime,
			'user_url': user_url,
			'user_id': user_id,
			'user_name': user_name,
			'text': text,
		}



	# 程序开始运行
	load_page.start(
		PAGE_URL, 
		SCROLL_DOWN, 
		FILTER_CMTS_BY, 
		VIEW_MORE_CMTS, 
		VIEW_MORE_REPLIES,
		crawl_count,
	)
	driver = load_page.driver
	total = 0

	listJsonPosts = []
	listHtmlPosts = driver.find_elements_by_css_selector('[class="du4w35lb k4urcfbm l9j0dhe7 sjgh65i0"]')
	print('Start crawling', len(listHtmlPosts), 'posts...')

	for post in listHtmlPosts:
		# post_url = get_child_attribute(post, '._5pcq', 'href').split('?')[0]
		# post_id = re.findall('\d+', post_url)[-1]
		# utime = get_child_attribute(post, 'abbr', 'data-utime')
		post_text = get_child_attribute(post, '[data-ad-preview="message"]','textContent')
		# total_shares = get_child_attribute(post, '[data-testid="UFI2SharesCount/root"]', 'innerText')
		# total_cmts = get_child_attribute(post, '._3hg-', 'innerText')

		# listJsonCmts = []
		# listHtmlCmts = post.find_elements_by_css_selector('._7a9a>li')

		# num_of_cmts = len(listHtmlCmts)
		# total += num_of_cmts

		# if num_of_cmts > 0:
		# 	print('Crawling', num_of_cmts, 'comments of post', post_id)

		# 	for comment in listHtmlCmts:
		# 		comment_owner = comment.find_elements_by_css_selector('._7a9b')
		# 		comment_info = get_comment_info(comment_owner[0])

		# 		listJsonReplies = []
		# 		listHtmlReplies = comment.find_elements_by_css_selector('._7a9g')

		# 		num_of_replies = len(listHtmlReplies)
		# 		total += num_of_replies

		# 		if num_of_replies > 0:
		# 			print('Crawling', num_of_replies, 'replies for', comment_info['user_name'] + "'s comment")
					
		# 			for reply in listHtmlReplies:
		# 				reply_info = get_comment_info(reply)
		# 				listJsonReplies.append(reply_info)

		# 		comment_info.update({ 'replies': listJsonReplies })
		# 		listJsonCmts.append(comment_info)

		# listJsonReacts = []
		# listHtmlReacts = post.find_elements_by_css_selector('._1n9l')

		# for react in listHtmlReacts:
		# 	react_text = react.get_attribute('aria-label')
		# 	listJsonReacts.append(react_text)

		listJsonPosts.append({
			# 'url': post_url,
			# 'id': post_id,
			# 'utime': utime,
			'facebook_id': user_id,
			'text': post_text,
			# 'total_shares': total_shares,
			# 'total_cmts': total_cmts,
			# 'crawled_cmts': listJsonCmts,
			# 'reactions': listJsonReacts,
		})


		# 将爬取结果输出到文件中
		print('Total comments and replies crawled:', total)
		load_page.stop_and_save('data2.json', listJsonPosts)
		# 打印当前爬取进度
		current_percent = str(round(id_list.index(user_id) / id_list_length, 2))
		print('已完成爬取：' + current_percent + '%')

		crawl_count += 1

# 关闭浏览器，程序运行结束
kill_browser()