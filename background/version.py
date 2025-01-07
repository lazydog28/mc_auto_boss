__version__ = "2.0.4"
description = "更新"

# ver2.0.4
# update:2025-01-07
# updated by wakening
# 1.部分boss增加行走距离，防止锁定不上
# 2.修复因游戏太卡，脚本误判传送已完成过早行走，导致真正传送完成后角色不动的bug
# 3.删除config.example.yaml内参数FightTacticsUlt、DetectionUE4、BossWaitTime_Dreamless、BossWaitTime_Jue、WaitUltAnimation，程序内部这些都还在，只是开放出来修改无意义，都隐藏掉

# ver2.0.3
# update:2025-01-05
# updated by wakening
# 1.修复罗蕾莱传送后因判断过快，导致未识别到不在家；罗蕾莱增加行走距离，防止锁定不上
# 2.优化复活流程，复活中途出现异常时中止复活重新回到大世界接着打boss，因为是偶发，下次还能正常复活

# ver2.0.2
# update:2025-01-04
# updated by wakening
# 1.F6声骸合成、F8声骸锁定增加新套装识别，请参考echo_config.example.yaml内的说明重新配置echo_config.yaml
# 2.罗蕾莱不在家时，调整时间到半夜；修复部分角色传送到赫卡忒处无法交互的问题
# 3.增加关闭显卡驱动版本过旧弹窗

# ver2.0.1
# update:2025-01-04
# updated by wakening
# 1.支持所有新boss，异构武装、赫卡忒、罗蕾莱、叹息古龙、7个梦魇boss，新boss都不需要插信标, config.example.yaml内也有详细说明
# 2.其他不重要的小功能等下个版本

# ver2.0.0
# update:2025-01-03
# updated by wakening
# 1.支持新boss：异构武装、赫卡忒，这两个都不需要插信标, config.example.yaml内也有详细说明，其他新boss暂不支持，等下个版本
# 2.修复无妄者传送，修复角色阵亡传送
# 3.其他不重要的小功能没写修复就是没修复，等下下个版本

# ver1.4.1
# update:2024-11-18
# updated by wakening
# 1.修复角传送识别过快导致误判传送完成导致没打就走了，增加等待时间

# ver1.4.0
# update:2024-11-16
# updated by wakening
# 1.修复大世界传送到boss战边缘不进战斗的bug
# 2.修复角传送，无需插借位信标

# ver1.3.3
# update:2024-10-15
# updated by wakening
# 1.优化鼠标重置，鼠标瞬时位移大且是被抢去游戏窗口中心时才触发
# 2.优化重新挑战，不再因触发其他流程导致出现不相干的日志
# 3.优化声骸搜索，声骸掉在正前方被人物挡住可能会识别不到，在最后加一次前行检索
# 4.优化boss传送，增加延时时间，防止卡顿等导致传送失败
# 5.修复新增的加载界面里包含终端字眼导致传送误判的bug
# 6.修复无妄者卡在领取奖励不能搜索声骸（可正常离开）

# ver1.3.2
# update:2024-10-06
# updated by wakening
# 1.修复无妄者物资领取上限后卡在领取弹窗无法离开的bug
# 2.优化复活点击地图时增加延时和点击次数，防止卡顿等导致传送失败

# ver1.3.1
# update:2024-10-01
# updated by wakening
# 1.修复F8声骸锁定不能用的bug
# 2.增加功能，F8声骸锁定支持识别声骸名称，4C声骸支持每种单独配置词条，详见echo_config.example.yaml，兼容旧版
# 3.移除龟龟快打，原地传送跳过起身等待时间已被修复
# 4.优化复活，无感快速检测，复活点改为今州城

## ver1.3.0
# update:2024-09-29
# updated by wakening
# 1.支持新boss无归的谬误
# 2.修复不能打boss的bug，无妄者、角在单刷时支持重新挑战

# ver1.2.7
# update:2024-09-24
# updated by wakening
# 1.F8,F6支持在大世界页面执行，可自动进入背包、合成页面，并在结束后返回大世界
# 2.命令行F8,F6,F5支持组合执行，例启动后先合成再打无妄者：python background/main.py -t F6,F5 -c config-dreamless.yaml
# 3.去除合成的图片匹配改为像素比例定位，防止再出现合成异常
# 4.新增环境搭建步骤，见：CUDA12环境搭建.md

# ver1.2.6
# update:2024-08-18
# updated by wakening
# 1.修复1.2版本锁定合成异常的bug
# 2.优化ue4崩溃检测，将发送关闭窗口消息改为停止游戏进程，删除检测进程，移除pyautogui依赖
# 3.修复战斗统计异常时重置计数
# 4.支持在不修改编队的情况下，调整出战顺序，即可将3号位维里奈以1号姿态出击，确保等待战斗时先上盾，见config.yaml参数FightOrder
# 5.修复F7/F12无法停止程序的bug
# 6.删除F9相关代码

