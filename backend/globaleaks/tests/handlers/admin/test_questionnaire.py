# -*- coding: utf-8 -*-
import json
import os

from twisted.internet.defer import inlineCallbacks

from globaleaks.handlers.admin import questionnaire
from globaleaks.handlers.admin.context import ContextInstance
from globaleaks.handlers.admin.questionnaire import get_questionnaire
from globaleaks.handlers.admin.field import FieldCollection
from globaleaks.models import Questionnaire
from globaleaks.rest import errors
from globaleaks.tests import helpers
from globaleaks.tests.helpers import get_dummy_fieldoption_list

# special guest:
stuff = u"³²¼½¬¼³²"


class TestQuestionnaireCollection(helpers.TestHandler):
    _handler = questionnaire.QuestionnairesCollection

    def test_get(self):
        handler = self.request(role='admin')
        return handler.get()

    @inlineCallbacks
    def test_post(self):
        self.dummyQuestionnaire = yield get_questionnaire(u'default', 'en')
        self.dummyQuestionnaire['id'] = ''

        for attrname in Questionnaire.unicode_keys:
            self.dummyQuestionnaire[attrname] = stuff

        handler = self.request(self.dummyQuestionnaire, role='admin')
        response = yield handler.post()

        for attrname in Questionnaire.unicode_keys:
            self.assertEqual(response[attrname], stuff)

    @inlineCallbacks
    def test_import_valid_json(self):
        self.test_data_dir = os.path.join(helpers.DATA_DIR, 'questionnaires')
        self.valid_files = [
          'normal-custom-template.json',
          'normal.json',
          'normal-whistleblower-id.json',
        ]

        for fname in self.valid_files:
            p = os.path.join(self.test_data_dir, 'valid', fname)
            with open(p) as f:
                new_q = json.loads(f.read())

            if fname == 'normal-custom-template.json':
                with open(os.path.join(self.test_data_dir, 'valid', 'custom_template.json')) as f:
                    template = json.loads(f.read())
                h = self.request(template, role='admin', handler_cls=FieldCollection)
                yield h.post()

            handler = self.request(new_q, role='admin')
            handler.request.args = {'multilang': ['1']}

            resp_q = yield handler.post()

            self.assertEqual(new_q, resp_q)

class TestQuestionnaireInstance(helpers.TestHandlerWithPopulatedDB):
    _handler = questionnaire.QuestionnaireInstance

    @inlineCallbacks
    def test_put(self):
        for attrname in Questionnaire.unicode_keys:
            self.dummyQuestionnaire[attrname] = stuff

        handler = self.request(self.dummyQuestionnaire, role='admin')
        response = yield handler.put(self.dummyQuestionnaire['id'])

        for attrname in Questionnaire.unicode_keys:
            self.assertEqual(response[attrname], stuff)

    @inlineCallbacks
    def test_delete(self):
        handler = self.request(self.dummyQuestionnaire, role='admin')
        ctx_handler = self.request({}, handler_cls=ContextInstance, role='admin')
        yield ctx_handler.delete(self.dummyContext['id'])
        yield handler.delete(self.dummyQuestionnaire['id'])
        yield self.assertFailure(handler.delete(self.dummyQuestionnaire['id']),
                                 errors.QuestionnaireIdNotFound)

    @inlineCallbacks
    def test_export_import(self):
        handler = self.request(role='admin')

        raw_s = yield handler.get(self.dummyQuestionnaire['id'])
        q = json.loads(raw_s)

        q['name'] = 'testing_quests'

        q['steps'][0]['type'] = 'multichoice'
        q['steps'][0]['options'] = get_dummy_fieldoption_list()

        handler = self.request(q, role='admin',
                               handler_cls=questionnaire.QuestionnairesCollection)
        handler.request.args = {'full': ['1']}
        yield handler.post()
