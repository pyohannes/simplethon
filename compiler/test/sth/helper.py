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


def _compile(inputfile, executable):
    compileret = subprocess.call([
        sys.executable,
        STH_MAIN,
        '-o',
        executable,
        inputfile])
    assert compileret == 0


def _assert_output(executable, output, retcode):
    p = subprocess.Popen(
            [ executable ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    pout, perr = p.communicate()

    print(pout.decode('utf-8'))
    print(perr.decode('utf-8'))

    assert retcode == p.returncode
    assert pout.decode('utf-8') == output


def _assert_valgrind(executable):
    global valgrind_available
    if valgrind_available:
        p = subprocess.Popen(
                [ 'valgrind', executable ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        pout, perr = p.communicate()

        assert "All heap blocks were freed -- no leaks are possible" \
                in perr.decode('utf-8')


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
    tmpdir = None
    try:
        tmpdir = tempfile.mkdtemp()
        srcfile = os.path.join(tmpdir, 'input.sth')
        executable = os.path.join(tmpdir, 'executable')

        with open(srcfile, 'w') as f:
            f.write(inp)

        _compile(srcfile, executable)

        _assert_output(executable, out, ret)

        if valgrind:
            _assert_valgrind(executable)
    finally:
        if tmpdir:
            shutil.rmtree(tmpdir)


def assert_compiled_output_python_compat(inp, valgrind=True):
    tmpdir = None
    try:
        tmpdir = tempfile.mkdtemp()
        srcfile = os.path.join(tmpdir, 'input.sth')
        pyfile = os.path.join(tmpdir, 'input.py')
        executable = os.path.join(tmpdir, 'executable')

        with open(srcfile, 'w') as f:
            f.write(inp)

        _compile(srcfile, executable)

        with open(pyfile, 'a') as f:
            f.write('\nimport sys\nfrom typing import List\ndef free(x): pass\n')
            f.write(inp)
            f.write('\nsys.exit(main(sys.argv))')

        p = subprocess.Popen([ sys.executable, pyfile ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        out, err = p.communicate()

        print(err.decode('utf-8'))

        _assert_output(executable, out.decode('utf-8'), p.returncode)

        if valgrind:
            _assert_valgrind(executable)
    finally:
        if tmpdir:
            shutil.rmtree(tmpdir)
