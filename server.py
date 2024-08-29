from httpx import AsyncClient, get, ConnectError
from fastapi import FastAPI, WebSocket, logger
from dataclasses import dataclass
from asyncio import sleep
from uvicorn import run
from json import loads
import yaml
import os


app = FastAPI()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0"
}


@dataclass
class Config:
    server_port: int
    dandanplay: str
    sync_interval: int


default_yaml = """server_port: 2333 # 服务端运行在哪个端口上
dandanplay: "host:port" # dandanplay远程访问的地址
sync_interval: 5 # 校准的间隔，一般不建议太短，可能会导致客户端处理不过来所以客户端播放鬼畜
"""


def init():
    if not os.path.exists("server_config.yml") and not os.path.isfile("server_config.yml"):
        open("server_config", "w").write(default_yaml)
    config = Config(**yaml.safe_load(open("server_config.yml", "r").read()))

    global config
    try:
        get(f"http://127.0.0.1:{ddport}/welcome", headers=headers)
    except ConnectError:
        print("链接dandanplay远程访问失败")
        exit(-1)


async def get_hash(video_data: dict[str, str], client: AsyncClient) -> str:
    title = video_data["AnimeTitle"]
    all_video = loads((await client.get(f"http://{config.dandanplay}/api/v1/library", headers=headers)).text)
    video_hash = ""
    for i in all_video:
        if i["AnimeTitle"] == title:
            video_hash = i["Hash"]
    return video_hash

@app.websocket("/")
async def _(ws: WebSocket):
    await ws.accept()
    async with AsyncClient() as client:
        video_data = loads((await client.get(f"http://{config.dandanplay}/api/v1/current/video", headers=headers)).text)
        if video_data["AnimeTitle"] is None:
            await ws.send_json({
                "type": "disconnect",
                "message": "服务端未在播放视频"
            })
            await ws.close()
        video_hash = await get_hash(video_data, client)
        if not video_hash:
            await ws.send_json({
                "type": "disconnect",
                "message": "获取服务端播放视频hash失败"
            })
            logger.error("获取服务端播放视频hash失败,请播放存在于媒体库的视频")
            await ws.close()
            exit(-1)
        await ws.send_json({
            "type": "handshake",
            "hash": video_hash
        })
        while True:
            await sleep(config.sync_interval)
            play_data = loads((await client.get(f"http://{config.dandanplay}/api/v1/current/video", headers=headers)).text)
            print(play_data["Duration"],play_data["Position"])
            time = int(play_data["Duration"]*play_data["Position"])
            await ws.send_json({
                "type": "sync",
                "time": str(time)
            })
            print("发送校准包，time:", time)


if __name__ == "__main__":
    init()
    run(app, host="0.0.0.0", port=config.server_port)