# ver1.2.5
# update:2024-07-19
# updated by ArcS17
# 1.连招支持闪避动作: l(小写L)
# 2.首次治疗传送自动调整地图缩放 From RinRose0
# 3.加快搜索声骸镜头重置
# 4.增加大招动画等待所支持分辨率

# ver1.2.4
# update:2024-07-16
# updated by ArcS17
# 1.新增指定周本Boss等待时间
# 2.新增声骸文件配置提醒
# 3.修复截取窗口失败TypeError，默认连续已锁声骸检测阈值过低，声骸分值计算功能角色名称错误
# 4.重写F9后调用逻辑，重写F9功能使用提醒

# ver1.2.3
# update:2024-07-08
# updated by wakening
# 1.支持国服、b服账号登录弹窗识别，并自动点击登录

# ver1.2.2
# update:2024-07-08
# updated by ArcS17
# 1.新增初始化时config文件不存在以example为模板自动生成完整格式及风格的config文件
# 2.absorption_action完成后统计一次吸收率
# 3.config.example.TargetBoss示例增加角
# 4.对齐日志各Level输出


# ver1.2.1
# update:2024-07-08
# updated by wang115t
# 1.重构代码，副本打完BOSS卡加载后，自动重启游戏的功能
# 2.过副本支持显示进度条


# ver1.2.0
# update:2024-07-07
# updated by wang115t
# 1.重构代码，角脚本卡加载后，自动重启游戏的功能

# ver1.1.0
# update:2024-07-06
# updated by wang115t
# 1.新增角脚本卡加载后，自动重启游戏的功能

# ver1.0.9
# update:2024-07-05
# updated by wang115t
# 1.游戏更新完成后，通过点击退出按钮来重新启动游戏。
# 2.新增UE4弹窗崩溃后，自动重启游戏。
# 3.注意：需要安装pyautogui依赖
# 4.自定义检测UE4崩溃弹窗间隔时间，在config.yaml中进行配置

# ver1.0.8
# update:2024-07-05
# updated by ArcS17
# 1.优化了游戏窗口崩溃后重启启动游戏及脚本的逻辑
# 2.修复了一个BUG（崩溃后log统计战斗次数为0会抛出TypeError: cannot unpack non-iterable NoneType object）
# 3.增加了在config文件设置游戏定时重启的功能
# 4.增加了多次截取游戏窗口失败后重启游戏及脚本的功能
# 5.增加了声骸锁定及声骸合成功能对1600*900分辨率1.0缩放、1366*768分辨率1.0缩放的适配
# 6.增加了声骸识别失败后主动抛出适配分辨率提醒

# ver1.0.7
# update:2024-07-03
# updated by wakening
# 1.修复声骸锁定异常退出bug
# 2.声骸锁定代码逻辑优化，提升执行速度

# ver1.0.6
# update:2024-06-27
# updated by wakening
# 1.增加了命令行参数-t/--task，可以在启动后立即打boss，无需再按快捷键
# 2.增加了命令行参数-c/--config，可以指定自定义的配置文件，打不同boss使用不同配置启动

# ver1.0.5
# update:2024-06-26
# updated by RoseRin0
# 1.增强了合成功能的实用性。
# 2.修改了部分变量的名字
# 3.修复了部分设备上对【湮灭】词条的识别问题。
# 4.将isCrashes.txt移至项目根目录

# ver1.0.4
# update:2024-06-22
# updated by wang115t
# 1.新增防止游戏崩溃的功能，实时检测游戏窗口
# 2.修复游戏崩溃后，数据重置为0的问题

# ver1.0.3
# update:2024-06-22
# updated by RoseRin0
# 1.增加了背包自动识别声骸属性并锁定的功能。实验性

# ver1.0.2
# update:2024-06-19
# updated by RoseRin0
# 1.修复了一个BUG，该BUG导致直接使用example配置会闪退。（删除了example文件中的大招技能连段后的“,”）
# 2.增加了BOSS起身无敌时间的判断。
# 3.将日志文件默认路径改为了项目根目录。
# 4.增加了防倒卖的受骗说明。

# ver1.0.1
# update:2024-06-19
# updated by RoseRin0
# 1.更新了大招连段。（如大招动画判断可用）
# 2.添加了版本管理文件，以方便管理版本。
# 3.添加了日志功能，可在config中更改日志文件路径，默认为：C:\mc_log.txt
