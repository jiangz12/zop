#! /usr/bin/env python
import subprocess, os, sys, fileinput, argparse
from os import listdir
import os
# import pathlib
from os.path import isfile, join
from os.path import isfile, join

script_path = os.path.realpath(__file__)
script_path = os.path.dirname(script_path)

# Some Constant Values
PROJECT_CLONE_URL = "ssh://git@10.133.14.52:4040/zop/zop.git"
SUBMODULE_DIR = "src/components"
DOT_GIT = "/.git"
GIT_PULL = "git pull"
GIT_SUB_PULL = "git submodule update --init "
RESET = "git reset --h"


def script(cmd): # normally return 0, other means error
    print (cmd)
    ret = subprocess.call(cmd, shell = True)
    if ret != 0:
        print("Failed: " + cmd)
        sys.exit(1)
    return ret


# Make a constant submodule dictionary based on the subdirectories main project has
def make_submodule_dict():
    sub_dict = {"0": "ALL"}
    i = 1
    for subdir in os.listdir(script_path + '/' + SUBMODULE_DIR):
        sub_dict[str(i)] = subdir
        i += 1
    return sub_dict

SUBMODULE_DICT = make_submodule_dict()


# Overwrite git clone submodule
def g_clone(args):
    #script("git submodule update --init --recursive")
    for subdir in os.listdir(script_path + '/' + SUBMODULE_DIR):
        cmd = GIT_SUB_PULL + SUBMODULE_DIR + '/' + subdir
        script(cmd)
        print(cmd)
        if not os.path.exists(os.path.realpath(subdir)):
            script(RESET)
            print(RESET)



# Overwrite git commit
def g_commit():
    pass

# Overwrite git push
def g_push(): 
    pass

# Overwrite git branch create
def g_branch_co(branch_name):
    script("git checkout -b " + branch_name)
    script("git push origin " + branch_name + ":" + branch_name)
    script("git branch --set-upstream-to=origin/" + branch_name)

# Overwrite git branch delete
def g_branch_del(branch_name):
    script("git checkout master")
    script("git branch -D " + branch_name)
    script("rm -rf " + branch_name + "/.git/refs/remotes/origin/" + branch_name)

# Overwrite git pull
def g_pull():
    # pull zop main project
    script(GIT_PULL)

    # pull each owned zop submodule
    for subdir in os.listdir(script_path + '/' + SUBMODULE_DIR):
        # check submodule folder exists or not
        if os.path.exists(os.path.realpath(subdir) + DOT_GIT):
            # excute submodule update
            cmd = GIT_SUB_PULL + SUBMODULE_DIR + subdir
            script(cmd)
            print(cmd)

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--del_branch", type=str, default='master', help='Branch to be deleted locally')
parser.add_argument("-m", "--mk_branch", type=str, default='master', help='Branch to be created both locally and remotely')
parser.add_argument("-p", "--pull", help='Pull and Sync current developing branch and submodules together', action = "store_true")
parser.add_argument("-c", "--clone", help='Clone the submodules from the remote repository', action = "store_true")
args = parser.parse_args()
if args.del_branch != 'master':
    print("Branch to be deleted : "+args.del_branch)
if args.mk_branch != 'master':
    print("Branch to be created : "+args.mk_branch)


if __name__  == "__main__":
    if args.pull:
        g_pull()
    if args.clone:
        g_clone(args.clone)
    else:
        pass
    if args.del_branch != 'master':
        g_branch_del(args.del_branch)
    else:
        print("Invalid branch name to be deleted. Type -h for help")
    if args.mk_branch != 'master':
        g_branch_co(args.mk_branch)
    else:
        print("Invalid branch name to be created. Type -h for help")
