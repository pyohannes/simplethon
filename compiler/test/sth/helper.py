import os
import shutil
import subprocess
import sys
import tempfile


STH_MAIN = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        'sthc.py')

try:
    valgrind_available = (subprocess.call([ 'valgrind', '--version']) == 0)
except: 
    valgrind_available = False


def assert_transpiled_output(inp, out, ret):
    tmpdir = None
    try:
        tmpdir = tempfile.mkdtemp()
        sthfile = os.path.join(tmpdir, 'input.sth')

        with open(sthfile, 'w') as f:
            f.write(inp)

        p = subprocess.Popen([
            sys.executable,
            STH_MAIN,
            '-E',
            sthfile],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pout, perr = p.communicate()

        assert p.returncode == ret
        assert out.strip() == pout.decode('utf-8').strip()
    finally:
        if tmpdir:
            shutil.rmtree(tmpdir)


def assert_compiled_output(inp, out, ret, valgrind=True):
    global valgrind_available
    tmpdir = None
    try:
        tmpdir = tempfile.mkdtemp()
        srcfile = os.path.join(tmpdir, 'input.sth')
        executable = os.path.join(tmpdir, 'executable')

        with open(srcfile, 'w') as f:
            f.write(inp)
    
        compileret = subprocess.call([
            sys.executable,
            STH_MAIN,
            '-o',
            executable,
            srcfile])

        assert compileret == 0

        p = subprocess.Popen(
                [ executable ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        pout, perr = p.communicate()

        assert ret == p.returncode
        assert pout.decode('utf-8') == out

        if valgrind and valgrind_available:
            p = subprocess.Popen(
                    [ 'valgrind', executable ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
            pout, perr = p.communicate()

            assert "All heap blocks were freed -- no leaks are possible" \
                    in perr.decode('utf-8')
    finally:
        if tmpdir:
            shutil.rmtree(tmpdir)

