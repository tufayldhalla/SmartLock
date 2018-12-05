# Author: Martin Klamrowski
# Last modified: 5/12/2018

from doorlock import DoorLock

if __name__ == '__main__':
    
    # will use user prompted input instead of Arduino if 'y'
    debug = input("DEBUG? (y/n)  >>> ")

    lock = DoorLock('D1', debug, "n")
    lock.run()
