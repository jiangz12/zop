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
SUB_PATH = script_path + '/' + SUBMODULE_DIR + '/'
GIT_PULL = "git pull"
GIT_PUSH = "git push"
GIT_ADD_ALL = "git add ."
GIT_COMMIT = "git commit -m "
GIT_SUB_PULL = "git submodule update --init "
RESET = "git reset --h"
DIFF = "git diff --quiet"


def script(cmd): # normally return 0, other means error
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
    for subdir in os.listdir(SUB_PATH):
        script(GIT_SUB_PULL + SUBMODULE_DIR + '/' + subdir)
        if not os.path.exists(SUB_PATH + subdir):
            script(RESET)
        print("***clone " + SUB_PATH + subdir + " done***\n")


# Overwrite git commit
def g_commit(comment):
    # commit changes to each owned submodule
    comment = "'" + comment + "'"
    for subdir in os.listdir(SUB_PATH):
        # check submodule .git file exists or not
        print(os.path.exists(SUB_PATH + subdir + DOT_GIT))
        print(os.system(DIFF))
        if os.path.exists(SUB_PATH + subdir + DOT_GIT) and os.system(DIFF) == 1:
            # excute submodule comit
            os.chdir(SUB_PATH + subdir)
            script(GIT_ADD_ALL)
            script(GIT_COMMIT + comment)
            os.chdir(script_path)
            print("***commit " + SUB_PATH + subdir + " done***\n")
    script(GIT_ADD_ALL)
    script(GIT_COMMIT + comment)
    print("***commit " + script_path + " done***\n")


# Overwrite git push
def g_push(): 
    # push changes to each owned submodule
    for subdir in os.listdir(SUB_PATH):
        # check submodule .git file exists or not
        if os.path.exists(SUB_PATH + subdir + DOT_GIT):
            # excute submodule update
            os.chdir(SUB_PATH + subdir)
            script(GIT_PUSH)
            os.chdir(script_path)
            print("***push " + SUB_PATH + subdir + " done***\n")
    # push to origin master
    script(GIT_PUSH)
    print("***push " + script_path + " done***\n")
    

# Overwrite git pull
def g_pull():
    # pull zop main project
    script(GIT_PULL)
    print("***pull " + script_path + " done***\n")
    # pull each owned zop submodule
    for subdir in os.listdir(SUB_PATH):
        # check submodule folder exists or not
        if os.path.exists(SUB_PATH + subdir + DOT_GIT):
            # excute submodule update
            script(GIT_SUB_PULL + SUBMODULE_DIR + "/" + subdir)
            print(GIT_SUB_PULL + SUBMODULE_DIR + "/" + subdir)
            print("***pull " + SUB_PATH + subdir + " done***\n")


# Overwrite git branch create or switch
def g_branch_co(branch_name):
    _script_branch_co_helper(branch_name)
    print(SUBMODULE_DICT)
    selected = raw_input("Choose a submodule, 0 for exit: ")
    while selected != "0":
        if selected in SUBMODULE_DICT.keys():
            os.chdir(script_path + "/" + SUBMODULE_DIR + "/" + SUBMODULE_DICT[selected])
            _script_branch_co_helper(branch_name)
            os.chdir(script_path)
        else:
            selected = raw_input("Invalid submodule, choose again: ")

# Helper function for git branch create
def _script_branch_co_helper(branch_name):
    script("git checkout -b " + branch_name)
    script("git push origin " + branch_name + ":" + branch_name)
    script("git branch --set-upstream-to=origin/" + branch_name)


# Overwrite git branch delete
def g_branch_del(branch_name):
    _script_branch_del_helper(branch_name)
    script("rm -rf " + script_path + "/.git/refs/remotes/origin/" + branch_name)
    print(SUBMODULE_DICT)
    selected = raw_input("Choose a submodule, 0 for exit: ")
    while selected != "0":
        if selected in SUBMODULE_DICT.keys():
            os.chdir(script_path + "/" + SUBMODULE_DIR + "/" + SUBMODULE_DICT[selected])
            _script_branch_del_helper(branch_name)
            os.chdir(script_path)
            script("rm -rf " + script_path + "/.git/modules/src/components/" + SUBMODULE_DICT[selected] + "/refs/remotes/origin/" + branch_name)
        else:
            selected = raw_input("Invalid submodule, choose again: ")

# Helper function for git branch delete
def _script_branch_del_helper(branch_name):
    script("git checkout master")
    script("git branch -D " + branch_name)


parser = argparse.ArgumentParser()
parser.add_argument("-d", "--del_branch", help='Branch to be deleted locally', action = "store_true")
parser.add_argument("-m", "--mk_branch", help='Branch to be created both locally and remotely', action = "store_true")
parser.add_argument("-pl", "--pull", help='Pull and Sync current developing branch and submodules together', action = "store_true")
parser.add_argument("-ps", "--push", help='Push current branch to master of submodules and main project', action = "store_true")
parser.add_argument("-cl", "--clone", help='Clone the submodules from the remote repository', action = "store_true")
parser.add_argument("-co", "--commit", type=str, default='', help='Commit the changes in submodules and main project')
args = parser.parse_args()



if __name__  == "__main__":
    if args.pull:
        g_pull()
    elif args.push:
        g_push()
    elif args.clone:
        g_clone()
    elif args.commit:
        g_commit(args.commit)
    elif args.del_branch:
        branch = raw_input("Please give a branch name: ")
        if branch != 'master':
            print("Branch to be deleted : " + branch)
            g_branch_del(branch)
        else:
            print("Invalid branch name to be deleted. Type -h for help")
    elif args.mk_branch:
        branch = raw_input("Please give a branch name: ")
        if branch != 'master':
            print("Branch to be created : " + branch)
            g_branch_co(branch)
        else:
            print("Invalid branch name to be created. Type -h for help")
