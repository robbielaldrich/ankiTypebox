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

    d['q'] += ("<br/><br/>")
    d['q'] += ("<textarea rows=4 cols=50/>")
    """
    d['q'] += ("<script>")
    d['q'] += ("$(document).delegate('#textbox', 'keydown', function(e){")
    d['q'] += ("var keyCode = e.keyCode || e.which;")
    d['q'] += ("if (keyCode == 9) {")
    d['q'] += ("e.preventDefault();")
    d['q'] += ("var start = $(this).get(0).selectionStart;")
    d['q'] += ("var end = $(this).get(0).selectionEnd;")
    d['q'] += ("$(this).val($(this).val().substring(0, start)+'\t'+ $(this).val().substring(end));")
    d['q'] += ("$(this).get(0).selectionStart = $(this).get(0).selectionEnd = start + 1;} });")
     d['q'] += ("</script>")
    """
    return d

# anki/collection.py
# _renderQA(data, *args) called by _getQA() in anki/cards.py
origRenderQA = _Collection._renderQA

def toggleNotepad():
	global notepad_bool
	if notepad_bool == 0:
		notepad_bool = 1
		_Collection._renderQA = npRenderQA
	elif notepad_bool == 1:
		notepad_bool = 0
		_Collection._renderQA = origRenderQA
	if mw.state == "overview" or mw.state == "deckBrowser":# or mw.state = "overview":
		return
	elif mw.reviewer.state == "question":
		# reset card, pulled from onSave() (aqt/editcurrent.py)
		r = mw.reviewer
		try:
			r.card.load()
		except:
			# card was removed by clayout
			pass
		else:
			r.cardQueue.append(r.card)
		mw.moveToState("review")

#Reviewer._keyHandler = wrap(Reviewer._keyHandler, keyHandler, "around")
def showState():
	showInfo(mw.state)

a = QAction(mw)
a.setText("Toggle Notepad")
a.setShortcut(notepad_shortcut)
mw.form.menuTools.addAction(a)
mw.connect(a, SIGNAL("triggered()"), toggleNotepad)
