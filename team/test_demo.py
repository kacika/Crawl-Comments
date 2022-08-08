import csv
import random
import time
import requests
from bs4 import BeautifulSoup

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11"
]


# 获取html
def get_resource(url, params=None, flag='html'):
    headers = {
        'Host': 'movie.douban.com',
        'User-Agent': random.choice(user_agents),
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }
    response = requests.get(url=url, params=params, headers=headers)
    if response.status_code == 200:
        # 判断flag
        if flag == 'html':
            return response.text
        elif flag == 'media':
            return response.content
    else:
        print('获取资源有误！')


def parse_html_other(resource):
    comment_list = []
    soup = BeautifulSoup(resource, 'lxml')
    comments = soup.select_one('#comments')
    comment_items = comments.select('.comment-item')
    for item in comment_items:
        comment_info = item.select_one('.comment h3 .comment-info')
        username = comment_info.find('a').text
        comment_text = item.find('span', attrs={'class': 'short'}).text
        comment_time = comment_info.select_one('.comment-time ').text
        comment = [username, comment_text, comment_time]
        comment[2] = comment[2].strip()
        comment_list.append(comment)

    return comment_list


# 保存
def save_data(comment_list):
    with open('data/douban.csv', mode='a', newline='', encoding='utf-8') as fw:
        writer = csv.writer(fw)
        # 遍历评论列表
        writer.writerows(comment_list)

    print('保存完毕！')


if __name__ == '__main__':
    url = 'https://movie.douban.com/subject/3114220/comments'
    params = {'status': 'P', 'limit': 20, 'sort': 'new_score'}
    for i in range(9):
        n = i * 20
        params['start'] = n
        resource = get_resource(url=url, params=params)
        comment_list = parse_html_other(resource)
        save_data(comment_list)
        time.sleep(random.randint(4, 6))
