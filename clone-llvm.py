#!/usr/bin/env python

from __future__ import print_function

import argparse
import os
import subprocess

class ChangeDir:
    '''Temporarily enter a directory.'''

    def __init__(self, new_dir):
        self.old_dir = os.path.abspath(os.curdir)
        self.new_dir = new_dir

    def __enter__(self):
        print(':: Entering', self.new_dir)
        os.chdir(self.new_dir)

    def __exit__(self, Ty, Val, TB):
        print(':: Changing back to', self.old_dir)
        os.chdir(self.old_dir)

def shell(cmd, verbose=False):
    print(':: Executing', cmd)
    return subprocess.check_output(cmd, stderr=subprocess.PIPE, shell=True)

def clone(project_name, username):
    # If the checkout exists, bail.
    if os.access(project_name, os.F_OK):
        return

    svn_name = {'clang': 'cfe'}.get(project_name, project_name)
    git_url = 'http://llvm.org/git/{0}.git'.format(project_name)
    svn_url = 'https://llvm.org/svn/llvm-project/{0}/trunk'.format(svn_name)
    shell('git clone {0}'.format(git_url))

    if not username:
        return

    with ChangeDir(project_name) as cd:
        shell('git svn init {0} --username {1}'.format(svn_url, username))
        shell('git config svn-remote.svn.fetch :refs/remotes/origin/master')
        shell('git svn rebase -l')

def clone_repos(args):
    if not os.access(args.path, os.F_OK):
        os.makedirs(args.path)

    os.chdir(args.path)

    clone('llvm', args.username)

    with ChangeDir('llvm/tools') as cd:
        if args.clang:
            clone('clang', args.username)
        if args.lldb:
            clone('lldb', args.username)
        if args.lld:
            clone('lld', args.username)
        if args.polly:
            clone('polly', args.username)

    with ChangeDir('llvm/projects') as cd:
        if args.compiler_rt:
            clone('compiler-rt', args.username)
        if args.libcxx:
            clone('libcxx', args.username)
            clone('libcxxabi', args.username)

def configure(args, mode):
    src_dir = os.path.abspath(args.path)
    build_dir = os.path.join(os.path.expanduser("~/src/builds"),
                             os.path.basename(src_dir)) + '-' + mode

    if os.access(build_dir, os.F_OK):
        print("Build directory exists! Bailing.")
        return

    os.makedirs(build_dir)

    cmd = ['xcrun cmake -G Ninja', src_dir]

    use_release = '-DCMAKE_BUILD_TYPE=Release'
    use_asserts = '-DLLVM_ENABLE_ASSERTIONS=On'
    use_modules = '-DLLVM_ENABLE_MODULES=On'
    use_minimal = '-DCLANG_ENABLE_ARCMT=Off ' \
                  '-DCLANG_ENABLE_STATIC_ANALYZER=Off ' \
                  '-DLLVM_TARGETS_TO_BUILD="X86;ARM;AArch64"'

    if mode == "RA":
        cmd.extend([use_release, use_asserts, use_modules, use_minimal])

    with ChangeDir(build_dir) as cd:
        shell(' '.join(cmd))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    parser.add_argument('--username', help='svn username on llvm.org')
    parser.add_argument('--clang', action='store_true', default=False)
    parser.add_argument('--compiler_rt', action='store_true', default=False)
    parser.add_argument('--libcxx', action='store_true', default=False)
    parser.add_argument('--lldb', action='store_true', default=False)
    parser.add_argument('--lld', action='store_true', default=False)
    parser.add_argument('--polly', action='store_true', default=False)
    parser.add_argument('--configure_RA', action='store_true', default=False)
    args = parser.parse_args()

    if args.configure_RA:
        configure(args, "RA")
    else:
        clone_repos(args)
