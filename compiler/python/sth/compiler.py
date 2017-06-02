###+

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

from sth.ast import parse
from sth.simplifier import simplify
from sth.typifier import typify
from sth.preparator import prepare
from sth.translator import translate, unparse


verbose = False


def print_msg(msg):
    global verbose
    if verbose:
        print(msg)


class SthCompilerError(Exception):
    pass


def command_line_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c',
            action='store_true',
            dest='compile_only',
            default=False,
            help='Compile, but do not link')
    parser.add_argument('-o',
            dest='output_file',
            default=False,
            help='Output file')
    parser.add_argument('-v', '--verbose',
            action='store_true',
            dest='verbose',
            default=False,
            help='Verbose output')
    parser.add_argument('-E',
            action='store_true',
            dest='transpile_only',
            default=False,
            help='Transpile only, but do not compile')
    parser.add_argument('src_files',
            metavar='files',
            type=str,
            nargs='...',
            default=[],
            help='Source file(s)')

    return parser


def transpile(src_file, dst_dir):
    dst_file = src_file + ".c"
    dst_file = dst_file.replace('/', '_').replace('\\', '_')
    dst_file = os.path.join(dst_dir, dst_file)
    print_msg('Transpiling %s to %s' % (src_file, dst_file))
    with open(src_file, 'r') as srcf:
        with open(dst_file, 'w') as dstf:
            srctxt = srcf.read()
            dstf.write(unparse(
                translate(prepare(typify(simplify(parse(srctxt)))))))
    return dst_file


def run_cmd(cmd, msg, err_msg_prefix):
    p = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    print_msg(msg)
    print_msg(cmd)
    out, err = p.communicate()
    out, err = out.decode('utf-8'), err.decode('utf-8')
    if p.returncode != 0:
        raise SthCompilerError("%s: %s" % (err_msg_prefix, err))
    if out.strip():
        print_msg(out.strip())
    if err.strip():
        print_msg(err.strip())


def ccompile(src_file, dst_dir, inc):
    compilestr = 'gcc -Wall -g -I%(inc)s -o %(out)s -c %(src)s'
    args = dict(inc=inc, src=src_file, out='%s.o' % src_file)
    run_cmd(compilestr % args, 
            "Compiling %(src)s to %(out)s" % args,
            "Cannot compile C code:")
    return args['out']


def link(objs, output, lib):
    linkstr = 'gcc -o %(out)s %(objs)s %(lib)s'
    args = dict(out=output, objs=' '.join(objs), lib=lib)
    run_cmd(linkstr % args, 
            "Linking %(objs)s to %(out)s" % args,
            "Cannot link object files:")
    return args['out']


def main(lib, inc):
    global verbose

    parser = command_line_parser()
    args = parser.parse_args()
    tmpdir = tempfile.mkdtemp()

    verbose = args.verbose

    try:
        if not args.src_files:
            raise SthCompilerError("No source files given")
   
        # Transpiling
        csrcs = []
        for src_file in args.src_files:
            csrcs.append(transpile(src_file, tmpdir))

        if args.transpile_only:
            for csrc in csrcs:
                with open(csrc, 'r') as f:
                    print(f.read())
            sys.exit(0)

        # Compiling
        objs = []
        for csrc in csrcs:
            objs.append(ccompile(csrc, tmpdir, inc))

        if args.compile_only:
            for src, obj in zip(args.src_files, objs):
                target = os.path.splitext(src)[0] + '.o'
                print_msg('Copying %s to %s' % (obj, target))
                shutil.copyfile(obj, target)
            sys.exit(0)

        # Linking
        output = args.output_file or 'a.out'
        link(objs, output, lib)
        sys.exit(0)

    except SthCompilerError as e:
        print('Error: %s' %  e)
        sys.exit(1)
