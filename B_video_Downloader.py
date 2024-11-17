import re
import requests
import json
import os
import concurrent.futures
 
hearers = {"Cookie": input("请输入cookie:"),
    "user-agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)"}
 
 
def get_video_url(i,B_V,Bool,hearers=hearers):
    """
    根据B站视频的BV号和是否为首页视频，获取视频的标题、音频URL和视频URL。
 
    参数:
    i -- 视频的页码，如果为首页视频则此参数无效
    B_V -- 视频的BV号
    Bool -- 布尔值，指示是否为首页视频
 
    返回:
    title -- 视频的标题
    audio_url -- 视频的音频URL
    video_url -- 视频的视频URL
    """
     
    # 根据Bool值决定请求的链接是否是首页视频链接
    if Bool == True:
        link = "https://www.bilibili.com/video/"+B_V+"/?spm_id_from=pageDriver&vd_source=7deef2232461db0465df2ada9b33b52f"
    else:
        link = "https://www.bilibili.com/video/"+B_V+"/?p="+str(i)+"&spm_id_from=pageDriver&vd_source=7deef2232461db0465df2ada9b33b52f"
     
    # 发起HTTP请求，获取视频页面内容
    RT = requests.get(url=link,headers=hearers)
     
    # 解析页面内容，提取视频的播放信息
    html = RT.text
    info =re.findall('window.__playinfo__=(.*?)</script>',html)
    json_str = json.loads(info[0])
     
    # 提取音频和视频的URL
    audio_url = json_str["data"]["dash"]["audio"][1]["baseUrl"]
    video_url = json_str["data"]["dash"]["video"][1]["baseUrl"]
     
    # 提取视频标题
    title = re.findall('<h1 data-title="(.*?)" title=',html)
     
    # 返回视频标题、音频URL和视频URL
    return title[0],audio_url,video_url
 
def get_BV(sid,hearers=hearers):
    """
    根据给定的sid获取对应的BV号。
 
    参数:
    sid -- 视频的sid
 
    返回:
    BV -- BV号列表
    """
     
    # 构造API请求链接
    link = "https://api.bilibili.com/x/polymer/web-space/seasons_archives_list?mid=7466789&season_id="+sid+"&sort_reverse=false&page_num=1&page_size=30&web_location=333.999"
    print(link)
     
    # 发送HTTP请求获取网页内容
    RT = requests.get(url=link,headers=hearers)
    html = RT.text
    if '-404' in html:
        print('error:A线程404')
        link=f'https://api.bilibili.com/x/series/archives?mid=298254767&series_id={sid}&only_normal=true&sort=desc&pn=1&ps=30&current_mid=1179475507'
        RT = requests.get(url=link,headers=hearers)
        html = RT.text
        if '-404' in html:
            print('html')
    # 使用正则表达式提取BV号
    BV = re.findall('"bvid":"(.*?)"',html)
    print("info:",html)
    # 返回BV号列表
    return BV
 
def download_video(title,audio_url,video_url,BV,l,hearers=hearers):
    """
    下载视频及其音频并合成文件。
 
    参数:
    title -- 视频的标题
    audio_url -- 视频的音频URL
    video_url -- 视频的视频URL
    BV -- 视频的BV号
    l -- 视频序号
    """
     
    hearer_SAFE = {"Cookie": hearers["Cookie"], "user-agent": hearers["user-agent"],"referer":f"https://www.bilibili.com/video/{BV}/?spm_id_from=333.999.0.0"}
    safe_title = re.sub(r"[\[ :;(),&\]？！￥…（|）—“”‘’《》、/\\。，？！@#￥%……&*（）——+【】、；‘’“”《》【】]", "", title)  # 替换掉非法字符
 
    audio_file = f'audio{safe_title}.m4s'
    video_file = f'vidio{safe_title}.m4s'
    output_file = f'Output{safe_title}{l}.mp4'
    print("info:",title,audio_url,video_url)
    audio_content=requests.get(url=audio_url,headers=hearer_SAFE).content
    video_content=requests.get(url=video_url,headers=hearer_SAFE).content
    with open(audio_file, mode='wb') as audio:
        audio.write(audio_content)
    with open(video_file, mode='wb') as video:
        video.write(video_content)
    cmd = cmd = f'ffmpeg -i {video_file} -i {audio_file} -c:v copy -c:a aac {output_file} -y'
    os.system(cmd)
    print(f'info:下载完成{title}')
    os.remove(audio_file)
    os.remove(video_file)
 
