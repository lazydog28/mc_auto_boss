@echo off
cd /d %~dp0
goto menu
:menu
ECHO.************************************************************************
ECHO.                             	             主菜单
ECHO.
ECHO.
ECHO. 				0.         安装依赖
ECHO. 
ECHO. 				1. 	   启动脚本
ECHO.
ECHO. 				2. 	   更新项目
ECHO.
ECHO.************************************************************************
ECHO.
set sel=		
set  /p sel=请输入序号,并按回车Enter： 
ECHO.
if “%sel%”==“0” goto installModule
if “%sel%”==“1” goto initiateScript
if “%sel%”==“2” goto openProject


:installModule
conda activate mc
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple 
goto ReturnMenu

:initiateScript
call conda activate mc
python ./background/main.py




:openProject
start "" "https://github.com/lazydog28/mc_auto_boss/"
goto ReturnMenu


:ReturnMenu
  	
  @echo off	
  	echo.
  	echo 按任意键返回主菜单
  	pause >nul
        cls
  	goto menu
        
