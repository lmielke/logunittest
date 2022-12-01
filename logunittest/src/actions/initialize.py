# info.py
import logunittest.src.settings as sts
import subprocess
import os, sys
import configparser
import subprocess
import colorama as color

color.init()

paName = 'logunittest'
prName = 'logunittest'
alias = 'lut'


def main(*args, **kwargs):
    print(f"filePath to be changed: {sts.projectPath}")
    if not input(f"Want to continue renaming all files in {sts.projectPath}? [y/n] default is N: ").upper():
        exit()
    files = sorted([(d, f) for d, ds, fs in os.walk(sts.projectPath) for f in fs], 
                        key=lambda x: len(x[0].split(os.sep)), reverse=True)
    rename(files, *args, **kwargs)

def rename(files, *args, packageName, **kwargs):
    for i, (fileDir, fileName) in enumerate(files):
        print(f"next {i}: {fileDir}, {fileName}")
        if os.path.isfile(os.path.join(fileDir, fileName)):
            try:
                with open(os.path.join(fileDir, fileName), 'r') as f:
                    text = f.read()
                while paName in text: text = text.replace(paName, packageName)
                while prName in text: text = text.replace(prName, packageName)
                while alias in text: text = text.replace(alias, packageName[:max(6, len(packageName))])
                
                with open(os.path.join(fileDir, fileName), 'w') as f:
                    f.write(text)
            except:
                pass

        if fileName in [prName, paName]:
            os.rename(os.path.join(fileDir, fileName), os.path.join(fileDir, prName))

        if os.path.basename(fileDir) in [prName, paName]:
            os.rename(fileDir, os.path.join(os.path.dirname(fileDir), prName))

if __name__ == "__main__":
    main()
