__author__ = 'g8y3e'

# append data to file
def writeDataToFile(file_name, data, type = "w"):
    try:
        file = open(file_name, type)
        file.write(data)
        file.close()
    except Exception, err:
        print "Exception: ", str(err)
        import traceback, sys
        print '-' * 60
        traceback.print_exc(sys.stdout)
        print '-' * 60

def appendDataToFile(file_name, data):
   writeDataToFile(file_name, data, "a")

def readDataFromFile(file_name):
    data = None
    try:
        file = open(file_name, "r")
        data = file.read();
        file.close()
    except Exception, err:
        print "Exception: ", str(err)
        import traceback, sys
        print '-' * 60
        traceback.print_exc(sys.stdout)
        print '-' * 60

    return data