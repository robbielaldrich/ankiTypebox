__addon_name__ = "Typebox"
__version__ = "1.0"

from anki.hooks import addHook
from aqt.reviewer import Reviewer

"""
Replaces {{typebox:}} with textarea. See anki/template/template, 
Template.render_unescaped for filter that finds 'fmod_' hooks.
"""
def Typebox(txt, extra, context, tag, fullname):
    return """<textarea id=typebox></textarea>"""

addHook('fmod_typebox', Typebox)

"""
np_revHTML gets entered value from typebox before answer
is shown and sets the typebox post-answer with that value. 
Also enables tab functionality within textareas.
"""
np_revHtml = """
<img src="qrc:/icons/rating.png" id=star class=marked>
<div id=qa></div>
<script>
var ankiPlatform = "desktop";
var typeans;
function _updateQA (q, answerMode, klass) {
    
    // Begin Typebox code -----------
    //get guess from typebox, if exists
    var typed = $("#typebox").val();
    
    //---Default Anki code----
    $("#qa").html(q);
    //------------------------

    
    //Note (inlcuding question) has been rewritten,
    //so if something was entered into typebox in 
    //queston mode, set typebox value to that in 
    //answer mode.
    
    if (typed && answerMode) {
        $("#typebox").val(typed);
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
    // End Typebox code -------------

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
