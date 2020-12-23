def BlankFunc(*args, **kwargs): #Blank func to use as default value in function type parameter
    pass

def writeInLambda(variable, value): #Lambdas doesn't support appending
    variable = value
    return None

def dictKeyByVal(dict, byVal): #There is no default method to search for keys in dictionary by value
    keys = []
    items = dict.items()
    for item in items: #item = [key, value]
        if item[1] == byVal: keys.append(item[0])
    return keys

def ErrorEventWrite(lockerinstance, errstring = '', errorlevel = 255):
    lockerinstance[0].lock.acquire()
    if errstring not in lockerinstance[0].shared['Errors']: lockerinstance[0].shared['Errors'] += errstring
    lockerinstance[0].errorlevel[errorlevel] = True
    lockerinstance[0].events['Error'] = True
    lockerinstance[0].lock.release()