from sys import exit

__version__ = "0.1.0"

def version_callback(value: bool):
    if value:
        print(f"Netacea Super Log Generator Version: {__version__}")
        exit()
