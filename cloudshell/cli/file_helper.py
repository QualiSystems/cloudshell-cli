__author__ = 'g8y3e'

# append data to file
def write_data_to_file(file_name, data, type = "w"):
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

def append_data_to_file(file_name, data):
   write_data_to_file(file_name, data, "a")

def read_data_from_file(file_name):
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