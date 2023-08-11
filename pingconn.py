import subprocess

res = subprocess.call(["ping", "google.com", "-c 1", "-W2", "-q"])
print(res)
if res == 0:
   print("Has Internet connectivity")
else:
   print("Not connected")
