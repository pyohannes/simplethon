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

    rootdoc = 'doc/compiler.tex'

    src = [ 'python/sth/parser.py' ]

    rootdoc = os.path.join(CWD, rootdoc)
    src = [ os.path.join(CWD, s) for s in src ]

    olddir = os.getcwd()
    try:
        os.chdir(DOCDIR)
        shutil.copyfile(rootdoc, os.path.basename(rootdoc))
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


def print_usage():
    print("ERROR: Usage: make.py doc|clean")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'doc':
            make_doc()
        elif sys.argv[1] == 'clean':
            make_clean()
        else:
            print_usage()
            sys.exit(1)
    else:
        print_usage()
        sys.exit(1)
