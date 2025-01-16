1. ### 下载本项目
    先下载代码管理工具git，安装windows版，打开链接，点击64-bit Git for Windows Setup    
    [https://git-scm.com/downloads/win](https://git-scm.com/downloads/win)    
    一直点下一步即可完成安装git

    使用git下载本项目，先打开梯子，比如将项目下载到D盘    
    打开cmd或powershell执行以下命令下载项目：
    ```shell
    cd D:
    ```
    ```shell
    git clone https://github.com/wakening/mc_auto_boss.git
    ```

    拓展：当项目有更新，可进入项目目录，打开梯子，使用git更新项目：    
    打开cmd或powershell执行以下命令
    ```shell
    cd D:\mc_auto_boss
    ```
    ```shell
    git pull
    ```
3. ### 安装 python 3.10.x
    双击python-3.10.11-amd64.exe    
    点击Add python.exe to Path    
    一直点下一步完成安装

4. ### 安装 CUDA 12
    打开cmd或powershell执行以下命令：
    ```shell
    nvidia-smi
    ```
    查看CUDA Version的值，此为你电脑当前显卡驱动支持的最高cuda版本    
    下载 CUDA 12.x，选择小于上方版本的下载    
    [https://developer.nvidia.com/cuda-toolkit-archive](https://developer.nvidia.com/cuda-toolkit-archive)    
    安装，选自定义，只勾选安装CUDA，取消勾选其他组件
    
    下载cuDNN，比如cuDNN v8.9.7, for CUDA 12.x    
    [https://developer.nvidia.com/rdp/cudnn-archive](https://developer.nvidia.com/rdp/cudnn-archive)    
    解压zip文件，将所有文件夹（如：bin include lib）复制到cuda安装路径内    
    比如我安装的是cuda12.6，那么位置就在：C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\

6. ### 安装依赖
   先进入项目目录，打开cmd或powershell执行以下命令：
   ```shell
    cd D:\mc_auto_boss
    ```   
   1.安装paddlepaddle-gpu
   ```shell
   python -m pip install paddlepaddle-gpu==2.6.1.post120 -f https://www.paddlepaddle.org.cn/whl/windows/mkl/avx/stable.html
   ```
   上方链接可能随官方升级而变化，官方地址：[https://www.paddlepaddle.org.cn/install/quick](https://www.paddlepaddle.org.cn/install/quick)    
   打开网址后，选择2.6 windows pip 英伟达 CUDA12.0，可获得最新版本，下方就是文档，有验证是否安装正确的教程    
   2.安装onnxruntime-gpu：
   ```shell
   pip install onnxruntime-gpu==1.18.0 --extra-index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/onnxruntime-cuda-12/pypi/simple/
   ```
   CUDA、cuDNN、onnx三者兼容版本参考：    
   https://github.com/microsoft/onnxruntime/issues/22198#issuecomment-2376010703    
   https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html    
   本教程使用的是CUDA12.x、cuDNNv8.9.x、onnx1.18.0    
    3.安装剩余依赖：
    ```shell
   pip install --upgrade -r requirements_gpu_cuda12.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

