from multiprocessing import Process, Manager, Lock
from threading import threading
from tkinter import *
from time import sleep
from Estun import Estun



if __name__=="__main__":
    with Manager() as manager:
        shared = manager.dict({
            'Events':{
                'ack':False,
                'Error':False}
            'Error':255*[False],
            'Errors':'',
            'servoModuleFirstAccess':True,
            'configurationError':False,
            'TactWDT':False

        })
        lock = Lock()
        processes = [
            Process(target = Estun.Run(), args=(shared,lock)),
        ]
        for i in range(len(processes)):
            processes[i].start()
        for i in range(len(processes)):
            processes[i].join()