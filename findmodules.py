from modulefinder import ModuleFinder
from os.path import isfile, dirname, abspath

forbiddenlist = list()
forbiddenlist.extend(dir(__builtins__))

if __name__ == '__main__':
    finder = ModuleFinder()
    selfpath = dirname(abspath(__file__))
    script = ''
    if isfile(selfpath + '\\main.py'):
        script = selfpath + '\\main.py'
    elif isfile(selfpath + '\\main.pyw'):
        script = selfpath + '\\main.pyw'
    if script:
        finder.run_script(script)
    if finder.modules:
        output = sorted(set([name.split('.')[0] for name in list(finder.modules.keys())]))
        if output:
            output = filter(lambda element: element not in forbiddenlist and element[0] != '_', output)
            output = map(lambda element: element + '\n', output)
            with open('modules.txt','w') as vfile:
                vfile.writelines(output)
