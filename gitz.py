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
GIT_PUSH = "git push"
GIT_COMMIT = "git commit -m "
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
    sub_dict = {}
    i = 1
    for subdir in os.listdir(script_path + '/' + SUBMODULE_DIR):
        sub_dict[str(i)] = subdir
        i += 1
    return sub_dict

SUBMODULE_DICT = make_submodule_dict()


# Overwrite git clone submodule
def g_clone():
    for subdir in os.listdir(script_path + '/' + SUBMODULE_DIR):
        script(GIT_SUB_PULL + SUBMODULE_DIR + '/' + subdir)
        if not os.path.exists(os.path.realpath(subdir)):
            script(RESET)


# Overwrite git commit
def g_commit(comment):
    # commit changes to each owned submodule
    for subdir in os.listdir(script_path + '/' + SUBMODULE_DIR):
        # check submodule .git file exists or not
        if os.path.exists(os.path.realpath(subdir) + DOT_GIT):
            # excute submodule comit
            script("cd " + os.path.realpath(subdir))
            script(GIT_COMMIT + comment)
            script("cd " + script_path)
    script(IT_COMMIT + comment)


# Overwrite git push
def g_push(): 
    # push changes to each owned submodule
    for subdir in os.listdir(script_path + '/' + SUBMODULE_DIR):
        # check submodule .git file exists or not
        if os.path.exists(os.path.realpath(subdir) + DOT_GIT):
            # excute submodule update
            script("cd " + os.path.realpath(subdir))
            script(GIT_PUSH)
            script("cd " + script_path)
    # push to origin master
    script(GIT_PUSH)
    

# Overwrite git pull
def g_pull():
    # pull zop main project
    script(GIT_PULL)
    # pull each owned zop submodule
    for subdir in os.listdir(script_path + '/' + SUBMODULE_DIR):
        # check submodule folder exists or not
        if os.path.exists(os.path.realpath(subdir) + DOT_GIT):
            # excute submodule update
            script(GIT_SUB_PULL + SUBMODULE_DIR + subdir)
            script("cd " + script_path)


# Overwrite git branch create or switch
def g_branch_co(branch_name):
    _script_branch_co_helper(branch_name)

    selected = input("Choose a submodule, 0 for exit: ")
    while selected != "0":
        if selected in SUBMODULE_DICT.keys():
            script("cd " + script_path + SUBMODULE_DIR + "/" + SUBMODULE_DICT[selected])
            _script_branch_co_helper(branch_name)
            script("cd " + script_path)
        else:
            selected = input("Invalid submodule, choose again: ")

# Helper function for git branch create
def _script_branch_co_helper(branch_name):
    script("git checkout -b " + branch_name)
    script("git push origin " + branch_name + ":" + branch_name)
    script("git branch --set-upstream-to=origin/" + branch_name)


# Overwrite git branch delete
def g_branch_del(branch_name):
    _script_branch_del_helper(branch_name)
    script("rm -rf " + script_path + "/.git/refs/remotes/origin/" + branch_name)
    selected = input("Choose a submodule, 0 for exit: ")
    while selected != "0":
        if selected in SUBMODULE_DICT.keys():
            script("cd " + script_path + SUBMODULE_DIR + "/" + SUBMODULE_DICT[selected])
            _script_branch_del_helper(branch_name)
            script("rm -rf " + script_path + "/.git/modules/src/components/" + SUBMODULE_DICT[selected] + "/refs/remotes/origin/" + branch_name)
        else:
            selected = input("Invalid submodule, choose again: ")

# Helper function for git branch delete
def _script_branch_del_helper(branch_name):
    script("git checkout master")
    script("git branch -D " + branch_name)


parser = argparse.ArgumentParser()
parser.add_argument("-d", "--del_branch", type=str, default='master', help='Branch to be deleted locally')
parser.add_argument("-m", "--mk_branch", type=str, default='master', help='Branch to be created both locally and remotely')
parser.add_argument("-pl", "--pull", help='Pull and Sync current developing branch and submodules together', action = "store_true")
parser.add_argument("-ps", "--push", help='Push current branch to master of submodules and main project', action = "store_true")
parser.add_argument("-cl", "--clone", help='Clone the submodules from the remote repository', action = "store_true")
parser.add_argument("-co", "--commit", type=str, default='commit the changes', help='Commit the changes in submodules and main project')
args = parser.parse_args()



if __name__  == "__main__":
    if args.pull:
        g_pull()
    if args.push:
        g_push()
    if args.clone:
        g_clone()
    if args.commit != "commit the changes":
        g_commit(args.commit)
    else:
        print("Add appropriated commit comments.")
    if args.del_branch != 'master':
        print("Branch to be deleted : "+args.del_branch)
        g_branch_del(args.del_branch)
    else:
        print("Invalid branch name to be deleted. Type -h for help")
    if args.mk_branch != 'master':
        print("Branch to be created : "+args.mk_branch)
        g_branch_co(args.mk_branch)
    else:
        print("Invalid branch name to be created. Type -h for help")
