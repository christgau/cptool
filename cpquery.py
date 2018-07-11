#!/usr/bin/env python3
import sys
import argparse

from cp import CPFile


def is_integer_string(s):
    return any(i.isdigit() for i in s)


def is_condition_match(table, line_no, field, condition):
    if is_integer_string(condition):
        return line_no + 1 == int(condition)
    else:
        # nothing more supported at the moment
        return False


parser = argparse.ArgumentParser(
        description='select values from a CP file')

parser.add_argument('expr', nargs=1,
                    help='xpath-like select expression')
parser.add_argument('inputs', nargs='*', help='input files')

args = parser.parse_args(sys.argv[1:])
if len(args.inputs) == 0:
    args.inputs.append(sys.stdin)

select_path = args.expr[0].strip('/')
components = select_path.split('/')
if len(components) != 2:
    raise ValueError('Path must contain two components.')

table_name, field_component = components

# extract condition, if any
condition = None
cond_start = field_component.find('[')
if cond_start != -1:
    cond_end = field_component.find(']', cond_start)
    if cond_end == -1:
        raise ValueError('Undelimited condition in select path')
    condition = field_component[cond_start + 1:cond_end]
    field = field_component[:cond_start]
else:
    field = field_component

# convert field to integer
if is_integer_string(field):
    field = int(field)

for f in args.inputs:
    cp = CPFile(f)
    table = cp.get_table(table_name)
    if table is None:
        continue

    for line_no in range(len(table.lines)):
        if condition is None or is_condition_match(
                table, line_no, field, condition):
            value = table.get_field(line_no, field)
            print(value)
