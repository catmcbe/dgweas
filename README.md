# 一哈基三米 - Pygame游戏

这是一个使用Pygame开发的塔防三消混合游戏。

## 游戏特点

- 经典模式和战斗模式
- 冒险模式和无尽模式
- 三消游戏机制与塔防结合
- 支持多用户账户系统
- 背景音乐和音效

## 使用GitHub Actions打包

本项目配置了GitHub Actions，可以自动为Windows、Linux和macOS平台打包可执行文件。

### 自动打包流程

1. 将代码推送到GitHub仓库的main分支
2. GitHub Actions会自动触发打包流程
3. 打包完成后，可以在Actions页面下载三个平台的可执行文件

### 打包产物

- `hajimipvz-windows`: Windows版本 (.exe)
- `hajimipvz-linux`: Linux版本
- `hajimipvz-macos`: macOS版本

### 手动触发打包

你也可以在GitHub的Actions页面手动触发打包流程：

1. 进入仓库的Actions标签页
2. 选择"Package Application with Pyinstaller"工作流
3. 点击"Run workflow"按钮
4. 选择分支并点击"Run workflow"

## 本地开发

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行游戏

```bash
python integrated_game.py
```

## 依赖项

- pygame==2.5.2
- opencv-python==4.8.1.78
- moviepy==1.0.3

## 游戏控制

- 鼠标点击进行三消操作
- 点击按钮进行游戏设置
- 支持音量调节和游戏难度调整

## 账户系统

游戏支持多用户账户，每个用户有独立的进度和最高分记录。

## 开发者

哔哩哔哩 我就是仁菜
