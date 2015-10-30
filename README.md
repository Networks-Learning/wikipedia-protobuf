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
