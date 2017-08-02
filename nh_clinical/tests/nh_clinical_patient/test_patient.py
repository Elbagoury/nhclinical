# Part of NHClinical. See LICENSE file for full copyright and licensing details
# -*- coding: utf-8 -*-
import logging

from openerp.tests import common

_logger = logging.getLogger(__name__)


class TestClinicalPatient(common.SingleTransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestClinicalPatient, cls).setUpClass()
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.partner_pool = cls.registry('res.partner')

    def test_05_create(self):
        cr, uid = self.cr, self.uid

        patient_id = self.patient_pool.create(
            cr, uid, {'other_identifier': 'TESTHN004', 'given_name': 'John',
                      'family_name': 'Smith', 'middle_names': 'Clarke'})
        patient = self.patient_pool.browse(cr, uid, [patient_id])
        self.assertEquals(patient_id, patient.id)
        self.assertEquals('TESTHN004', patient.other_identifier)

        # test for that a partner is created in res_partner.
        self.assertEquals(patient_id,
                          self.partner_pool.browse(cr, uid, [patient_id]).id)

        # test when 'name' is in vals
        patient_id = self.patient_pool.create(
            cr, uid, {
                'other_identifier': 'TESTHN005',
                'name': 'Smith, John',
                'given_name': 'John',
                'family_name': 'Smith'
            })
        patient = self.patient_pool.browse(cr, uid, [patient_id])
        self.assertEquals('Smith, John', patient.name)

    def test_06_write(self):
        cr, uid = self.cr, self.uid

        patient_id = self.patient_pool.search(
            cr, uid, [['other_identifier', '=', 'TESTHN004']])
        self.assertTrue(self.patient_pool.write(cr, uid, patient_id,
                                                {'title': 'test'}))
        self.assertTrue(self.patient_pool.write(cr, uid, patient_id,
                                                {'family_name': 'testfamily'}))

    def test_07_unlink(self):
        cr, uid = self.cr, self.uid

        patient_id = self.patient_pool.create(
            cr, uid, {'other_identifier': 'TEST_UNLINK', 'given_name': 'John',
                      'family_name': 'Smith', 'middle_names': 'Clarke'})
        self.patient_pool.unlink(cr, uid, [patient_id])
        # unlink sets the field 'active' to False, making it invisible to users
        self.assertFalse(
            self.patient_pool.browse(cr, uid, [patient_id]).active)

    def test_get_not_admitted_patient_ids_gets_patients_no_started_spell(self):
        cr, uid = self.cr, self.uid
        spell_pool = self.registry('nh.clinical.spell')
        patient_id = self.patient_pool.create(
            cr, uid, {'other_identifier': 'TESTHN010', 'given_name': 'John',
                      'family_name': 'Smith', 'middle_names': 'Clarke'})

        patient_ids = self.patient_pool.get_not_admitted_patient_ids(cr, uid)

        self.assertTrue(patient_id in patient_ids)
        spell_ids = spell_pool.search(
            cr, uid, [('patient_id', '=', patient_id)])
        self.assertEqual(len(spell_ids), 0)

    def test_not_admitted_dict_with_key_patient_id_and_value_True(self):
        cr, uid = self.cr, self.uid
        patient_id = self.patient_pool.create(
            cr, uid, {'other_identifier': 'TESTHN011', 'given_name': 'John',
                      'family_name': 'Smith', 'middle_names': 'Clarke'})

        res = self.patient_pool._not_admitted(
            cr, uid, [patient_id], None, None)

        self.assertEqual(res, {patient_id: True})

    def test_not_admitted_search_return_domain_patients_not_admitted(self):
        cr, uid = self.cr, self.uid
        patient_id = self.patient_pool.create(
            cr, uid, {'other_identifier': 'TESTHN012', 'given_name': 'John',
                      'family_name': 'Smith', 'middle_names': 'Clarke'})
        args = [('not_admitted', '=', True)]

        domain = self.patient_pool._not_admitted_search(
            cr, uid, None, None, args)

        self.assertEqual(type(domain), list)
        self.assertTrue(patient_id in domain[0][2])
