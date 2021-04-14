from distutils.core import setup
import py2exe
parameters = {
    'windows':[
        {
            'script':'main.pyw',
            'icon_resources':[(0,'icon.ico')],
            'dest_base':'VGControl'
        }
    ]
}


setup(**parameters)