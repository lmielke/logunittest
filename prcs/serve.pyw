import os
import subprocess

template = os.path.expanduser(r'~/python_venvs/libs/logunittest/logunittest/src/actions/serve.py')
executable = os.path.expanduser(r'~/.virtualenvs/logunittest-sg8orfNO/Scripts/python.exe')
workingdir = os.path.expanduser(r'~/python_venvs/libs/logunittest')

os.chdir(workingdir)
cmds = ['pipenv', 'run', 'python', template, 'serve', '-n', 'digiserver', '-rt', '-v', '2']
subprocess.Popen(cmds, shell=True)

# subprocess.call(['python', template, 'serve', '-n', 'digiserver', '-rt', '-v', '2'], shell=True,
#                 executable=executable)