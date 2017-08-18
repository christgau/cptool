# cptool

basic manipulation of CP files

# Background

CP files are a (more or less) proprietary file format used by a major vendor of
sport timekeeping technology and result service provider. The file format is a
mix of Windows INI files and CSV files. The sections of the INI file can be
considered as tables. The rows of a section are the rows of the table. Each row
contains a number of columns delimited by semicolons. Sections/tables start
with the name of the table enclosed in square brackets. There is an
(optionally?) blank line between subsequent tables.

A special table named "Definition" should be placed at the beginning of the
file. It contains key-value pairs (separated by "=") with table names as key.
The values are the names of the columns inside that table. Column names are
delimited by semicolons as well.

There is no usage of quotes, thus columns should not contain semicolons.

Usually, CP files are encoded with ISO-8859-1. However, cptool requires them to
be provided in UTF-8.

# Usage

`cptool.py [OPTIONS] [input [input ...]]`

cptool uses the provided input files and consumes them as if they were merged
into a single file. If multiple input files contain tables with the same name
(except for the Definition table), subsequent occurances are ignored and only
the first table is considered for further processing. The `--merge` option can
be used to change this behaviour. If no input is specified, stdin is read.

Without further options, cptool reads the inputs and produces a (nearly)
identical output. The command line options can be used to modify the processing
to some extent, which is basically selection of desired tables.

command line options:

  * `-d TABLES`, `--delete TABLES`

	Delete the TABLES with the given names. They are not considered for further
	processing. Multiple tables can be seperated by commas. By default, no
	tables are deleted.

  * `-m`, `--merge`

	Merge tables that have the same name and occur several times in the inputs.
	The fields of the first seen table(s) are extended by subsequent table(s)
	if their field count is larger than the already known ones.

  * `-o FILE`, `--output FILE`

    Save the output in the given FILE. The default output file is stdout.

  * `-S TABLES`, `--select TABLES`

    Only output the provided TABLES. Multiple tables are delimited by commas. By
	default all encoutered tables are considered for output. The option can be
	considered as the opposite to the `-d|--delete` option.

  * `-s`, `--sort`

	Sort the tables that will be output by their names. By default, tables are
	emitted in order of their occurance. This may be used to beautify the
	output.

  * `-x`, `--xml`

	Store the output as UTF-8 encoded XML. For each table, the XML contains as
	much elements as rows are present in that table. The element is named as the
	table. Each row element contains as many child elements as stated in the
	definition. The child elements are named after the column names. In case,
	there were no field names provided, no elements are output.
