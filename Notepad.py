notepad_shortcut = '|' #choose whichever hotkey you like!
notepad_on_start = 0 #set to 1 for notepad on by default

"""
If you encounter a problem, please email robbielaldrich@gmail.com. 
Thanks!
"""

__addon_name__ = "Notepad"
__version__ = "1.0"

from aqt import mw
from aqt.qt import *
from aqt.reviewer import Reviewer

orig_revHtml = Reviewer._revHtml

notepad_bool = 0
if notepad_on_start:
	toggleNotepad()

def toggleNotepad():
	global notepad_bool
	if notepad_bool == 0:
		notepad_bool = 1
		w = str( mw.width() - 45 )
		h = str( mw.height() / 4 )
		if int(w) > 650: w = '650'

		# from aqt/reviewer.py 
		# _showQuestion() and _showAnswer() call _updateQA() in _revHtml
		# answerMode == 0 if showing question, 1 if showing answer
		# q argument in _updateQA() is either question HTML or answer HTML
		np_revHtml = """
<img src="qrc:/icons/rating.png" id=star class=marked>
<div id=qa></div>
<script>
var ankiPlatform = "desktop";
var typeans;
function _updateQA (q, answerMode, klass) {
	
	if (!answerMode){
		q += "<br/>";
		q += "<textarea id=qNotepad style='width:""" + w + """px;height:""" + h + """px;position:relative;'/>";
	}
    var typed = $("#qNotepad").val();
    if (answerMode && typed) {
    	// if card is not a cloze, should line break
    	if (q.search('cloze') == -1){
    	    q += "<br/><br/>";
    	}
    	q += "<textarea id=aNotepad style='width:""" + w + """px;height:""" + h + """px;position:relative;'px/>";
    }

    $("#qa").html(q);

    if (answerMode && typed) {
        $("#aNotepad").val(typed);
    }

    // allow tabbing within textarea 
    $("textarea").keydown(function(e) {
	    if(e.keyCode === 9) {
	        var start = this.selectionStart;
	        var end = this.selectionEnd;
	        var $this = $(this);
	        var value = $this.val();
	        $this.val(value.substring(0, start)
	                    + "\t" + "\t" + "\t" + "\t"
	                    + value.substring(end));
	        this.selectionStart = this.selectionEnd = start + 4;
	        e.preventDefault();
	    }
	});

    typeans = document.getElementById("typeans");
    if (typeans) {
        typeans.focus();
    }

    if (answerMode) {
        var e = $("#answer");
        if (e[0]) { e[0].scrollIntoView(); }
    } else {
        window.scrollTo(0, 0);
    }
    if (klass) {
        document.body.className = klass;
    }
    // don't allow drags of images, which cause them to be deleted
    $("img").attr("draggable", false);
};

function _toggleStar (show) {
    if (show) {
        $(".marked").show();
    } else {
        $(".marked").hide();
    }
}

function _getTypedText () {
    if (typeans) {
        py.link("typeans:"+typeans.value);
    }
};
function _typeAnsPress() {
    if (window.event.keyCode === 13) {
        py.link("ansHack");
    }
}
</script>
"""
		Reviewer._revHtml = np_revHtml
	elif notepad_bool == 1:
		notepad_bool = 0
		Reviewer._revHtml = orig_revHtml
	if mw.state == "review" and mw.reviewer.state == "question":
		# reset card; code from onSave() (aqt/editcurrent.py)
		r = mw.reviewer
		try:
			r.card.load()
		except:
			pass
		else:
			r.cardQueue.append(r.card)
		mw.moveToState("review")

a = QAction(mw)
a.setText("Toggle Notepad")
a.setShortcut(notepad_shortcut)
mw.form.menuTools.addAction(a)
mw.connect(a, SIGNAL("triggered()"), toggleNotepad)
