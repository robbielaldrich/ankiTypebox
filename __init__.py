import html.parser
import re

from aqt.reviewer import Reviewer
from anki.utils import stripHTML


Reviewer.typeboxAnsPat = r"\[\[type:box:(.+?)\]\]"


def typeboxAnsFilter(self, buf: str) -> str:
    if self.state == "question":
        typebox_replaced = self.typeboxAnsQuestionFilter(buf)
    else:
        typebox_replaced = self.typeboxAnsAnswerFilter(buf)
    if typebox_replaced != buf:
        return typebox_replaced

    if self.state == "question":
        return self.typeAnsQuestionFilter(buf)
    return self.typeAnsAnswerFilter(buf)


def typeboxAnsQuestionFilter(self, buf: str) -> str:
    m = re.search(self.typeboxAnsPat, buf)
    if not m:
        return buf
    fld = m.group(1)
    # loop through fields for a match
    for f in self.card.model()["flds"]:
        if f["name"] == fld:
            # get field value and style details
            self.typeCorrect = self.card.note()[f["name"]]
            self.typeFont = f["font"]
            self.typeSize = f["size"]
            break

    if not self.typeCorrect:
        if self.typeCorrect is None:
            warn = _("Type answer: unknown field %s") % fld
            return re.sub(self.typeboxAnsPat, warn, buf)
        # empty field, remove typebox answer pattern
        return re.sub(self.typeboxAnsPat, "", buf)

    return re.sub(
        self.typeboxAnsPat,
        """
<center>
<textarea id=typeans style="font-family: '%s'; font-size: %spx;"></textarea>
</center>
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
    # munge correct value
    parser = html.parser.HTMLParser()
    cor = self.mw.col.media.strip(self.typeCorrect)
    cor = re.sub("(\n|<br ?/?>|</?div>)+", "__newline__", cor)
    cor = stripHTML(cor)
    # ensure we don't chomp multiple whitespace
    cor = cor.replace(" ", "&nbsp;")
    cor = parser.unescape(cor)
    cor = cor.replace("\xa0", " ")
    cor = cor.replace("__newline__", "\n")
    cor = cor.strip()
    given = self.typedAnswer
    # compare with typed answer
    res = self.correct(given, cor, showBad=False)

    # and update the type answer area
    s = """
<pre style="text-align:left; font-family: '%s'; font-size: %spx">%s</pre>""" % (
        self.typeFont,
        self.typeSize,
        res,
    )
    if hadHR:
        # a hack to ensure the q/a separator falls before the answer
        # comparison when user is using {{FrontSide}}
        s = "<hr id=answer>" + s
    return re.sub(self.typeAnsPat, s, buf)


Reviewer.typeAnsFilter = typeboxAnsFilter
Reviewer.typeboxAnsQuestionFilter = typeboxAnsQuestionFilter
Reviewer.typeboxAnsAnswerFilter = typeboxAnsAnswerFilter

