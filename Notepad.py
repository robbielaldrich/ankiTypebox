notepad_shortcut = '|'
notepad_on_start = 0 #switch to 1 for notepad by default
notepad_bool = notepad_on_start

"""If find problem, email at robbielaldrich@gmail.com"""

__addon_name__ = "Notepad"
__version__ = "0.0"

# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
# import all of the Qt GUI library
from aqt.qt import *
from anki.hooks import wrap
from anki.collection import _Collection
from aqt.reviewer import Reviewer 

def npRenderQA(self, data, qfmt=None, afmt=None):
    d = origRenderQA(self, data, qfmt, afmt)

    #CUSTOM CODE
    d['q'] += ("<br/><input>")
    return d

# anki/collection.py
# _renderQA(data, *args) called by _getQA() in anki/cards.py
origRenderQA = _Collection._renderQA

def keyHandler(self, evt, _old):
	global notepad_bool
	key = unicode(evt.text())
	if key == notepad_shortcut:
		if notepad_bool == 0:
			notepad_bool = 1
			_Collection._renderQA = npRenderQA
		elif notepad_bool == 1:
			notepad_bool = 0
			_Collection._renderQA = origRenderQA
	else: 
		return _old(self, evt)



Reviewer._keyHandler = wrap(Reviewer._keyHandler, keyHandler, "around")

