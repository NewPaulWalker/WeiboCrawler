# !/usr/bin/nev python
# -*-coding:utf8-*-

import requests
import urllib3
import csv
import re
import time
import datetime
from parsel import Selector
from requests_html import HTMLSession

urllib3.disable_warnings()
session = HTMLSession()

file_path_list = [
    '',
    './data/1.尼格',
    './data/2.纳沙',
    './data/3.奥鹿',
    './data/4.梅花',
    './data/5.马鞍',
    './data/6.木兰',
    './data/7.桑达',
    './data/8.暹芭',
    './data/9.烟花'
]
n_list = [
    0,
    16,
    27,
    17,
    17,
    14,
    11,
    10,
    13,
    12
]
url_list_all = [
    '',
    f'https://s.weibo.com/weibo/%2523%25E5%258F%25B0%25E9%25A3%258E%25E5%25B0%25BC%25E6%25A0%25BC%2523?topnav=1&wvr=6&page=',
    f'https://s.weibo.com/weibo/%2523%25E5%258F%25B0%25E9%25A3%258E%25E7%25BA%25B3%25E6%25B2%2599%2523?topnav=1&wvr=6&b=1&page=',
    f'https://s.weibo.com/weibo/%2523%25E5%258F%25B0%25E9%25A3%258E%25E5%25A5%25A5%25E9%25B9%25BF%2523?topnav=1&wvr=6&b=1&page=',
    f'https://s.weibo.com/weibo/%2523%25E5%258F%25B0%25E9%25A3%258E%25E6%25A2%2585%25E8%258A%25B1%2523?topnav=1&wvr=6&b=1&page=',
    f'https://s.weibo.com/weibo/%2523%25E5%258F%25B0%25E9%25A3%258E%25E9%25A9%25AC%25E9%259E%258D%2523?topnav=1&wvr=6&b=1&page=',
    f'https://s.weibo.com/weibo/%2523%25E5%258F%25B0%25E9%25A3%258E%25E6%259C%25A8%25E5%2585%25B0%2523?topnav=1&wvr=6&b=1&page=',
    f'https://s.weibo.com/weibo/%2523%25E5%258F%25B0%25E9%25A3%258E%25E6%25A1%2591%25E8%25BE%25BE%2523?topnav=1&wvr=6&b=1&page=',
    f'https://s.weibo.com/weibo/%2523%25E5%258F%25B0%25E9%25A3%258E%25E6%259A%25B9%25E8%258A%25AD%2523?topnav=1&wvr=6&b=1&page=',
    f'https://s.weibo.com/weibo/%2523%25E5%258F%25B0%25E9%25A3%258E%25E7%2583%259F%25E8%258A%25B1%2523?topnav=1&wvr=6&b=1&page='
]

headers_list = {
    'cookie': 'your_weibo.com_cookie',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}
headers = {
    'cookie': 'your_m.weibo.cn_cookie',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}
def parse_comment(dict):
    try:
        text_origin = dict['text']
        alts = ''.join(re.findall(r'alt=(.*?) ', text_origin))
        text = re.sub("<span.*?</span>", alts, text_origin)
        GMT_format = '%a %b %d %H:%M:%S +0800 %Y'
        created_at = dict['created_at']
        timeArray = datetime.datetime.strptime(created_at, GMT_format)
        std_create_times = timeArray.strftime('%Y-%m-%d %H:%M:%S')
        source = dict['source']
        screen_names = dict['user']['screen_name']
        csv_writer.writerow([screen_names, source, std_create_times, text])
        if (dict['comments'] != False):
            cid = dict['id']
            url_child_comment = f'https://m.weibo.cn/comments/hotFlowChild?cid={cid}&max_id=0&max_id_type=0'
            responses_child_comment = session.get(url_child_comment, proxies={'http': prox, 'https': prox}, headers=headers, verify=False).json()
            max_id = responses_child_comment['max_id']
            max_id_type = responses_child_comment['max_id_type']
            data = {
                'cid': cid,
                'max_id': max_id,
                'max_id_type': max_id_type
            }
            parse_child_comment(responses_child_comment)
            get_child_comment(data)
    except Exception as e:
        return

