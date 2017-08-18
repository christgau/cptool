from collections import OrderedDict
from io import IOBase

FIELD_SEP = ';'
DEFINITON_TABLE_NAME = 'Definition'


class CPTable:
    def __init__(self, name, fields=[]):
        self.name = name
        self.fields = fields
        self.lines = []

    def add_line(self, fields):
        if not isinstance(fields, list):
            raise ValueError('fields must be a list')

        self.lines.append(fields)

    def get_field(self, line_nr, field):
        if isinstance(field, int):
            return self.lines[line_nr][field]
        else:
            return self.lines[line_nr][self.get_field_index(field)]

    def get_field_index(self, field_name):
        return self.fields.index(str(field_name))


class CPFile:
    def __init__(self, afile=None):
        self.tables = OrderedDict()
        if not isinstance(afile, IOBase) and afile:
            afile = open(str(afile), 'r')

        if afile is not None:
            self.load_from_stream(afile)

    def add_table(self, table):
        self.tables[table.name] = table

    def has_table(self, name):
        return name in self.tables.keys()

    def get_table(self, name, create=False):
        if not self.has_table(name):
            if create:
                self.tables[name] = CPTable(name)
            else:
                return None

        return self.tables[name]

    def delete_table(self, name):
        if self.has_table(name):
            del self.tables[name]

    def save_to_stream(self, stream):
        if not isinstance(stream, IOBase):
            raise ValueError('can only write to stream')

        if len(self.tables) == 0:
            return

        stream.write('[' + DEFINITON_TABLE_NAME + ']\n')
        for name, table in self.tables.items():
            stream.write('{0}={1}\n'.format(name,
                         FIELD_SEP.join(table.fields)))

        for name, table in self.tables.items():
            self.save_table_to_stream(stream, table)

    def save_table_to_stream(self, stream, table):
        stream.write('\n[{0}]\n'.format(table.name))
        for fields in table.lines:
            stream.write('{0}\n'.format(FIELD_SEP.join(fields)))

    def load_from_stream(self, stream):
        if not isinstance(stream, IOBase):
            raise ValueError('can only read from streams')

        current_table = None
        field_definitions = {}

        # load all tables but the Definition table
        while True:
            line = stream.readline()
            if len(line) == 0 or len(line.strip()) == 0:
                if current_table and current_table.name != DEFINITON_TABLE_NAME:
                    self.add_table(current_table)
                if len(line) == 0:
                    break

            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                table_name = line.strip('[]')
                current_table = CPTable(table_name)
            elif len(line) > 0 and current_table:
                if current_table.name != DEFINITON_TABLE_NAME:
                    current_table.add_line(line.split(';'))
                else:
                    (table_name, fields) = line.split('=', 2)
                    field_definitions[table_name] = fields.split(FIELD_SEP)

        # assign loaded fields to tables (Definition table may occur
        # somewhere in the file)
        for table_name, fields in field_definitions.items():
            table = self.get_table(table_name)
            if table:
                table.fields = fields
