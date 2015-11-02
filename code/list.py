"""
   This scrip extracts a list of wikipedia pages using a given list
"""

import google.protobuf
import argparse
import os
from code import wikipedia_pb2, decoder
import hashlib
import logging
import pandas as pd
import datetime

parser = argparse.ArgumentParser(description='This scripts extract subset of documents from a list of wikipedia pages.')
parser.add_argument('-i','--input', type=str, required=True,
                   help = 'Input directory of wikipedia pages.')
parser.add_argument('-l','--list', type=str, required=True,
                   help = 'list of wikipedia pages.')
parser.add_argument('-o','--output', type=str,required=True,
                   help = 'output directory')
parser.add_argument('-s','--size', type=float,required=True,
                   help='output file sizes')
parser.add_argument('--logging',default='W',type=str,help = 'logging level, can be [W]arning,[E]rror,[D]ebug,[I]nfo,[C]ritical')
parser.add_argument('--logging_dir',default='./experiments/',help='path for storing log files')
parser.add_argument('--column',default=0,help='column number, 0 picks the first column')
parser.add_argument('--sep',default='\t',help='separator for csv file')
parser.add_argument('--has_header',default=False,action='store_true',help='input csv has header')
def store(buff):
  m = hashlib.md5()
  m.update(buff[0].SerializeToString())
  curr_hash = m.hexdigest()
  writer = open(os.path.join(args.output,curr_hash),'wb')
  decoder.encodeEntry(writer.write,buff)
  writer.close()

if __name__ == "__main__":
  args = parser.parse_args()
  level = logging.WARNING
  if args.logging == 'D':
    level = logging.DEBUG
  if args.logging == 'I':
    level = logging.INFO
  if args.logging == 'W':
    level = logging.WARNING
  if args.logging == 'E':
    level = logging.ERROR
  if args.logging == 'C':
    level = logging.CRITICAL
  logging.basicConfig(filename=os.path.join(args.logging_dir,"wiki_read_"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")+".log"),level=level)

  files = os.listdir(args.input)
  df = pd.read_csv(args.list,sep = args.sep,header = 0 if args.has_header else None)
  print(df.columns[args.column])
  names = [k for k in map(lambda x:x.replace(' ','_'),df[df.columns[args.column]].str.replace('"','').tolist())]
  logging.info('first title %s'  % names[0])
  size_meta = 0
  buff = []
  titles = set()
  for fi in files:
    li = decoder.decodeEntry(open(os.path.join(args.input,fi),'rb').read(),wikipedia_pb2.WikipediaPage)
    for item in li:
      if item.title.replace(' ','_') in names:
        logging.info("current title: %s, current size: %.2f"% (item.title,size_meta/1000000.0))
        titles.add(item.title.replace(' ','_'))
        if size_meta > args.size*1000000:
          logging.info("maximum size reached: %d" % size_meta)
          store(buff)
          buff = []
          size_meta = 0
        size_meta += len(item.SerializeToString())
        buff.append(item)
  if len(set(names).difference(titles)) > 0:
    logging.warning("Following names were not found: %s" % str(set(names).difference(titles)))
  if len(buff)>0:
    store(buff)
    buff = []
    size_meta = 0
