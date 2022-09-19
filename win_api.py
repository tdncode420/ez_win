'''Methods specific to Windows operating system'''


from os import path, walk, sep, popen
import os
import re
import pythoncom
from win32com.shell import shell
import pywinauto
import win32api
import win32gui
import win32con
import win32process
import win32security
import multiprocessing
import time
from subprocess import check_output

ROOT = os.path.abspath(os.sep)
USER_NAME = os.getlogin()
APP_DATA = os.path.join(ROOT, 'Users', USER_NAME, 'AppData')
LOCAL_APP_DATA = os.path.join(APP_DATA, 'Local')
ROAMING_APP_DATA = os.path.join(APP_DATA, 'Roaming')

def getProcIds() -> list:
    '''Get a list of all current process'/threads by their PID's 
    
        Returns:
        (list(int)) - a list of process_id(int)'s
        
        getProcIds()
        >> [4364, 8704, 13016, 11180, ...]
    '''
    
    thelist = []

    def findit(hwnd, ctx):
        thelist.append(win32process.GetWindowThreadProcessId(hwnd)[1])
    win32gui.EnumWindows(findit, None)
    return thelist



def getThreadIds() -> list:
    '''Get a list of all current process'/threads by their TID's
    
        Returns:
        (list(int)) - a list of thread_id(int)'s
    
        getThreadIds()
        >> [3876, 3876, 7256, 5284, ...]
    '''
    
    thelist = []

    def findit(hwnd, ctx):
        thelist.append(win32process.GetWindowThreadProcessId(hwnd)[0])
    win32gui.EnumWindows(findit, None)
    return thelist


def getProcWinTxts() -> list:
    '''Get a list of all current process'/threads by their Window Text
    
        Returns:
        list(str) - a list of window_title_text(str)'s
        
        getProcWinTxts()
        >> ['Task Host Window', 'DWM Notification Window', '', 'Program Manager', ...]
    '''
    
    thelist = []

    def findit(hwnd, ctx):
        thelist.append(win32gui.GetWindowText(hwnd))
    win32gui.EnumWindows(findit, None)
    return thelist

def getHwndBy(by: ["title", "pid", "tid"], value: str) -> list:
    '''Get Process By 'title' | 'id'
    
        Parameters:
            by (str): 'title' | 'id'
            value (str): the value corresponding to the 'by' arg
            
        Returns:
        list(int): a list of HWND(int)'s matching the pattern provided
    
    
        getHwndBy('title', 'Battery Meter')
        >> [131594]
    
    '''
    
    if by == "title":
        found = []
        def findit(hwnd, ctx):
            if win32gui.GetWindowText(hwnd) == value:
                found.append(hwnd)
        win32gui.EnumWindows(findit, None)
        return found
    elif by == "pid":
        found = []
        def findit(hwnd, ctx):
            if win32process.GetWindowThreadProcessId(hwnd)[1] == value:
                found.append(hwnd)
        win32gui.EnumWindows(findit, None)
        return found
    elif by == "tid":
        found = []
        def findit(hwnd, ctx):
            if win32process.GetWindowThreadProcessId(hwnd)[0] == value:
                found.append(hwnd)
        win32gui.EnumWindows(findit, None)
        return found
    else:
        return


def getAvailCmds() -> list:
    '''Get a list of all available commands as found as an '.exe' within the 'windows/system32' directory (command prompt built-ins NOT included)
    
        Returns:
        list(str): a list of available command names found (a command .exe file without the '.exe')
    
    
        getAvailCmds()
        >> ['agentactivationruntimestarter', 'aitstatic', 'alg', ..., 'chkdsk', 'chkntfs', 'choice', 'CIDiag', 'cipher', ...]
    '''
    
    cmds = []
    CMD_PATH = "C:\\Windows\\System32"
    all_files = os.listdir(CMD_PATH)
    for file_ in all_files:
        x = re.search(".exe$", file_)
        if x:
            cmds.append(file_.replace(".exe", ""))
    return cmds

def getCmdOut(cmd, shell=False):
    '''Runs the provided command and returns the output. If command is invalid, returns False
    
        Returns:
        str: the stdout of the command given
        
        getCmdOut('echo hi')
        >> hello
    
    '''
    
    try:
        return check_output(cmd, shell=shell).decode()
    except Exception:
        return False


