import subprocess
import json

print(r"""
           =============           
       =====================       
     =========================     
    =======     ===     ========   
  ======      =======      ======  
 ======      ==========     ====== 
 =====     =============     ======                  ___       _______  __       __    ______        _______.
=====     ===============     =====                 /   \     |   ____||  |     |  |  /  __  \      /       |
=====     ======   ======      ====                /  ^  \    |  |__   |  |     |  | |  |  |  |    |   (----`
====      ===============      ====               /  /_\  \   |   __|  |  |     |  | |  |  |  |     \   \ 
=====      =============       ====              /  _____  \  |  |____ |  `----.|  | |  `--'  | .----)   |
=====       ===========       =====             /__/     \__\ |_______||_______||__|  \______/  |_______/         
======         ======         =====
 ======                      ===== 
  ======                   ======  
    =======             ========   
     ===========   ===========     
       =====================       
           ==============                             
""")

print("\n \n***************************************** LAUNCHING TOR *****************************************\n")

with open("config.json", "r") as f:
    config = json.load(f)

tor_path = config["tor_path"]

try:
    process = subprocess.Popen(tor_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    for line in process.stdout:
        print(line, end="")

        if "Bootstrapped 100% (done): Done" in line:
            print("\n \n***************************************** TOR LAUNCHED *****************************************\n")
            print("[NOTICE] -- Don't close this window now if you want to use Tor")

except FileNotFoundError:
    print("[ERROR] -- tor executable not found")
except Exception as e:
    print(f"[ERROR] -- There was an error during starting tor.exe : {e}")