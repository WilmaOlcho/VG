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

