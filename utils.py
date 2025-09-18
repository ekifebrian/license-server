import hashlib
import subprocess
from datetime import datetime




def sha256_hex(s: str) -> str:
return hashlib.sha256(s.encode('utf-8')).hexdigest()




def get_windows_hwid():
try:
out = subprocess.check_output("wmic csproduct get uuid", shell=True, stderr=subprocess.DEVNULL)
lines = out.decode(errors='ignore').splitlines()
for line in lines:
v = line.strip()
if v and v.lower() != "uuid":
return v
except Exception:
pass
return None




def utcnow():
return datetime.utcnow()
