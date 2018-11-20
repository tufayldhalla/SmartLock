from doorlock import DoorLock

if __name__ == '__main__':
    
    debug = input("DEBUG? (y/n)  >>> ")

    lock = DoorLock('D1', debug)
    lock.run()
