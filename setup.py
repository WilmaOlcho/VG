from distutils.core import setup
import py2exe
parameters = {
    'console':[
        {
            'script':'main.pyw',
            'icon_resources':[(0,'icon.ico')],
            'dest_base':'VGControl'
        }],
    'options':{'py2exe':{
        'dist_dir':'Z:\\'
    }}
}


setup(**parameters)