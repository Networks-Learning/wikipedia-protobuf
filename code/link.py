'''
Created on Mar 1, 2015

@author: btabibian
'''

from code import wikipedia_pb2,decoder,buffer_utils
import fnmatch
import os
import subprocess
import hashlib
import re
import argparse
import pickle
from collections import OrderedDict

parser = argparse.ArgumentParser(description='Process wikipedia data, extract links life time.')
parser.add_argument('-i','--input', type=str, required=True,
                   help = 'Input directory.')
parser.add_argument('-o','--output', type=str, required = True,
                   help = 'Output file')
parser.add_argument('-m','--match', type=str, default  = None,
                   help = 'Regular expression to match only some paths')
parser.add_argument('--after', type=str,default = None,
                   help = 'starts parsing directories with names after given pattern') 
parser.add_argument('--before', type=str,default = None,
                   help = 'ends before the matching directory')
parser.add_argument('--count',type=float, default = 128, 
                   help = 'number of items per file')

def read_file(fi):
  f_ = open(fi, "rb")
  content = f_.read()
  for item in decoder.decodeEntry(content,wikipedia_pb2.WikipediaPage):
    yield item
  f_.close()

def revision_extract_links(revision,reverse):
  new_links = set()
  old_links = set()    
  for segment in revision.diff.split("***************")[1:]:
    new,old = utils.parseChange(segment)
    res_new = re.findall("^[!+-].*(?P<url>https?://[a-zA-Z0-9-\./]+)", new,re.MULTILINE)
    
    if len(res_new) >0:
      for link in res_new:
        new_links.add(link)
    
    res_old = re.findall("^[\!\+\-].*(?P<url>https?://[a-zA-Z0-9-\./]+)", old,re.MULTILINE)
    if len(res_old) > 0:
      for link in res_old:
        old_links.add(link)
  if reverse:
    return (revision.id,int(revision.time_stamp),old_links.difference(new_links),new_links.difference(old_links))
  else:
    return (revision.id,int(revision.time_stamp),new_links.difference(old_links),old_links.difference(new_links))
def detect_reverse_diff(revision_zero):
    segment = revision_zero.diff.split("***************")[1]
    return len(re.findall("^\+",segment,flags=re.MULTILINE))==0

def doc_extract_links(doc):
  rev_diff = detect_reverse_diff(doc.revisions[0])
  links_list = map(lambda d: revision_extract_links(d,rev_diff),doc.revisions)
  open_ = dict()
  t = -1
  for id_, time, new, old in links_list:
    if t> time:
      print('black hole detected, traveling back in time!! now: %d, input: %d' % (t,time)) 
    else:
      t = time
    for o in old:
      if o not in open_:
        raise Exception("old item not found %s" % o)
      start_ = open_[o]['date']
      open_[o]['count'] -= 1 
      if open_[o]['count'] == 0:
        if start_>time:
          print('start later than end! %s, %s' % (str(start_),str(time)))
        yield (o,start_,time,id_,doc.title)
    for n in new:
      if n in open_ and open_[n]['count'] != 0:
        open_[n]['count'] += 1
      else:
        open_[n] = {'count' :1,'date':time}
  for item in open_:
    if open_[item]['count'] > 0:
      yield (item,open_[item]['date'],-1,id_,doc.title)
def get_items(doc_index,sites,link,tld):
  url = link[0]
  try:
    site = utils.get_domain(url,tld)
  except ValueError:
    return None
  except Exception as inst:
    raise inst
  if site in sites:
    sites[site] += 1
  else:
    sites[site] = 1
  return (doc_index,list(sites.keys()).index(site),link[1],link[2],link[3],link[4])

if __name__ == '__main__':
  args = parser.parse_args()
  docs = buffer_utils.extract_files(args.input,read_file, args.match, False, args.after, args.before)
  docs_items = map(doc_extract_links,docs)
  tld = utils.get_tld_list()
  sites = OrderedDict()
  doc_index = 0
  final_items = []
  for items in docs_items:
    final_items.extend([t for t in filter(lambda x: x is not None,map(lambda x:get_items(doc_index,sites,x,tld),items))])
    doc_index +=1
  fi = open(args.output,'wb')
  pickle.dump({'data':final_items,'sites':sites},fi)
  fi.close()
