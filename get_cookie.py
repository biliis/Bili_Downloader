import json
import httpx
import qrcode
import os
import time

def get_qrurl() -> list:
    """返回qrcode链接以及token"""
    with httpx.Client() as client:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
        }
        url = 'https://passport.bilibili.com/x/passport-login/web/qrcode/generate?source=main-fe-header'
        data = client.get(url=url, headers=headers)
    total_data = data.json()
    qrcode_url = total_data['data']['url']
    qrcode_key = total_data['data']['qrcode_key']
    data = {}
    data['url'] = qrcode_url
    data['qrcode_key'] = qrcode_key
    return data

def make_qrcode(data):
    """制作二维码"""
    qr = qrcode.QRCode(
        version=5,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data['url'])
    qr.make(fit=True)
    # fill_color和back_color分别控制前景颜色和背景颜色，支持输入RGB色，注意颜色更改可能会导致二维码扫描识别失败
    img = qr.make_image(fill_color="black")
    img.show()


def sav_cookie(data, id):
    """用于储存cookie"""
    try:
        with open(f'./bilibili_login/cookie/{id}.json', 'w') as f:
            json.dump(data, f, ensure_ascii=False)
    except FileNotFoundError:
        path = os.getcwd()
        path_0 = path.replace('\\', '/')
        path0 = path_0 + '/bilibili_login/cookie'
        os.mkdir(path0)
        with open(f'./bilibili_login/cookie/{id}.json', 'w') as f:
            json.dump(data, f, ensure_ascii=False)

def main_run():
    """主函数"""
    data = get_qrurl()
    token = data['qrcode_key']
    make_qrcode(data)
    panding = False
    while panding == False:

        with httpx.Client() as client:
            headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
        }
            url = f"https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key={token}&source=main-fe-header"
            data_login = client.get(url=url, headers=headers)  # 请求二维码状态
            data_login = json.loads(data_login.text)
        code = int(data_login['data']['code'])
        if code == 0:
            cookie = dict(client.cookies)
            sav_cookie(cookie, cookie['DedeUserID'])
            cookie_0 = cookie
            print('SESSDATA='+cookie_0['SESSDATA']+';bili_jct='+cookie_0['bili_jct']+';DedeUserID='+cookie_0['DedeUserID']+'; DedeUserID__ckMd5='+cookie_0['DedeUserID__ckMd5']+';sid='+cookie_0['sid'])
            break
        else:
            print('二维码未扫描')
            time.sleep(3)
            continue
if __name__ == "__main__":
    main_run()
