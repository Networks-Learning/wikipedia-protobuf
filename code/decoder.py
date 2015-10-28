from code import protoStream_pb2
import fnmatch
import os

import sys
def _VarintDecoder(mask):
    '''Like _VarintDecoder() but decodes signed values.'''

    local_ord = ord
    def DecodeVarint(buffer, pos):
        result = 0
        shift = 0
        while 1:
          if sys.version_info >= (3, 0):
            b = buffer[pos]
          else:
            b = local_ord(buffer[pos])
          result |= ((b & 0x7f) << shift)
          pos += 1
          if not (b & 0x80):
              if result > 0x7fffffffffffffff:
                  result -= (1 << 64)
                  result |= ~mask
              else:
                  result &= mask
                  return (result, pos)
          shift += 7
          if shift >= 64:
              ## need to create (and also catch) this exception class...
              raise _DecodeError('Too many bytes when decoding varint.')
    return DecodeVarint

def _VarintEncoder():
  """Return an encoder for a basic varint value."""

  local_chr = chr
  def EncodeVarint(write, value):
      bits = value & 0x7f
      value >>= 7
      while value:
        if sys.version_info >= (3, 0):
          enc = bytes([0x80|bits])
        else:
          enc = local_chr(0x80|bits)
        write(enc)
        bits = value & 0x7f
        value >>= 7
      if sys.version_info >= (3, 0):
        return write(bytes([bits]))
      else:
        return write(local_chr(bits))


  return EncodeVarint

def encodeEntry(write,dat):
  pos = 0
  encodeVarint = _VarintEncoder()
  
  header    = protoStream_pb2.ProtoStreamHeader()
  delimiter = protoStream_pb2.ProtoStreamDelimiter()
  delimiter.delimiter_type = protoStream_pb2.ProtoStreamDelimiter.ENTRY
  
  deli = delimiter.SerializeToString()
  size_deli = len(deli)
  encodeVarint(write,size_deli)
  write(deli)
  for data in dat:
    deli = delimiter.SerializeToString()
    size_deli = len(deli)
    encodeVarint(write,size_deli)
    write(deli)
    data_str = data.SerializeToString()
    encodeVarint(write,len(data_str))
    write(data_str)
  delimiter = protoStream_pb2.ProtoStreamDelimiter()
  delimiter.delimiter_type = protoStream_pb2.ProtoStreamDelimiter.END
  deli = delimiter.SerializeToString()
  size_deli = len(deli)
  encodeVarint(write,size_deli)
  write(deli)

def decodeEntry(content,type_):
  ## get a 64bit varint decoder
  decoder = _VarintDecoder((1<<64) - 1)

  ## get the three types of protobuf messages we expect to see
  #header    = protoStream_pb2.ProtoStreamHeader()
  delimiter = protoStream_pb2.ProtoStreamDelimiter()

  ## get the header
  pos= 0
  next_pos, pos = decoder(content, pos)
  delimiter.ParseFromString(content[pos:pos + next_pos])
  entry = type_()
  while 1:
    try:
      entry = type_()
      pos += next_pos
      next_pos, pos = decoder(content, pos)
      delimiter.ParseFromString(content[pos:pos + next_pos])    
      if delimiter.delimiter_type == delimiter.END:
        break

      pos += next_pos
      next_pos, pos = decoder(content, pos)

      entry.ParseFromString(content[pos:pos + next_pos])
      
      yield entry
    except Exception as inst:
      print("error: "+ str(inst))
      yield None
      break

