import os
import subprocess
import re
from urllib.parse import urlparse

def check_vand(pre,new,after,temp_dir):
  def append_name(diff,ind):
    f = open(os.path.join(temp_dir,ind),'w')
    f.write((diff+"\n"))#.encode('utf-8','strict'))
  append_name(pre,'pre')
  append_name(new,'new')
  append_name(after,'after')
  with open(os.path.join(temp_dir,'out1'),'w') as f_out:  
    res = subprocess.Popen(["combinediff", 
                        os.path.join(temp_dir,'pre'),
                        os.path.join(temp_dir,'new')],stdout=f_out,stderr=subprocess.PIPE)
    res.wait()
  with open(os.path.join(temp_dir,'out2'),'w') as f_out2:  
    res2 = subprocess.Popen(["combinediff", 
                        os.path.join(temp_dir,'out1'),
                        os.path.join(temp_dir,'after')],stdout=f_out2,stderr=subprocess.PIPE)
    res2.wait()
  b = subprocess.Popen(["interdiff", 
                      os.path.join(temp_dir,'pre'),
                      os.path.join(temp_dir,'out2')],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  b.wait()
  (stdoutdata, stderrdata) = b.communicate()
  
  return len(stdoutdata)==0

def countChanges(lines):
  changes = 0
  for i in lines.splitlines(1):
    if i[0] == "!" or i[0] == "-" or i[0] == "+":
      changes +=1
  return changes
def parseChange(lines):
  splits = re.split('^---',lines,flags=re.MULTILINE)
  if len(splits)==2:
    old = splits[0]
    new = splits[1]
  else:
    if len(re.findall("^\+",lines,flags=re.MULTILINE))==0:
      old = lines
      new = ""
    else:
      old = ""
      new = lines
  #oldCount = countChanges(old)
  #newCount = countChanges(new)
  return new,old

## extracted from http://stackoverflow.com/questions/1066933/how-to-extract-top-level-domain-name-tld-from-url
# load tlds, ignore comments and empty lines:
def get_tld_list(fi = "./wikidatasets/effective_tld_names.dat.txt"):
  with open(fi,'r',encoding="utf-8") as tld_file:
    tlds = [line.strip() for line in tld_file if line[0] not in "/\n"]
  return tlds

def get_domain(url, tlds):
    url_elements = urlparse(url)[1].split('.')
    # url_elements = ["abcde","co","uk"]

    for i in range(-len(url_elements), 0):
        last_i_elements = url_elements[i:]
        #    i=-3: ["abcde","co","uk"]
        #    i=-2: ["co","uk"]
        #    i=-1: ["uk"] etc

        candidate = ".".join(last_i_elements) # abcde.co.uk, co.uk, uk
        wildcard_candidate = ".".join(["*"] + last_i_elements[1:]) # *.co.uk, *.uk, *
        exception_candidate = "!" + candidate

        # match tlds: 
        if (exception_candidate in tlds):
            return ".".join(url_elements[i:]) 
        if (candidate in tlds or wildcard_candidate in tlds):
            return ".".join(url_elements[i-1:])
            # returns "abcde.co.uk"

    raise ValueError("Domain not in global list of TLDs")
