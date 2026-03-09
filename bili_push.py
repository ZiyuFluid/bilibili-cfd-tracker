import requests
import time
import os

# 配置你想搜索的关键词
KEYWORDS = ["fluent 仿真", "openfoam"]
# 获取环境变量中的 Server酱 Key
PUSH_KEY = os.environ.get("PUSH_KEY") 

def search_bilibili(keyword):
    """调用B站搜索API，按发布时间排序"""
    url = "https://api.bilibili.com/x/web-interface/search/type"
    params = {
        "search_type": "video",
        "keyword": keyword,
        "order": "pubdate" # pubdate 表示按最新发布排序
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        return response.json()
    except Exception as e:
        print(f"搜索 {keyword} 时出错: {e}")
        return None

def send_wechat(title, content):
    """通过 Server酱 发送微信推送"""
    if not PUSH_KEY:
        print("未配置 PUSH_KEY，跳过推送。内容如下：\n", content)
        return
    url = f"https://sctapi.ftqq.com/{PUSH_KEY}.send"
    data = {
        "title": title,
        "desp": content # 支持 Markdown 格式
    }
    requests.post(url, data=data)
    print("推送成功！")

def main():
    today_content = ""
    # 计算24小时前的时间戳
    yesterday_timestamp = time.time() - 24 * 3600

    for kw in KEYWORDS:
        data = search_bilibili(kw)
        if not data or data.get("code") != 0:
            continue
            
        videos = data.get("data", {}).get("result", [])
        # 筛选出最近24小时内发布的视频
        new_videos = [v for v in videos if v.get("pubdate", 0) > yesterday_timestamp]

        if new_videos:
            today_content += f"### 【{kw}】 新增视频：\n\n"
            for v in new_videos:
                # B站返回的标题带有 html 标签高亮，清理掉
                title = v.get("title").replace('<em class="keyword">', '').replace('</em>', '')
                link = v.get("arcurl")
                author = v.get("author")
                today_content += f"- **{title}** (UP主: {author})\n  [点击观看]({link})\n\n"

    if today_content:
        send_wechat("B站 Fluent/OpenFOAM 每日上新", today_content)
    else:
        print("今天没有新的相关视频发布。")

if __name__ == "__main__":
    main()
