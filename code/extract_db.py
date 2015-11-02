'''
Created on Mar 1, 2015

@author: btabibian
'''

import google.protobuf
print(google.protobuf.__file__)
import argparse
from mw import xml_dump
import itertools as itool
import difflib
from code import wikipedia_pb2, decoder, buffer_utils
import fnmatch
import os
import subprocess
import hashlib

parser = argparse.ArgumentParser(description='Process wikipedia history and store meta data information.')
parser.add_argument('-i','--input', type=str, required=True,
                   help = 'Input directory.')
parser.add_argument('-o','--output', type=str,
                   help = 'Output directory')
parser.add_argument('-m','--match', type=str, default  = None,
                   help = 'Regular expression to match only some paths, this is useful if you would like to split the process into several parts.')
parser.add_argument('--after', type=str,default = None,
                   help = 'starts parsing files only with names matching after the given pattern, excluding the pattern itself. Note that this only skips one file, if multiple files match only the first is skipped.')
parser.add_argument('--before', type=str,default = None,
                   help = 'ends before the matching path The boundary is exclusing.')
parser.add_argument('--space',type=float, default = 128,
                   help = 'meta data size per file(before zip). The chunksize for each proto file. Note that this is a soft threshold, if a document is large the threshold may not be respected.')
parser.add_argument('--mzip', dest = 'mzip', action = 'store_true', default = False,
                   help = 'zip metadata after processing.')
parser.add_argument('--temp', dest = 'temp', default = None, type = str, help= 'a temp directory to unzip files, the files created ar removed after processing. If not provided the input directory is used.')

def get_diffs(page,w_page):
  def extractdiff(page,first = ""):
     pre = first
     for rev in page:
       yield rev,difflib.context_diff(rev.text.split('\n'),pre.split('\n'))
       pre = rev.text
  before_id = -1
  res = []
  for rev, diff in extractdiff(page):
    w_rev = wikipedia_pb2.WikipediaRevision()
    w_rev.parent_id = page.id
    w_rev.id = rev.id
    w_rev.time_stamp = str(rev.timestamp)
    u_id = str(rev.contributor.id) if rev.contributor.id is not None else ""
    u_text = str(rev.contributor.user_text) if rev.contributor.user_text is not None else ""
    w_rev.contributor =  u_id+":"+u_text
    w_rev.minor = rev.minor
    w_rev.diff = ("\n".join(diff)).encode(encoding='utf_8')
    w_rev.sha1 = rev.sha1
    w_rev.model = rev.model
    w_rev.format = rev.format
    w_rev.beginningofpage = rev.beginningofpage
    w_rev.previous_id = before_id
    w_rev.comment = rev.comment if rev.comment is not None else ""
    before_id = rev.id
    res.append(w_rev)
  return res

def read_file(fi):
  fname = open(fi,'r',encoding="utf-8")
  print('reading %s' % fname)
  dump = xml_dump.Iterator.from_file(fname)
  for p in dump:
    try:
      print("page %s" % p.title)
    except:
      print("page title not printable")
    page = wikipedia_pb2.WikipediaPage()
    page.revisions.extend(get_diffs(p,page))
    page.id = p.id
    page.redirect = "" if p.redirect is None else p.redirect.title
    page.namespace = p.namespace
    page.title = p.title
    print(len(page.SerializeToString()))
    yield page

buff_meta = []
size_meta = 0
curr_file_index = ""
def consumer_metadata(val):
  global buff_meta,size_meta
  global current_file_buf, curr_file_index
  item_ = val[0]
  file_name = val[1]

  if size_meta > args.space*1000000 or ("/".join(curr_file_index.split('/')[0:-1]) != "/".join(file_name.split('/')[0:-1]) and curr_file_index != ""):
    m = hashlib.md5()
    m.update(buff_meta[0].SerializeToString())
    curr_hash = m.hexdigest()
    print('writing meta', os.path.join(args.output,curr_hash))
    writer = open(os.path.join(args.output,curr_hash),'bw')
    decoder.encodeEntry(writer.write,buff_meta)
    writer.close()
    if args.mzip:
      subprocess.call(["7z",'a','-mx9',os.path.join(args.output,curr_hash)+".7z",os.path.join(args.output,curr_hash)])
      os.remove(os.path.join(args.output,curr_hash))
    buff_meta = []
    size_meta = 0
  if curr_file_index != file_name:
    curr_file_index = file_name
  print("%d elements in buffer" % len(buff_meta))
  size_meta += len(item_.SerializeToString())
  buff_meta.append(item_)

def finalize():
  global buff_meta
  if len(buff_meta) > 0:
    print('writing last set of meta')

    m = hashlib.md5()
    m.update(buff_meta[0].SerializeToString())
    curr_hash = m.hexdigest()
    writer = open(os.path.join(args.output,curr_hash),'bw')
    decoder.encodeEntry(writer.write,buff_meta)
    writer.close()
    if args.mzip:
      subprocess.call(["7z",'a','-mx9',os.path.join(args.output,curr_hash)+".7z",os.path.join(args.output,curr_hash)])
      os.remove(os.path.join(args.output,curr_hash))
    buff_meta = []
    size_meta = 0
if __name__ == "__main__":
  args = parser.parse_args()
  print("start")
  production = buffer_utils.extract_files(args.input, read_file, args.match, True, args.after, args.before,args.temp)
  for item in map(consumer_metadata,production):
    pass
  finalize()