def findFile(fname, root=path.abspath(sep), find_all=False, timeout=None):
    '''Searches for a given file by file name recursively
    
        NOTE: Depending on where the file being searched for is located and what root directory the search is started in (aka 'root' arg), this method may take a little time to complete, especially if arg 'find_all' is set to True. To control the amount of execution time that you find acceptable, refer the the 'timeout' arg.
    
        Parameters:
            fname (str): the name of the file to search for
            root (str): the directory to start the search in. Default is the os root ('c:')
            find_all (bool): search for all files matching pattern; If False, will return path after finding the first match
            timeout (int): a number (in seconds) to run the function until returning
    
        Returns:
            str | None: the path to the file if found, None if not found
        
        # using default arg values
        findFile('chkdsk.exe')
        >> ['c://windows/system32/chkdsk.exe']
        
        # specifying 'root' directory to start in, reducing execution time
        findFile('chkdsk.exe', root='c://windows/system32')
        >> ['c://windows/system32/chkdsk.exe']
        
        # Search for all found instances
        findFile('chkdsk.exe', root='c://windows/system32, find_all=True')
        >> ['c://windows/system32/chkdsk.exe']
    
        # specifying the amount amount of execution time allowed (in this case, 10 seconds)
        findFile('chkdsk.exe', root='c://windows/system32', find_all=True, timeout=10)
        >> ['c://windows/system32/chkdsk.exe']
    '''
    
    found = []
    def run():
        for rt, dirs, files in walk(root):
            for f in files:
                if f == fname:
                    if not find_all:
                        return path.join(rt, f)
                    found.append(path.join(rt, f))
                    
    if timeout is not None and isinstance(timeout, int):            
        p = multiprocessing.Process(target=run, name="Run", args=(timeout,))
        p.start()
        time.sleep(10)
        p.terminate()
        p.join()
    else:
        run()
                      
    return found


def findDir(dname, root=path.abspath(sep), find_all=False, timeout=None):
    '''Searches for a given directory by directory name recursively
    
        NOTE: Depending on where the directory being searched for is located and what root directory the search is started in (aka 'root' arg), this method may take a little time to complete, especially if arg 'find_all' is set to True. To control the amount of execution time that you find acceptable, refer the the 'timeout' arg.
    
        Parameters:
            dname (str): the name of the directory to search for
            root (str): the directory to start the search in. Default is the os root ('c:')
            find_all (bool): search for all directories matching pattern; If False, will return path after finding the first match
            timeout (int): a number (in seconds) to run the function until returning
    
        Returns:
            str | None: the path to the directory if found, None if not found
        
        # using default arg values
        findDir('system32')
        >> ['c://windows/system32']
        
        # specifying 'root' directory to start in, reducing execution time
        findDir('system32', root='c://windows')
        >> ['c://windows/system32']
        
        # Search for all found instances
        findDir('system32', root='c://windows, find_all=True')
        >> ['c://windows/system32']
    
        # specifying the amount amount of execution time allowed (in this case, 10 seconds)
        findDir('system32', root='c://windows', find_all=True, timeout=10)
        >> ['c://windows/system32']
    '''

    found = []

    def run():
        for rt, dirs, files in walk(root):
            for f in files:
                if f == fname:
                    if not find_all:
                        return path.join(rt, f)
                    found.append(path.join(rt, f))

    if timeout is not None and isinstance(timeout, int):
        p = multiprocessing.Process(target=run, name="Run", args=(timeout,))
        p.start()
        time.sleep(10)
        p.terminate()
        p.join()
    else:
        run()

    return found


def checkNpmPkg(pkg):
    '''Check if the given NPM Package is globally installed
    
        Parameters:
            pkg (str) - the name of thhe package to check for
    
    '''
    
    cmd = popen("npm list -g {}".format(pkg))
    return str(cmd.read().replace("â””â”€â”€", "").replace("â””â”€â”¬", "")).split("\n")[1].strip() != "(empty)"


def getNpmV():
    '''Get the installed NPM version
    
        Returns:
        str: NPM version (if found) or None
    
    '''

    try:
        return str(check_output("npm --version", shell=False).decode()).replace('v', '')
    except Exception:
        return None
    

def getJdkV():
    '''Get the installed JDK version
    
        Returns:
        str: JDK version (if found) or None
    
    '''
    try:
        return str(check_output("javac -version", shell=False).decode()).replace('javac ', '')
    except Exception:
        return None
    

def getNodejsV():
    '''Get the installed Nodejs version
    
        Returns:
        str: Nodejs version (if found) or None
    
    '''
    try:
        return str(check_output("node --version", shell=False).decode()).replace('v', '')
    except Exception:
        return None

def getRegEdAttr(attr = "Path"):
    '''Get a specific attribute value from within a registry key
    
        Parameters:
            attr (str) - the attribute of the value to get
            
        Returns:
            str | None
    
    '''
    def _filter_(x):
        if len(x.strip()) == 0:
            return False
        else:
            return True
    try:
        return ' '.join(list(filter(_filter_, str(check_output('reg.exe query "HKEY_LOCAL_MACHINE\SOFTWARE\Android Studio" /v {}'.format(attr)).decode()).split('\n')[2].strip().split(' ')))[2:])
    except Exception:
        return None
    
    
def is_os_64bit():
    '''Check if the current platform architecture is 64 or 32 bit
    
        Return:
        bool
    '''
    return platform.machine().endswith('64')
