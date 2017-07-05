#!/usr/bin/env python
### +
import os
import shutil
import subprocess
import sys


CWD = os.path.abspath(os.path.dirname(__file__))
OBJDIR = os.path.join(CWD, 'obj')
DOCDIR = os.path.join(OBJDIR, 'doc')


def _ensure_objdir():
    if not os.path.isdir(DOCDIR):
        os.makedirs(DOCDIR)


def _execute(cmd):
    print(' '.join(cmd))
    ret = subprocess.call(cmd)
    if ret != 0:
        sys.exit(ret)


def make_doc():
    _ensure_objdir()

    src = [ 'python/sth/ast.py',
            'python/sth/typifier.py'
          ]

    rootdoc = 'doc/compiler.tex'

    docs = [ rootdoc,
             'doc/introduction.tex',
             'doc/workflow.tex'
           ]

    rootdoc = os.path.join(CWD, rootdoc)
    src = [ os.path.join(CWD, s) for s in src ]

    olddir = os.getcwd()
    try:
        os.chdir(DOCDIR)
        for d in docs:
            shutil.copyfile(os.path.join(CWD, d), os.path.basename(d))
        for s in src:
            _execute([
                'fetzen', 
                '--out', '%s.tex,docu-latex' % os.path.basename(s),
                '--preprocessor', 'uncomment-#',
                s])
        _execute(['pdflatex', os.path.basename(rootdoc)])

    finally:
        os.chdir(olddir)


def make_clean():
    shutil.rmtree(OBJDIR)


def make_test():
    pythondir = 'python'

    os.environ['PYTHONPATH'] = os.path.abspath(pythondir)

    _execute([ 'py.test' ] + sys.argv[2:])


def print_usage():
    print("ERROR: Usage: make.py doc|clean")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'doc':
            make_doc()
        elif sys.argv[1] == 'clean':
            make_clean()
        elif sys.argv[1] == 'test':
            make_test()
        else:
            print_usage()
            sys.exit(1)
    else:
        print_usage()
        sys.exit(1)
