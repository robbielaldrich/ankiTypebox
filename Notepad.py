notepad_shortcut = '|'
notepad_on_start = 0 #switch to 1 for notepad by default

"""If find problem, email at robbie9889@gmail.com [this should be at very top]"""


__addon_name__ = "Notepad"
__version__ = "0.0"

# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
# import all of the Qt GUI library
from aqt.qt import *
from anki.hooks import wrap
from aqt.reviewer import Reviewer

"""
class Notepad(object):

	def __init__(self):
		self.notepadOn = notepad_on_start

	def toggleNotepad(self):
		if self.notepadOn:
			self.notepadOn = 0
		else:
			self.notepadOn = 1	

	def npKeyHandler(self, evt, _old):
	    key = unicode(evt.text())
	    card = mw.reviewer.card
	    if key == notepad_shortcut:
	    	toggleNotepad()
	    else:	
	    	return _old(self, evt)

npObj = Notepad()
Reviewer._keyHandler = wrap(Reviewer._keyHandler, npObj.npKeyHandler, "around")
"""

def keyHandler(self, evt, _old):
    key = unicode(evt.text())
    if self.state == "question" and key == notepad_shortcut:
    	card = mw.reviewer.card
    	showInfo(card._getQA(False, False)['q'])
    else: return _old(self, evt)

Reviewer._keyHandler = wrap(Reviewer._keyHandler, keyHandler, "around")

"""
action = QAction("Enable Notepad", mw)
# set it to call function when it's clicked
mw.connect(action, SIGNAL("triggered()"), toggleNotepad)
# and add it to the tools menu
mw.form.menuTools.addAction(action)

mw.reviewer.show = wrap(mw.reviewer.show, deck_namer.overview_title)
"""
