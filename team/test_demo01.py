# 仅针对腾讯视频此平台具有的电视资源（不包括电影以及其他平台）

import csv
import random
import re

import os
import requests
import time
from bs4 import BeautifulSoup
from pyecharts import Line

user_agents = [
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
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
]

# 获取html
def get_resource(url, params=None, flag='html'):
    headers = {
        # 'Host': 'coral.qq.com',
        'User-Agent': random.choice(user_agents)
    }
    # 使用requests发出请求
    response = requests.get(url=url, params=params, headers=headers)
    # 判断response的状态码
    if response.status_code == 200:
        # 判断flag
        if flag == 'html':
            return response.text
        elif flag == 'media':
            return response.content
    else:
        print('response.status_code:',response.status_code)
        print('获取资源有误！')

# 搜寻影视剧并获取电视剧总集数，同时得到每一集的网址
def search_television():
    print('*' * 70)
    print("*" * 12, '腾讯视频电视剧的评论下载和分析', '*' * 12)
    print('*' * 70)
    # https://v.qq.com/x/search/?q=大秦帝国之裂变
    name = input('输入电视剧名称: ')
    params = {'q': name}
    url = 'https://v.qq.com/x/search/'
    resource = get_resource(url=url, params=params)
    if resource:
        soup = BeautifulSoup(resource, 'lxml')
        tv_url = soup.find('a', {'class': 'figure result_figure'}).get('href')
        # print('tv_url',tv_url)
        tv_resource = get_resource(url=tv_url)
        if(tv_resource):
            episode_list = []
            tv_soup = BeautifulSoup(tv_resource, 'lxml')
            episode_items = tv_soup.find_all('span', {'_stat':'series:numbtn'})
            for item in episode_items:
                # episode_url ---> 某集地址
                episode_url = item.find('a').get('href')
                # episode_id ---> 某集集数
                episode_id = item.find('a').text
                episode_id = episode_id.replace('\n', '')
                episode_id = episode_id.replace(' ', '')
                episode = [episode_id, episode_url]
                episode_list.append(episode)
            return name, episode_list
        else:
            print('请注意是否搜索的是电视资源！')
    else:
        print('获取资源有误！')

# 获取不同集数的评论网页网址并保存相应内容
def select_episode():
    name, episode_list = search_television()
    if not os.path.exists(name):
        os.mkdir(name)
    comnum_list = []
    columns = []
    for episode in episode_list:

        episode_resource = get_resource(url=episode[1])
        path = name + '/' + episode[0]
        # comment_id
        patid = '"comment_id":"(.*?)",'
        comment_id = re.compile(patid).findall(episode_resource)[0]

        # https://coral.qq.com/4003145426
        # 原地址 https://coral.qq.com/article/4003145426/comment/v2?callback=_article4003145426commentv2&orinum=10&oriorder=o&pageflag=1&cursor=0
        # 简化后 https://coral.qq.com/article/4003145426/comment/v2?callback=_article4003145426commentv2&oriorder=o&cursor=0
        url = 'https://coral.qq.com/article/{}/comment/v2'.format(comment_id)
        callback = '_article{}commentv2'.format(comment_id)
        # 初始化为0
        cursor = 0
        params = {'callback': callback, 'oriorder': 'o', 'cursor': cursor}
        comment_resource = get_resource(url, params)
        patnum = '"commentnum":"(.*?)",'

        comment_num = re.compile(patnum).findall(comment_resource)[0]
        comnum_list.append(comment_num)
        columns.append(episode[0])
        # print('comment_num:', comment_num)
        # 每集至多保存100条评论
        city_list1 = []
        for i in range(0, 10):
            data = comment_resource
            # 获取下一个Cursor
            pat_next = '"last":"(.*?)",'
            nextcursor = re.compile(pat_next).findall(data)[0]

            # 抓取评论信息
            pat_com = '"content":"(.*?)",'
            comdata = re.compile(pat_com).findall(data)
            with open(path+'.txt', mode='a', encoding='utf-8') as fw:
                fw.write(str(comdata))
            # 抓取用户地址
            pat_region = '"region":"(中国:.*?)",'
            region_data = re.compile(pat_region).findall(data)

            for item in region_data:
                item = item.split(':')[2]
                if(len(item)):
                    city_list1.append(item)


            # 时间间隔
            # time.sleep(random.randint(1, 3))

            # 更新url
            params = {'callback': callback, 'oriorder': 'o', 'cursor': nextcursor}
            comment_resource = get_resource(url, params)
        with open(name + '/'+ episode[0]+ 'city.txt', mode='w', encoding='utf-8') as fw:
            fw.write(str(city_list1))
        print("*" * 12, '第' + episode[0] + '集评论保存完毕', '*' * 12)
    print("*" * 12, name + '的评论保存完毕', '*' * 12)
    return name, comnum_list, columns

if __name__ == '__main__':
    name, comnum_list, columns= select_episode()
    line = Line("折线图", name+"每集评论数")
    # is_label_show是设置上方数据是否显示
    line.add("评论数", columns, comnum_list, is_label_show=True)
    line.render(name+'/'+ 'render1.html')

