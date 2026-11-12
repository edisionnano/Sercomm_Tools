import sys, hashlib, gzip
from Crypto.Cipher import AES

data = open(sys.argv[1], 'rb').read()
words = [data[100 + i * 4:104 + i * 4] for i in range(24)]
blob = b''.join(words[i] if i % 2 == 0 else words[24 - i] for i in range(24))
key = hashlib.md5(blob[:32]).digest() + hashlib.md5(blob[64:96]).digest()
iv = words[8] + words[15] + words[10] + words[13]

ct = data[300:]
pt = AES.new(key, AES.MODE_CBC, iv).decrypt(ct[:len(ct) // 16 * 16])
pad = pt[-1]
if pt[-pad:] == bytes([pad]) * pad:
    pt = pt[:-pad]

open(sys.argv[2], 'wb').write(gzip.decompress(pt))
