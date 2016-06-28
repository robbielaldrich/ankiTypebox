# anki/collection.py
# _renderQA(data, *args) called by _getQA() in anki/cards.py
def _renderQA(self, data, qfmt=None, afmt=None):
    "Returns hash of id, question, answer."
    # data is [cid, nid, mid, did, ord, tags, flds]
    # unpack fields and create dict
    flist = splitFields(data[6])
    fields = {}
    model = self.models.get(data[2])
    for (name, (idx, conf)) in self.models.fieldMap(model).items():
        fields[name] = flist[idx]
    fields['Tags'] = data[5].strip()
    fields['Type'] = model['name']
    fields['Deck'] = self.decks.name(data[3])
    fields['Subdeck'] = fields['Deck'].split('::')[-1]
    if model['type'] == MODEL_STD:
        template = model['tmpls'][data[4]]
    else:
        template = model['tmpls'][0]
    fields['Card'] = template['name']
    fields['c%d' % (data[4]+1)] = "1"
    # render q & a
    d = dict(id=data[0])
    qfmt = qfmt or template['qfmt']
    afmt = afmt or template['afmt']
    for (type, format) in (("q", qfmt), ("a", afmt)):
        if type == "q":
            format = re.sub("{{(?!type:)(.*?)cloze:", r"{{\1cq-%d:" % (data[4]+1), format)
            format = format.replace("<%cloze:", "<%%cq:%d:" % (
                data[4]+1))
        else:
            format = re.sub("{{(.*?)cloze:", r"{{\1ca-%d:" % (data[4]+1), format)
            format = format.replace("<%cloze:", "<%%ca:%d:" % (
                data[4]+1))
            fields['FrontSide'] = stripSounds(d['q'])
        fields = runFilter("mungeFields", fields, model, data, self)
        html = anki.template.render(format, fields)
        d[type] = runFilter(
            "mungeQA", html, type, fields, model, data, self)
        # empty cloze?
        if type == 'q' and model['type'] == MODEL_CLOZE:
            if not self.models._availClozeOrds(model, data[6], False):
                d['q'] += ("<p>" + _(
            "Please edit this note and add some cloze deletions. (%s)") % (
            "<a href=%s#cloze>%s</a>" % (HELP_SITE, _("help"))))
    return d

# anki/cards.py
# _getQA(reload, browser) called by q() in anki/cards.py
def _getQA(self, reload=False, browser=False):
        if not self._qa or reload:
            f = self.note(reload); m = self.model(); t = self.template()
            data = [self.id, f.id, m['id'], self.odid or self.did, self.ord,
                    f.stringTags(), f.joinedFields()]
            if browser:
                args = (t.get('bqfmt'), t.get('bafmt'))
            else:
                args = tuple()
            self._qa = self.col._renderQA(data, *args)
        return self._qa

# cards.py
# c.q() called by _showQuestion in anki/reviewer.py 
def q(self, reload=False, browser=False):
        return self.css() + self._getQA(reload, browser)['q']

# anki/reviewer.py
# called in nextCard() in anki/reviewer.py and by 
def _showQuestion(self):
        self._reps += 1
        self.state = "question"
        self.typedAnswer = None
        c = self.card
        # grab the question and play audio
        if c.isEmpty():
            q = _("""\
The front of this card is empty. Please run Tools>Empty Cards.""")
        else:
            q = c.q()
        if self.autoplay(c):
            playFromText(q)
        # render & update bottom
        q = self._mungeQA(q)
        klass = "card card%d" % (c.ord+1)
        self.web.eval("_updateQA(%s, false, '%s');" % (json.dumps(q), klass))
        self._toggleStar()
        if self._bottomReady:
            self._showAnswerButton()
        # if we have a type answer field, focus main web
        if self.typeCorrect:
            self.mw.web.setFocus()
        # user hook
        runHook('showQuestion')

