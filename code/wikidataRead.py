from code import wikipedia_pb2, decoder, utils, extractLink
import os
import pickle
import re
from collections import OrderedDict
import numpy as np
from dateutil import parser
import datetime
import logging

def loadFile(fi,count=None,min_count=None):
  data = pickle.load(open(fi,'rb'))
  sites = data['sites']
  dat = np.array([li[:-1] for li in data['data']])
  titles = np.array([li[-1] for li in data['data']])
  #Check if data is consistent
  if (dat.shape[0] - np.logical_or((dat[:,3]-dat[:,2])>0,dat[:,3] == -1).sum()) !=0:
    logging.warning("Invalid data: %d" % (dat.shape[0] - np.logical_or((dat[:,3]-dat[:,2])>0,dat[:,3] == -1).sum()))
    titles = titles[np.logical_or((dat[:,3]-dat[:,2])>0,dat[:,3] == -1)]
    dat = dat[np.logical_or((dat[:,3]-dat[:,2])>0,dat[:,3] == -1),:]
  if count is not None:
    print(count)
    logging.info('end document %d' % (count-1))
    titles = titles[dat[:,0]<count]
    dat = dat[dat[:,0]<count,:]
  if min_count is not None:
    logging.info('start document %d' % (min_count+1))
    titles = titles[dat[:,0]>min_count]
    dat = dat[dat[:,0]>min_count,:]
  k = 0
  ## Removing duplicate
  dat[:,0] = -dat[:,0] -1
  for ti in np.unique(titles):
    d = dat[titles == ti,0][0]
    dat[dat[:,0] == d,0] = k
    k = k+1
  #titles = titles[dat[:,0]>0]
  #dat = dat[dat[:,0]>0,:]
  _sites =  list(sites.keys())[:dat[:,1].max()+1]
  sites_ = [(key,sites[key]) for key in _sites]
  nodes = np.zeros((dat.shape[0],2),dtype = 'int32')
  starts = np.zeros(np.max(dat[:,0])+1,dtype = 'int64')
  survived = np.zeros((dat.shape[0]),dtype = 'bool')
  nodes[:,0] = dat[:,0]
  ind = dat[:,3] == -1
  nodes[:,1] = 0
  times = np.zeros((dat.shape[0],2))
  T = np.zeros((dat.shape[0],1))
  T_ = np.max(dat[:,2:3])
  titles_d = np.zeros(np.max(dat[:,0])+1,dtype = titles.dtype)
  for d in range(np.max(dat[:,0])+1):
    logging.info('reading document %d' % d)
    dat_d = dat[dat[:,0] == d,:]
    times_d = times[dat[:,0] == d,:]
    T_d = T[dat[:,0] == d,:]
    survived[dat[:,0] == d] = dat_d[:,3] == -1
    if dat_d.shape[0] == 0:
     continue
    start_int = np.min(dat_d[:,2])
    titles_d[d] = titles[dat[:,0] == d][0]
    starts[d] = start_int
    start = parser.parse(str(start_int))
    def convert_to_int(val):
      diff = (parser.parse(str(val))-start).total_seconds()/(60*60*24)
      if diff <0:
        raise Exception("Invalid diff %s , %s " % (val,start))
      return diff

    convert = np.vectorize(convert_to_int)
    dat_d[dat_d[:,3]==-1,3] = T_+ 1
    times[dat[:,0] == d,0] = convert(dat_d[:,2])
    times[dat[:,0] == d,1] = convert(dat_d[:,3])
    
    convert = np.vectorize(convert_to_int)
    dat_d[dat_d[:,3]==-1,3] = T_+ 1
    times[dat[:,0] == d,0] = convert(dat_d[:,2])
    times[dat[:,0] == d,1] = convert(dat_d[:,3])

  return {'nodes':nodes,'times':times,'sites':np.reshape(dat[:,1],(dat[:,1].shape[0],1)),'survived':survived},sites_,titles_d,starts
