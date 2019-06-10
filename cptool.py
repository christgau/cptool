#!/usr/bin/env python3
import sys
import argparse

from collections import OrderedDict
from cp import CPFile


def merge_tables(src, dst, f):
    if len(dst.fields) > len(src.fields):
        print("warning: number of fields in table {0} from {1} larger "
              "than in first seen table ({2} vs {3} fields)".format(
               table_name, str(f), len(src.fields), len(dst.fields)),
              file=sys.stderr)

    for number, line in src.lines.items():
        dst.addLine(line)


def table_to_xml(table, output):
    for lineNo in range(len(table.lines)):
        output.write('\t<{0}>\n'.format(table.name))
        for field in table.fields:
            output.write('\t\t<{0}>{1}</{0}>\n'.format(field,
                         table.get_field(lineNo, field)))
        output.write('\t</{0}>\n'.format(table.name))


def to_xml(cp, args, output):
    output.write('<?xml version="1.0" encoding="utf-8"?>\n')
    output.write('<data>\n')

    for table_name in cp.tables.keys():
        table_to_xml(cp.get_table(table_name), output)

    output.write('</data>')


parser = argparse.ArgumentParser(
        description='operate on Swiss Timings CP files')

parser.add_argument('-d', '--delete', help='delete tables (comma seperated)')
parser.add_argument('-m', '--merge', help='merge tables with the same name',
                    action='store_true')
parser.add_argument('-o', '--output', help='change output, default is stdout')
parser.add_argument('-S', '--select', help='select tables for output')
parser.add_argument('-s', '--sort', help='sort tables before output',
                    action='store_true')
parser.add_argument('-x', '--xml', help='output as XML',
                    action='store_true')

parser.add_argument('inputs', nargs='*', help='input files')

args = parser.parse_args(sys.argv[1:])

args.select = args.select.split(',') if args.select else []
args.delete = args.delete.split(',') if args.delete else []

if len(args.inputs) == 0:
    args.inputs.append(sys.stdin)

document = CPFile()

for f in args.inputs:
    input_file = CPFile(f)

    # delete tables not in the select list (if any)
    tables_to_delete = []
    if len(args.select) > 0:
        for table_name in input_file.tables.keys():
            if table_name not in args.select:
                tables_to_delete.append(table_name)

    for table_name in tables_to_delete:
        input_file.delete_table(table_name)

    for table_name in args.delete:
        input_file.delete_table(table_name)

    # append tables to output, merge if neccessary
    for table_name, table in input_file.tables.items():
        if document.has_table(table_name):
            if args.merge:
                dst = document.get_table(table_name)
                src = table
                merge_tables(src, dst, f)
            else:
                print("warning: table {0} seen again in input {1}. Ignored."
                      "Use --merge to merge.".format(table_name, str(f)))
        else:
            document.add_table(table)

if args.sort:
    document.tables = OrderedDict(sorted(document.tables.items(),
                                  key=lambda x: x[0]))

# output
if args.output is None:
    out_stream = sys.stdout
else:
    out_stream = open(args.output, 'w')

if not args.xml:
    document.save_to_stream(out_stream)
else:
    to_xml(document, args, out_stream)
