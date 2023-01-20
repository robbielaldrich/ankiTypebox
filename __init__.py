import html
import re
from . import tinycss
from aqt.reviewer import Reviewer
from anki.utils import stripHTML
from aqt import gui_hooks
from aqt import mw

Reviewer.typeboxAnsPat = r"\[\[typebox:(.*?)\]\]"
Reviewer.newline_placeholder = "__typeboxnewline__"

def typeboxAnsFilter(self, buf: str) -> str:
	# replace the typebox pattern for questions, and if question has typebox,
	# 	use custom answer logic
	if self.state == "question":
		self._typebox_note = False
		typebox_replaced = self.typeboxAnsQuestionFilter(buf)

		if typebox_replaced != buf:
			self._typebox_note = True
			return typebox_replaced

		return self.typeAnsQuestionFilter(buf)

	elif hasattr(self, "_typebox_note") and self._typebox_note:
		self._typebox_note = False
		return self.typeboxAnsAnswerFilter(buf)

	return self.typeAnsAnswerFilter(buf)


def _set_font_details_from_card(reviewer, style, selector):
	selector_rules = [r for r in style.rules if hasattr(r, "selector")]
	card_style = next(
		(r for r in selector_rules if "".join([t.value for t in r.selector]) == selector), None)
	if card_style:
		for declaration in card_style.declarations:
			if declaration.name == "font-family":
				reviewer.typeFont = "".join([t.value for t in declaration.value])
			if declaration.name == "font-size":
				reviewer.typeSize = "".join([str(t.value) for t in declaration.value])


def typeboxAnsQuestionFilter(self, buf: str) -> str:
	self.typeCorrect = None
	m = re.search(self.typeboxAnsPat, buf)
	if not m:
		return buf
	fld = m.group(1)
	# loop through fields for a match
	fields = self.card.model()["flds"]
	for f in fields:
		if f["name"] == fld:
			# get field value for correcting
			self.typeCorrect = self.card.note()[f["name"]]
			# get font/font size from field
			self.typeFont = f["font"]
			self.typeSize = f["size"]
			break
	if not self.typeCorrect:
		maybe_answer_field = next((f for f in fields if f == "Back"), fields[-1])
		self.typeFont = maybe_answer_field["font"]
		self.typeSize = maybe_answer_field["size"]

	# ".card" styling should overwrite font/font size, as it does for the rest of the card
	if self.card.model()["css"] and self.card.model()["css"].strip():
		parser = tinycss.make_parser("page3")
		parsed_style = parser.parse_stylesheet(self.card.model()["css"])
		_set_font_details_from_card(self, parsed_style, ".card")
		_set_font_details_from_card(self, parsed_style, ".textbox-input")

	return re.sub(
		self.typeboxAnsPat,
		"""
<center>
<textarea id=typeans class=textbox-input onkeypress="typeboxAns();" style="font-family: '%s'; font-size: %spx;"></textarea>
</center>
<script>
function typeboxAns() {
	if (window.event.keyCode == 13 && window.event.ctrlKey) pycmd("ans");
}
</script>
	"""
		% (self.typeFont, self.typeSize),
		buf,
		)

def typeboxAnsAnswerFilter(self, buf: str) -> str:
	if not self.typeCorrect:
		return re.sub(self.typeboxAnsPat, "", buf)

	origSize = len(buf)
	buf = buf.replace("<hr id=answer>", "")
	hadHR = len(buf) != origSize

	# Compare answers -- replace line markup/chars with newline markers to
	# preserve line breaks during compare.
	# - `compare_answer` strips newlines from `expected`.
	#   - Source: https://github.com/ankitects/anki/blob/ded805b5046e2df849103022747b94ce289bed46/rslib/src/typeanswer.rs#L106

	provided = re.sub(r"(\r\n)", "\n", self.typedAnswer)
	expected = self.mw.col.media.strip(self.typeCorrect)
	expected = re.sub(r"(<div><br>|<br>)", "\n", expected)
	expected = re.sub(r"(<div>)+", "\n", expected)
	expected = re.sub(r"(\r\n)", "\n", expected)
	expected = stripHTML(expected)
	expected = html.unescape(expected)
	expected = expected.replace("\xa0", " ")
	expected = expected.strip()
	# Replace remaining "\n" chars with newline placeholder:
	provided = re.sub(r"\n", self.newline_placeholder, provided)
	expected = re.sub(r"\n", self.newline_placeholder, expected)
	# Anki compare (backend):
	output = self.mw.col.compare_answer(expected, provided)
	# Restore line breaks to comparison result:
	output = output.replace(self.newline_placeholder, "<br>")

	# and update the type answer area
	if self.card.model()["css"] and self.card.model()["css"].strip():
		parser = tinycss.make_parser("page3")
		parsed_style = parser.parse_stylesheet(self.card.model()["css"])
		_set_font_details_from_card(self, parsed_style, ".textbox-output-parent")
		_set_font_details_from_card(self, parsed_style, ".textbox-output")
	font_family = "font-family: '%s';" % self.typeFont if hasattr(self, "typeFont") else ""
	font_size = "font-size: %spx" % self.typeSize if hasattr(self, "typeSize") else ""
	s = """
<div class=textbox-output-parent>
<style>
pre {
   white-space:pre-wrap;
   %s%s 
}
</style>    
<pre class=textbox-output>%s</pre>
</div>
""" % (
		font_family,
		font_size,
		output,
	)
	if hadHR:
		# a hack to ensure the q/a separator falls before the answer
		# comparison when user is using {{FrontSide}}
		s = f"<hr id=answer>{s}"
	return re.sub(self.typeboxAnsPat, s.replace('\\', r'\\'), buf)

def focusTypebox(card):
    """
    Tell UI to autofocus on the typebox when the card has typebox in it.
    Anki does this by checking whether mw.reviewer.typeCorrect is truthy, but
    that doesn't cover cases such as when [[typebox:]] is used by itself
    without an answer field or when the answer field is empty. This function
    fixes that.
    """
    if hasattr(mw.reviewer, "_typebox_note") and mw.reviewer._typebox_note:
        mw.web.setFocus()


gui_hooks.reviewer_did_show_question.append(focusTypebox)
Reviewer.typeAnsFilter = typeboxAnsFilter
Reviewer.typeboxAnsQuestionFilter = typeboxAnsQuestionFilter
Reviewer.typeboxAnsAnswerFilter = typeboxAnsAnswerFilter
