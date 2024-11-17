import requests
import json
import time
 
#发起GET请求
def get_resou(url, headers):
    """
    发起GET请求获取资源
     
    参数:
    url: str - 需要请求的URL地址
    headers: dict - 请求头信息
     
    返回值:
    resou: requests.Response - 请求返回的响应对象，如果请求失败则返回None
    """
    try:
        # 尝试发送GET请求
        resou = requests.get(url, headers=headers)
        return resou
    except:
        # 请求异常处理，打印失败信息并返回None
        print('请求失败')
        return None
 
 
def extract_hot_search_keywords(json_str):
    """
    从JSON字符串中提取热门搜索关键词列表。
     
    参数:
    json_str: str - 包含热搜数据的JSON字符串。
     
    返回值:
    list - 热门搜索关键词的列表。
    """
    # 解析JSON字符串
    data = json.loads(json_str)
    hot_search_keywords = []
 
    # 遍历数据，提取关键词
    for item in data['data']['trending']['list']:
        hot_search_keywords.append(item['show_name'])
 
    return hot_search_keywords
 
# 设置请求的URL和头部信息
url = 'https://api.bilibili.com/x/web-interface/wbi/search/square?limit=50&platform=web&w_rid=ed39f37d84dc372747871a641d3c8c45&wts=1711190219'
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
resou = get_resou(url,headers)
time_delta = time.strftime("%y-%m-%d", time.localtime())
 
 
e = 1
# 打开文件准备写入热搜关键词
file = open('bilibili_hot_search'+time_delta+'.txt','a',encoding='utf-8')
#file.write('\n'+'_-----------------------------_'+'\n'+'当日日期:')
file.write(time_delta)
file.write('\n')
for i in extract_hot_search_keywords(resou.text):
    file.write(str(e)+'.')
    file.write(i)
    file.write('\n')
    e += 1
file.close()
 