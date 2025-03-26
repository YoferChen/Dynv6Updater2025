import os
import shutil


def setup():
    cmd = f"pyinstaller -w -F --version-file=version.txt -i logo.ico --clean dynv6_updater_2025.py -y"
    os.system(cmd)

    # 复制资源文件
    resourceFile = './logo.ico'
    targetDir = './dist'
    try:
        shutil.copy(resourceFile, targetDir)
        print(f'{resourceFile} has been copied to {targetDir}')
    except Exception as e:
        print(f'Failed to copy {resourceFile} to the {targetDir} directory, please manually operate')


if __name__ == '__main__':
    setup()
