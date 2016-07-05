notepad_shortcut = '|'
notepad_on_start = 0 #set to 1 for notepad on by default

"""If find problem, email at robbielaldrich@gmail.com"""

__addon_name__ = "Notepad"
__version__ = "1.0"

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
    
    d['q'] += r'''<script>
	    document.querySelector("textarea").addEventListener('keydown',function(e) {
	    	if(e.keyCode === 9) { 
	        	var start = this.selectionStart;
	        	var end = this.selectionEnd;

	        	var target = e.target;
	        	var value = target.value;
	        	target.value = value.substring(0, start)
	                    + "\t" + "\t" + "\t" + "\t"
	                    + value.substring(end);
	        	this.selectionStart = this.selectionEnd = start + 4;
	        	e.preventDefault();
	    	}
		},false);
	</script>'''
    return d

# from anki/collection.py
# _renderQA(data, *args) called by _getQA() in anki/cards.py
origRenderQA = _Collection._renderQA

notepad_bool = notepad_on_start

def toggleNotepad():
	global notepad_bool
	if notepad_bool == 0:
		notepad_bool = 1
		_Collection._renderQA = npRenderQA
	elif notepad_bool == 1:
		notepad_bool = 0
		_Collection._renderQA = origRenderQA
	if mw.state == "overview" or mw.state == "deckBrowser":
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

a = QAction(mw)
a.setText("Toggle Notepad")
a.setShortcut(notepad_shortcut)
mw.form.menuTools.addAction(a)
mw.connect(a, SIGNAL("triggered()"), toggleNotepad)
