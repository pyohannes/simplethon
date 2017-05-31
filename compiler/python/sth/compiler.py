###+

import argparse
import os
import shutil
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


def main():
    global verbose

    parser = command_line_parser()
    args = parser.parse_args()
    tmpdir = tempfile.mkdtemp()

    verbose = args.verbose

    try:
        if not args.src_files:
            raise SthCompilerError("No source files given")
    
        sthsrcs = []
        for src_file in args.src_files:
            sthsrcs.append(transpile(src_file, tmpdir))

        if args.transpile_only:
            if len(args.src_files) > 1:
                raise SthCompilerError("Multiple source files given")
            inputf = args.src_files[0]
            output = args.output_file
            if not output:
                output = inputf + '.c'
            print_msg('Copying %s to %s' % (sthsrcs[0], output))
            shutil.copyfile(sthsrcs[0], output)
            sys.exit(0)

    except SthCompilerError as e:
        print('Error: %s' %  e)
        sys.exit(1)