def download_file(url, headers, file_name):
    """
    下载文件的辅助函数。
    
    参数:
    url -- 资源的URL
    headers -- 请求头
    file_name -- 保存文件的名称
    
    返回:
    file_name -- 下载后的文件名
    """
    content = requests.get(url=url, headers=headers).content
    with open(file_name, mode='wb') as file:
        file.write(content)
    return file_name

def download_video_multithread(title, audio_url, video_url, BV, l, hearers=hearers, max_workers=4):
    """
    下载视频及其音频并合成文件。
 
    参数:
    title -- 视频的标题
    audio_url -- 视频的音频URL
    video_url -- 视频的视频URL
    BV -- 视频的BV号
    l -- 视频序号
    max_workers -- 最大线程数
    """
    hearer_SAFE = {
        "Cookie": hearers["Cookie"],
        "user-agent": hearers["user-agent"],
        "referer": f"https://www.bilibili.com/video/{BV}/?spm_id_from=333.999.0.0"
    }
    
    safe_title = re.sub(r"[$ :;(),&$？！￥…（|）—“”‘’《》、/\\。，？！@#￥%……&*（）——+【】、；‘’“”《》【】]", "", title)
    
    audio_file = f'audio{safe_title}.m4s'
    video_file = f'vidio{safe_title}.m4s'
    if l == 0:
        output_file = f'Output{safe_title}.mp4'
    else:
        output_file = f'Output{safe_title}{l}.mp4'
    
    print("info:", title, audio_url, video_url)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交音频和视频的下载任务
        future_audio = executor.submit(download_file, audio_url, hearer_SAFE, audio_file)
        future_video = executor.submit(download_file, video_url, hearer_SAFE, video_file)

        # 等待下载完成
        audio_result = future_audio.result()
        video_result = future_video.result()

    # 合成视频与音频
    cmd = f'ffmpeg -i {video_result} -i {audio_result} -c:v copy -c:a aac {output_file} -y'
    os.system(cmd)
    
    print(f'info: 下载完成 {title}')
    
    # 清理临时文件
    os.remove(audio_result)
    os.remove(video_result)


if __name__ == '__main__':
    """
    主程序，处理用户输入并调用其他函数实现视频下载功能。
    """
    input_mode = input('请输入模式\n1. 下载列表视频\n2. 下载组视频\n3. 下载单个视频\n')
    workers = input('多线程下载数')
    if input_mode == '1':
        input_list = input('请输入视频sid列表')
        BV_list = get_BV(sid=input_list,hearers=hearers)
        for BV in BV_list:
            title,audio_url,video_url = get_video_url(i=0,B_V=BV,Bool=True,hearers=hearers)
            download_video_multithread(title=title,audio_url=audio_url,video_url=video_url,BV=BV,l=1,hearers=hearers,max_workers=int(workers))
            print(f'info:下载完成{BV}')
    elif input_mode == '2':
        input_group = input('请输入BV号')
        input_num = int(input('请输入视频数量'))
        for i in range(1,input_num+1):
            title,audio_url,video_url = get_video_url(i,B_V=input_group,Bool=False,hearers=hearers)
            download_video_multithread(title=title,audio_url=audio_url,video_url=video_url,BV=input_group,l=i,hearers=hearers,max_workers=int(workers))
            print(f'info:下载完成{input_group}第{i}个视频')
    elif input_mode == '3':
        input_BV = input('请输入BV号')
        title,audio_url,video_url = get_video_url(i=0,B_V=input_BV,Bool=True,hearers=hearers)
        download_video_multithread(title=title,audio_url=audio_url,video_url=video_url,BV=input_BV,l=0,hearers=hearers,max_workers=int(workers))
        print(f'info:下载完成{input_BV}')
    else:
        print('输入错误')