from sys import exit, stderr, stdout

__version__ = "0.1.0"


def version_callback(value: bool):
    if value:
        logo = """     __     _                                 
  /\ \ \___| |_ __ _  ___ ___  __ _           
 /  \/ / _ \ __/ _` |/ __/ _ \/ _` |          
/ /\  /  __/ || (_| | (_|  __/ (_| |          
\_\ \/ \___|\__\__,_|\___\___|\__,_|          
                                              
 __                           __              
/ _\_   _ _ __   ___ _ __    / /  ___   __ _  
\ \| | | | '_ \ / _ \ '__|  / /  / _ \ / _` | 
_\ \ |_| | |_) |  __/ |    / /__| (_) | (_| | 
\__/\__,_| .__/ \___|_|    \____/\___/ \__, | 
         |_|                           |___/  
   ___                          _             
  / _ \___ _ __   ___ _ __ __ _| |_ ___  _ __ 
 / /_\/ _ \ '_ \ / _ \ '__/ _` | __/ _ \| '__|
/ /_\\  __/ | | |  __/ | | (_| | || (_) | |   
\____/\___|_| |_|\___|_|  \__,_|\__\___/|_|   
                                              

"""
        stderr.write(logo)
        stdout.write(__version__)
        exit()
