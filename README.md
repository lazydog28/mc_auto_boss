# 鸣潮后台自动刷BOSS声骸 GPU

> 水群1：853749942（已满）
> 
> 水群2：497743900（不禁言，喜欢水群可以加）
> 
> 通知群：597280384（禁言、只发版本更新通知）
>
> 本项目基于OCR文字识别，图像识别，自动化操作等技术，实现了鸣潮后台自动刷BOSS声骸的功能
>
> 后台运行时可以有其他窗口遮挡，但是不可以最小化
>
> 仅供学习参考，未对游戏进行任何修改，不会对游戏平衡性产生影响
>
> 本项目基于python3.10开发，如有问题请提issue

## 前置条件

1. 游戏窗口仅支持16:9分辨率,推荐分辨率为1280x720,屏幕缩放为100%
2. 必须解锁借位信标，在击杀目标BOSS的战利品位置放置借位信标，保证传送到借位信标后能直接触发BOSS或者和声弦交互
3. 队伍中最好有一个奶妈，保证队伍不会因为BOSS的攻击而死亡
4. 脚本必须以管理员权限运行！
5. 项目路径中不能包含中文或特殊字符

## 使用方法

> GPU环境搭建：[GPU环境搭建 · lazydog28/mc_auto_boss Wiki (github.com)](https://github.com/lazydog28/mc_auto_boss/wiki/GPU环境搭建)

1. ### 下载本项目
    ```shell
    git clone https://github.com/lazydog28/mc_auto_boss.git
    cd mc_auto_boss
    ```
2. ### 安装依赖
    ```shell
    pip install -r requirements.txt
    ```
   > 当前为GPU分支，使用的模型为`paddleocr`提供的模型进行识别，如果需要使用其他OCR引擎，请自行修改代码
   >
   >  `paddlepaddle-gpu` 官方地址：[https://www.paddlepaddle.org.cn/install/quick](https://www.paddlepaddle.org.cn/install/quick)
   > 
   > 如果当前用户名为中文，请下载 `paddleocr` [模型文件](https://github.com/PaddlePaddle/PaddleOCR/blob/main/doc/doc_ch/models_list.md) 后自行修改`background/ocr.py`中实例化`PaddleOCR`的参数`det_model_dir`和`rec_model_dir`为绝对路径且不包含中文

3. ### 修改配置文件
    ```shell
    cp config.example.yaml config.yaml # 复制配置文件，
    ```
   修改`config.yaml`中的配置项，主要是 TargetBoss 改为你要刷的BOSS名称，如`飞廉之猩`，`鸣钟之龟`等，BOSS位置必须放置好借位信标


4. ### 运行项目
   请在运行之前保证游戏已经打开
    ```shell
    python background/main.py
    ```
   
   请在提示 `初始化完成` 后按 `F5` 开始刷BOSS
   
   | 快捷键  | 功能                   |
   |------|----------------------|
   | F5   | 开始刷BOSS              |
   | F7   | 暂停运行                 |
   | F12  | 停止运行                 |


5. ### 战斗策略
   | 策略            | 说明        |
   |---------------|-----------|
   | `a`           | 鼠标左键 普攻   |
   | `e`、`q`、`r` / | 技能、声骸、大招  |
   | `0.5`         | 等待0.5秒    |
   | `a~ `         | 重击（按下0.5秒） |
   | `e~ `         | 按下E键0.5秒  |
   | `a~2`         | 按下鼠标左键2秒, |
   | `e~2`         | 按下E键2秒,   |


6. ### todo
	* ~~优化内存占用~~
	* ~~记录战斗次数及吸取次数~~
	* 掉落声骸目标识别进行拾取<无妄者已实现、其他BOSS未训练>