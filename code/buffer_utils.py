import os
import fnmatch
import subprocess

def extract_files(dir_path, read_file,match=None, return_filename = False, 
                  match_after = None,match_before = None, temp_path = None,error_file='errors.log'):
  count = 0
  files = sorted(filter(lambda f:True if match == None else fnmatch.fnmatch(f,match),os.listdir(dir_path)))
  
  match_after_index = 0
  if match_after is not None:
    for fi in files:
      match_after_index +=1
      if fnmatch.fnmatch(fi,match_after):
        break
  match_before_index = len(files)
  if match_before is not None:
    for fi in files:
      if fnmatch.fnmatch(fi,match_before):
        match_before_index = counter
        break
        

  print("First file: %s \n Last file: %s" % (files[match_after_index],files[match_before_index-1]))
  for f_set in files[match_after_index:match_before_index]:
    complete_path = ""
    type_ = ""
    if fnmatch.fnmatch(os.path.join(dir_path,f_set), '*.7z'):
      print(os.path.join(dir_path,f_set))
      source = (dir_path if temp_path is None else temp_path)
      complete_path = (os.path.join(source , f_set)).replace('.7z','')
      subprocess.call(["7z",'x',os.path.join(dir_path,f_set),'-o%s' % source ])
      type_ = ".7z"
    else:
      complete_path = os.path.join(dir_path,f_set)
    counter = 0
    try:
      for item in read_file(complete_path):
        if return_filename:
          yield (item,complete_path+type_)
        else:
          yield item
        counter += 1
    except:
      fi = open('errors.log',"a")
      fi.write(complete_path+"\n")
    if fnmatch.fnmatch(os.path.join(dir_path,f_set), '*.7z'):
      os.remove(complete_path)