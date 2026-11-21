from pathlib import Path
import shutil

# 1. 定义源文件路径
source = Path("test.txt")


# 2. 定义并创建目标文件夹
folder = Path("uploads")
# 3. 拼接目标文件路径
folder.mkdir(parents=True, exist_ok=True)
destination = folder / "test.txt"
# 4. 打开源文件和目标文件

# 5. 复制文件内容
with open(source, "rb") as src:
    with open(destination, "wb") as dst:
        shutil.copyfileobj(src, dst)
# 6. 检查目标文件是否存在
print(destination.exists())
