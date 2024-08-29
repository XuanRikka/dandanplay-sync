from dataclasses import dataclass
from json import loads
import httpx_ws
import httpx
import yaml
import os

default_yaml = """server: "host:port" # 链接的服务端的ip及端口
dandanplay: "host:port" # dandanplay远程访问的ip及端口
tolerance_time: 5000 # 可以接受的容差，单位为毫秒
video_validation: True # 是否检测视频一致性,禁用可能导致一系列问题
"""

headers = {
    "Content-Type": "application/json; charset=utf-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0"
}


@dataclass
class Config:
    server: str
    dandanplay: str
    tolerance_time: int
    video_validation: bool


config: Config | dict


def init():
    global config
    if not os.path.exists("config.yml") and not os.path.isfile("config.yml"):
        open("config.yml", "w").write(default_yaml)
        print("检测到配置文件不存在，已经自动生成配置文件")
        print("请修改配置后再启动")
        exit(0)
    with open("config.yml", "r") as f:
        config = yaml.safe_load(f)

    config = Config(**config)

    try:
        httpx.get(f"{config.dandanplay}/welcome", headers=headers)
    except httpx.ConnectError:
        print("链接dandanplay客户端远程访问失败")


def get_hash(video_data: dict[str, str]) -> str:
    title = video_data["AnimeTitle"]
    all_video = loads(httpx.get(f"http://{config.dandanplay}/api/v1/library", headers=headers).text)
    video_hash = ""
    for i in all_video:
        if i["AnimeTitle"] == title:
            video_hash = i["Hash"]
    return video_hash


def main():
    with httpx_ws.connect_ws(f"ws://{config.server}") as ws:
        data = ws.receive_json()
        if data["type"] == "disconnect":
            print(f"error: {data['message']}")
            exit(0)
        if data["type"] == "handshake":
            print("与服务端握手成功")
        video_data = loads(httpx.get(f"http://{config.dandanplay}/api/v1/current/video", headers=headers).text)
        video_hash = get_hash(video_data)
        while video_hash != data["hash"] and config.video_validation:
            if video_hash:
                print("客户端播放视频hash与服务端播放视频不同，请播放相同的视频")
            else:
                print("客户端没有在播放视频")
            video_data = loads(httpx.get(f"http://{config.dandanplay}/api/v1/current/video", headers=headers).text)
            video_hash = get_hash(video_data)
        while True:
            print("a")
            sync_data = ws.receive_json()
            play_data = loads(httpx.get(f"http://{config.dandanplay}/api/v1/current/video", headers=headers).text)
            client_time = play_data["Duration"]*play_data["Position"]
            if int(sync_data["time"])-config.tolerance_time < client_time < int(sync_data["time"])+config.tolerance_time:
                continue
            time = sync_data["time"]
            print("客户端与服务端进度出现差异，已校准，从服务端获取到的时间：", time)
            print(f"http://{config.dandanplay}/api/v1/control/seek/{time}")
            httpx.get(f"http://{config.dandanplay}/api/v1/control/seek/{time}", headers=headers)


if __name__ == "__main__":
    init()
    main()
