# wikipedia-protobuf
This repository processes wikipedia history dataset.

The library depends on [google protobuf](https://github.com/google/protobuf) library. The proto messages are stored in messages library and an already compiled version of these messages are stored in code package. While you don't need to compile them again yo do need to install protobuf python library to use them.

## Main functionalities

The main functionality provided by this library are exposed in three scripts:

### Reading from wikipedia history and converting to proto format.

In order to convert a complete history into proto format you need to call [`extarct_db.py`](code/extract_db.py). An example call would look like this:

```bash
python -m code.extract_db -i PATH/TO/WIKIDATASET/ -o OUTPUT/DIRECTORY
```

Calling help on the script would show something like the following explaining the arguments:

```bash
python -m code.extract_db -h
usage: extract_db.py [-h] -i INPUT [-o OUTPUT] [-m MATCH] [--after AFTER]
                     [--before BEFORE] [--space SPACE] [--mzip] [--temp TEMP]

Process wikipedia history and store meta data information.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input directory.
  -o OUTPUT, --output OUTPUT
                        Output directory
  -m MATCH, --match MATCH
                        Regular expression to match only some paths, this is
                        useful if you would like to split the process into
                        several parts.
  --after AFTER         starts parsing files only with names matching after
                        the given pattern, excluding the pattern itself. Note
                        that this only skips one file, if multiple files match
                        only the first is skipped.
  --before BEFORE       ends before the matching path The boundary is
                        exclusing.
  --space SPACE         meta data size per file(before zip). The chunksize for
                        each proto file. Note that this is a soft threshold,
                        if a document is large the threshold may not be
                        respected.
  --mzip                zip metadata after processing.
  --temp TEMP           a temp directory to unzip files, the files created ar
                        removed after processing. If not provided the input
                        directory is used.

```

## Extracting a subset of documents given an input list

Assuming documents are stored in proto format one can extract a subset od documents given a list of document names by calling [list.py](./code/list.py). Similar to above script this script can be used as follows:

```bash
python -m code.list -i PATH/TO/PROTO/FILES -o OUTPUT/DIRECTORY -l FILENAME/WITH/DOCUMENT/NAMES -s 150 -o ./OUTPUT/FILE --sep '\t' --logging I --column 1
```

This call reads data from input directory and a list. Assumes the list file is a csv file separated with tabs and read document names from column 1(column 0 is first column and default value).

Calling help on this script provides the arguments:

```bash
python -m code.list -h
usage: list.py [-h] -i INPUT -l LIST -o OUTPUT -s SIZE [--logging LOGGING]
               [--logging_dir LOGGING_DIR] [--column COLUMN] [--sep SEP]
               [--has_header]

This scripts extract subset of documents from a list of wikipedia pages

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input directory of wikipedia pages.
  -l LIST, --list LIST  list of wikipedia pages.
  -o OUTPUT, --output OUTPUT
                        output directory
  -s SIZE, --size SIZE  output file sizes
  --logging LOGGING     logging level, can be
                        [W]arning,[E]rror,[D]ebug,[I]nfo,[C]ritical
  --logging_dir LOGGING_DIR
                        path for storing log files
  --column COLUMN       column number, 0 picks the first column
  --sep SEP             separator for csv file
  --has_header          input csv has header

```

## Extracting document statistics

This script demonstrates how the data that is processed using above scripts can be used for other works. Calling [link.py](./code/link.py) read the input data and outputs a dictionary in [pickle]() format containing document index, list of web domains referenced in the dataset, a list of links with time they were inserted and removed(-1 if not removed). This script also needs a file called `effective_tld_names.dat.txt` which contains top level domains. You read more about this [here](http://stackoverflow.com/questions/1066933/how-to-extract-top-level-domain-name-tld-from-url) and get a copy of a possible tld list from [here](https://publicsuffix.org/list/effective_tld_names.dat)

```
python -m code.link -i INPUT/DIRECTORY -o OUTPUT/PICKLE/FILE
```

Calling help on this script returns additional arguments for this script:

```bash
python -m code.link -h
usage: link.py [-h] -i INPUT -o OUTPUT [-m MATCH] [--after AFTER]
               [--before BEFORE] [--ltd_names LTD_NAMES] [--count COUNT]

Process wikipedia data, extract links and life time.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input directory.
  -o OUTPUT, --output OUTPUT
                        Output file
  -m MATCH, --match MATCH
                        Regular expression to match only some paths, this is
                        useful if you would like to split the process into
                        several parts.
  --after AFTER         starts parsing files only with names matching after
                        the given pattern, excluding the pattern itself. Note
                        that this only skips one file, if multiple files match
                        only the first is skipped.
  --before BEFORE       ends before the matching path The boundary is
                        exclusing.
  --ltd_names LTD_NAMES
                        tld_list, this file contains the list of primary
                        domains and is necessary to extract main domains.
  --count COUNT         number of items per file

```
