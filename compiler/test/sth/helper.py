import os
import shutil
import subprocess
import sys
import tempfile

SPY_MAIN = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sth.py')


def assert_compiled_output(inp, out, ret):
    tmpdir = None
    try:
        tmpdir = tempfile.mkdtemp()
        srcfile = os.path.join(tmpdir, 'input.sth')
        objfile = os.path.join(tmpdir, 'input.o')
        executable = os.path.join(tmpdir, 'executable')

        with open(srcfile, 'w') as f:
            f.write(inp)
    
        subprocess.call([
            sys.executable,
            SPY_MAIN,
            'compile',
            srcfile,
            '-o',
            objfile])

        subprocess.call([
            sys.executable,
            SPY_MAIN,
            'link',
            '-o', executable,
            objfile])
    
        p = subprocess.Popen(
                [ executable ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        pout, perr = p.communicate()
    finally:
        if tmpdir:
            shutil.rmtree(tmpdir)

    assert ret == p.returncode
    assert pout.decode('utf-8') == out
