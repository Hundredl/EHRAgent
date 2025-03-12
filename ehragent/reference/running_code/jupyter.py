import tempfile
import time
import subprocess
from jupyter_client import KernelManager

def jupyter_execute(code):
    with tempfile.TemporaryDirectory() as kernel_dir:
        # 启动 Jupyter 内核
        km = KernelManager()
        km.start_kernel(stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # 连接到 Jupyter 内核
        kc = km.client()
        kc.start_channels()

        try:
            # 执行代码
            msg_id = kc.execute(code)
            result = []

            while True:
                try:
                    reply = kc.get_iopub_msg(timeout=10)
                except Exception as e:
                    return None, f"Error reading output: {str(e)}"

                if reply["parent_header"].get("msg_id") == msg_id:
                    content = reply.get("content", {})

                    # 检查是否是 `execute_result` 或 `stream` 类型
                    if content.get("execution_state") == "idle":
                        break
                    if "text" in content:
                        result.append(content["text"])
                    elif "data" in content and "text/plain" in content["data"]:
                        result.append(content["data"]["text/plain"])
                    elif "name" in content and content["name"] == "stdout":
                        result.append(content["text"])

            # 获取输出
            output = "\n".join(result)
            return output, None
        except Exception as e:
            return None, str(e)
        finally:
            kc.stop_channels()
            km.shutdown_kernel()

# 测试运行
# code = 'print("Hello World from Jupyter!")'
# stdout, stderr = jupyter_execute(code)
# print("输出:", stdout if stdout else f"错误: {stderr}")

# code = 'import sys; print("Python executable:", sys.executable)'
# stdout, stderr = jupyter_execute(code)
# print("输出:", stdout if stdout else f"错误: {stderr}")


def test_jupyter_environment():
    code = '''
import sys
import os

print("Python executable:", sys.executable)
print("sys.prefix:", sys.prefix)
print("Inside virtual environment:", sys.prefix != sys.base_prefix)
print("Conda environment:", os.environ.get("CONDA_PREFIX"))
print("Pip location:", os.popen("which pip" if os.name != "nt" else "where pip").read().strip())

import torch    
print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
# print gpu list
print("GPU list:", torch.cuda.device_count())

!ls
!pwd

# 执行命令 python yueying/ehr_run.py

# os.system("python yueying/ehr_run.py")
# python yueying/hello.py

from yueying.ehr_run import run
run()

'''
    stdout, stderr = jupyter_execute(code)
    print("输出:\n", stdout if stdout else f"错误: {stderr}")

# 运行测试
test_jupyter_environment()