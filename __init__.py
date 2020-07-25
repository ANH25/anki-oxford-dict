import os

from aqt import mw
from aqt.utils import *
from aqt.qt import *
from aqt import gui_hooks
from anki.utils import stripHTML

from .oxford_dict import *

config = mw.addonManager.getConfig(__name__)
addon_dir = os.path.dirname(__file__)
odict = OxfordDict(config['app_id'], config['app_key'])

def populate_fields(editor):

    config = mw.addonManager.getConfig(__name__)
    fields = editor.note.values()
    field_names = editor.note.keys()
    word = stripHTML(fields[editor.currentField])

    invalid_fields = []
    try:
        def_field_i = int(config['def_field'])
    except ValueError:
        invalid_fields.append('def_field')
    try:
        audio_field_i = int(config['audio_field'])
    except:
        invalid_fields.append('audio_field')
    if len(invalid_fields) > 0:
        warning = 'Invalid field number(s):\n'
        for i in invalid_fields:
            warning += f"{i} = {config[i]}\n"
        showWarning(warning)
        return
    if def_field_i < 0 and audio_field_i < 0:
        return

    results = []
    try:
        results = odict.get_word_data(word, config['lang'])['results']
    except Exception as e:
        showWarning(str(e))
        return

    added_audio = []
    prons = []
    def_field = f"{fields[def_field_i]} "

    for res in results:
        lex_entries = res['lexicalEntries']
        for lex_ent in lex_entries:

            if audio_field_i >= 0:
                pronunciations = lex_ent.get('pronunciations', [])
                for pr in pronunciations:
                    if 'audioFile' in pr.keys() and pr['audioFile'] not in added_audio:
                        phonetic_spelling = pr.get('phoneticSpelling', '')
                        prons.append([pr['audioFile'], phonetic_spelling])
                        added_audio.append(pr['audioFile'])
                else:
                    entries = lex_ent.get('entries', [])
                    for ent in entries:
                        pronunciations = ent.get('pronunciations', [])
                        for pr in pronunciations:
                            if 'audioFile' in pr.keys() and pr['audioFile'] not in added_audio:
                                phonetic_spelling = pr.get('phoneticSpelling', '')
                                prons.append([pr['audioFile'], phonetic_spelling])
                                added_audio.append(pr['audioFile'])

            if def_field_i >= 0:
                entries = lex_ent.get('entries', [])
                for ent in entries:
                    senses = ent.get('senses', [])
                    for sense in senses:
                        dfn = sense.get('definitions')
                        if dfn:
                            def_field += f"- {dfn[0]}<br>"
                            subsenses = sense.get('subsenses', [])
                            for subsense in subsenses:
                                dfn = subsense.get('definitions', [''])
                                def_field += f" &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- {dfn[0]}<br>"
                            def_field += "<br>"

    if def_field_i >= 0:
        editor.note.__setitem__(field_names[def_field_i], def_field)

    if audio_field_i >= 0:
        audio_field = f"{fields[audio_field_i]} "
        for pron in prons:
            filename = editor._retrieveURL(pron[0])
            if not filename:
                showWarning(f"Could not download {pron[0]}")
                continue
            audio_field += f"[sound:{filename}] {pron[1]} <br>"
        editor.note.__setitem__(field_names[audio_field_i], audio_field)

    editor.loadNote()
    editor.checkValid()

def add_button(buttons, editor):
    buttons.append(editor.addButton(
        os.path.join(addon_dir, 'icon.ico'),
        "oxford_dict",
        populate_fields,
        tip = "Oxford Dict (Ctrl+Shift+O)",
        keys = "Ctrl+Shift+O"))

gui_hooks.editor_did_init_buttons.append(add_button)
