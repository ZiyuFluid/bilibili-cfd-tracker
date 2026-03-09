import requests
import time
import os

# 配置你想搜索的关键词
KEYWORDS = ["fluent 仿真", "openfoam"]
PUSH_KEY = os.environ.get("PUSH_KEY") 
BILI_COOKIE = os.environ.get("BILI_COOKIE")

def search_bilibili(keyword):
    """调用B站搜索API，按发布时间排序"""
    url = "https://api.bilibili.com/x/web-interface/search/type"
    params = {
        "search_type": "video",
        "keyword": keyword,
        "order": "pubdate"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": BILI_COOKIE if BILI_COOKIE else "",
        "Referer": "https://search.bilibili.com/all" # 【新增】告诉B站：我是从搜索主页点进来的，别拦我
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        
        # 【新增】详细打印拦截原因
        if response.status_code != 200 or not response.text.strip().startswith('{'):
            print(f"被拦截了！HTTP状态码: {response.status_code}")
            print(f"B站返回的网页内容(前300字): {response.text[:300]}")
            return None
            
        return response.json()
    except Exception as e:
        print(f"搜索 {keyword} 时程序崩溃: {e}")
        return None

def send_wechat(title, content):
    """通过 Server酱 发送微信推送"""
    if not PUSH_KEY:
        print("未配置 PUSH_KEY，跳过推送。内容如下：\n", content)
        return
    url = f"https://sctapi.ftqq.com/{PUSH_KEY}.send"
    data = {
        "title": title,
        "desp": content
    }
    requests.post(url, data=data)
    print("推送成功！")

def main():
    today_content = ""
    time_limit = time.time() - 5 * 24 * 3600

    if not BILI_COOKIE:
        print("⚠️ 警告：没有检测到 BILI_COOKIE！程序可能会被拦截。")

    for kw in KEYWORDS:
        print(f"正在抓取关键词: {kw} ...")
        data = search_bilibili(kw)
        if not data or data.get("code") != 0:
            print(f"获取 {kw} 数据失败。API返回的JSON: {data}")
            continue
            
        videos = data.get("data", {}).get("result", [])
        new_videos = [v for v in videos if v.get("pubdate", 0) > time_limit]

        if new_videos:
            today_content += f"### 【{kw}】 新增视频：\n\n"
            for v in new_videos:
                title = v.get("title").replace('<em class="keyword">', '').replace('</em>', '')
                link = v.get("arcurl")
                author = v.get("author")
                today_content += f"- **{title}** (UP主: {author})\n  [点击观看]({link})\n\n"

    if today_content:
        send_wechat("B站 Fluent/OpenFOAM 最近5天更新", today_content)
    else:
        print("最近5天没有新的相关视频发布。")

if __name__ == "__main__":
    main()