def get_comment(data):
    if data['max_id'] == 0:
        return
    time.sleep(3)
    url_comment = 'https://m.weibo.cn/comments/hotflow?'
    responses_comment = session.get(url_comment, proxies={'http': prox, 'https': prox}, headers=headers, params=data, verify=False).json()
    if('data' in responses_comment):
        max_id = responses_comment['data']['max_id']
        max_id_type = responses_comment['data']['max_id_type']
        data = {
            'id': mid,
            'mid': mid,
            'max_id': max_id,
            'max_id_type': max_id_type
        }
        comment_list = responses_comment['data']['data']
        for comment_json_dict in comment_list:
            parse_comment(comment_json_dict)
        get_comment(data)

def parse_child_comment(responses_child_comment):
    data_list = responses_child_comment['data']
    for data_json_dict in data_list:
        try:
            texts_1 = data_json_dict['text']
            """需要sub替换掉标签内容"""
            # 需要替换的内容，替换之后的内容，替换对象
            alts = ''.join(re.findall(r'alt=(.*?) ', texts_1))
            texts = re.sub("<span.*?</span>", alts, texts_1)
            # 评论时间   格林威治时间---需要转化为北京时间
            GMT_format = '%a %b %d %H:%M:%S +0800 %Y'
            created_at = data_json_dict['created_at']
            timeArray = datetime.datetime.strptime(created_at, GMT_format)
            std_create_times = timeArray.strftime('%Y-%m-%d %H:%M:%S')
            # IP地址
            source = data_json_dict['source']
            # 用户名
            screen_names = data_json_dict['user']['screen_name']
            # print(screen_names, genders, std_create_times, texts, like_counts)
            csv_writer.writerow([screen_names, source, std_create_times, texts])
        except Exception as e:
            return

def get_child_comment(data):
    if (data['max_id'] == 0):
        return
    time.sleep(3)
    cid = data['cid']
    url_child_comment = 'https://m.weibo.cn/comments/hotFlowChild?'
    prox = ''
    responses_child_comment = session.get(url_child_comment, proxies={'http': prox, 'https': prox}, headers=headers, params=data, verify=False).json()
    max_id = responses_child_comment['max_id']
    max_id_type = responses_child_comment['max_id_type']
    data = {
        'cid': cid,
        'max_id': max_id,
        'max_id_type': max_id_type
    }
    parse_child_comment(responses_child_comment)
    get_child_comment(data)

for i in range(1,10):
    time.sleep(10)
    url_head = url_list_all[i]
    print(f'第{i}个台风')
    for page in range(1, n_list[i]+1):
        time.sleep(3)
        url_list = f'{url_head}{page}'
        responses_list = requests.get(url_list, headers=headers_list)
        html_data = responses_list.text
        print(f'第{page}页')
        selector = Selector(text=html_data)
        divs = selector.css('.m-con-l .card-wrap')
        for div in divs[1:]:
            time.sleep(3)
            mid = div.attrib['mid']
            print(mid)
            f_content = open(f'{file_path_list[i]}/{mid}.txt', 'w', encoding='utf-8')
            url_content = f'https://m.weibo.cn/statuses/extend?id={mid}'
            responses_content = requests.get(url_content, headers=headers)
            content = responses_content.json()['data']['longTextContent']
            f_content.write(content)
            f_comment = open(f'{file_path_list[i]}/{mid}.csv', mode='a', encoding='utf-8', newline='')
            csv_writer = csv.writer(f_comment)
            csv_writer.writerow(['昵称', '地区', '时间', '评论'])
            url_comment = f'https://m.weibo.cn/comments/hotflow?id={mid}&mid={mid}&max_id_type=0'
            prox = ''
            responses_comment = session.get(url_comment, proxies={'http': prox, 'https': prox}, headers=headers,
                                            verify=False).json()
            if ('data' in responses_comment):
                max_id = responses_comment['data']['max_id']
                max_id_type = responses_comment['data']['max_id_type']
                data = {
                    'id': mid,
                    'mid': mid,
                    'max_id': max_id,
                    'max_id_type': max_id_type
                }
                comment_list = responses_comment['data']['data']
                for comment_json_dict in comment_list:
                    parse_comment(comment_json_dict)
                get_comment(data)



