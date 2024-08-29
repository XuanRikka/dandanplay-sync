# dandanplay-sync

## 基于弹弹play的播放进度同步

[![LICENSE](https://img.shields.io/badge/license-Anti%20996-blue.svg)](https://github.com/996icu/996.ICU/blob/master/LICENSE)

### 功能
- 以服务端播放进度为标准同步客户端播放进度
- 一个服务端可以链接多个客户端

### 服务端
1. 确保运行服务端的机器已经安装弹弹play及python
2. 打开弹弹play的"远程控制"功能
3. 创建虚拟环境并进入虚拟环境(可选)
```bash
python -m venv venv
./venv/bin/activate
```
4. 安装依赖
```bash
pip install -r requirements.txt
```
5. 运行服务端生成配置
6. 修改配置并再次运行服务端

### 客户端
1. 确保运行客户端的机器已经安装弹弹play及python
2. 打开弹弹play的"远程控制"功能
3. 创建虚拟环境并进入虚拟环境(可选)
```bash
python -m venv venv
./venv/bin/activate
```
4. 安装依赖
```bash
pip install -r requirements.txt
```
5. 运行客户端生成配置
6. 修改配置并再次运行客户端

## 许可证

本程序遵循 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 贡献

如果你有任何问题或建议，欢迎提出 [issue](https://github.com/username/dandanplay-sync/issues) 或 [pull request](https://github.com/username/dandanplay-sync/pulls)。
