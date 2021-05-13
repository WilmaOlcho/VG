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
        'dist_dir':'Z:\\',
        'skip_archive':True
        
    }},
    'data_files':[('.',[
            'amuxConfiguration.json',
            'FlexiSoftVG_in.csv',
            'FlexiSoftVG_out.csv',
            'PneumaticsConfiguration.json',
            'ScoutConfiguration.json',
            'robotConfiguration.json',
            'ServoSettings.json',
            'SICKGMODconfiguration.json',
            #'Programs.json',
            'Troleysettings.json',
            'icon.ico',
            'widgetsettings.json' ])
        ]
}


setup(**parameters)