from . import common as __base
from . import callableFont as __cFont
from . import ScrolledTable as __cTable
from . import ScrolledText as __cText
from . import statusindicators as __status
from . import variablesframe as __vframe
PosTable = __cTable.PosTable
ScrolledWidget = __cTable.ScrolledWidget
ScrolledText = __cText.ScrolledText
LabelledScrolledText = __cText.LabelledScrolledText
Font = __cFont.Font

getroot = __base.getroot
LabelFrame = __base.LabelFrame
GeneralWidget = __base.GeneralWidget
Button = __base.Button
Entry = __base.Entry
Lamp = __base.Lamp
Window = __base.Window
Frame = __base.Frame
StatusIndicators = __status.StatusIndicators
VariablesFrame = __vframe.VariablesFrame
VariablesFrames = __vframe.VariablesFrames

Blank = __base.Blank

KEYWORDS = __base.KEYWORDS

#from win32api import GetSystemMetrics

