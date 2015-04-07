from datetime import datetime as dt
import logging

from openerp.tests import common
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF

_logger = logging.getLogger(__name__)

from faker import Faker
fake = Faker()
seed = fake.random_int(min=0, max=9999999)


def next_seed():
    global seed
    seed += 1
    return seed


class test_operations(common.SingleTransactionCase):
    @classmethod
    def setUpClass(cls):
        super(test_operations, cls).setUpClass()
        cr, uid = cls.cr, cls.uid

        cls.users_pool = cls.registry('res.users')
        cls.groups_pool = cls.registry('res.groups')
        cls.partner_pool = cls.registry('res.partner')
        cls.activity_pool = cls.registry('nh.activity')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.pos_pool = cls.registry('nh.clinical.pos')
        cls.spell_pool = cls.registry('nh.clinical.spell')
        # OPERATIONS DATA MODELS
        cls.placement_pool = cls.registry('nh.clinical.patient.placement')
        cls.move_pool = cls.registry('nh.clinical.patient.move')
        cls.swap_pool = cls.registry('nh.clinical.patient.swap_beds')
        cls.follow_pool = cls.registry('nh.clinical.patient.follow')
        cls.unfollow_pool = cls.registry('nh.clinical.patient.unfollow')

        cls.apidemo = cls.registry('nh.clinical.api.demo')

        cls.patient_ids = cls.apidemo.build_unit_test_env1(cr, uid, bed_count=4, patient_count=4)

        cls.wu_id = cls.location_pool.search(cr, uid, [('code', '=', 'U')])[0]
        cls.wt_id = cls.location_pool.search(cr, uid, [('code', '=', 'T')])[0]
        cls.pos_id = cls.location_pool.read(cr, uid, cls.wu_id, ['pos_id'])['pos_id'][0]
        cls.pos_location_id = cls.pos_pool.read(cr, uid, cls.pos_id, ['location_id'])['location_id'][0]

        cls.wmu_id = cls.users_pool.search(cr, uid, [('login', '=', 'WMU')])[0]
        cls.wmt_id = cls.users_pool.search(cr, uid, [('login', '=', 'WMT')])[0]
        cls.nu_id = cls.users_pool.search(cr, uid, [('login', '=', 'NU')])[0]
        cls.nt_id = cls.users_pool.search(cr, uid, [('login', '=', 'NT')])[0]
        cls.adt_id = cls.users_pool.search(cr, uid, [('groups_id.name', 'in', ['NH Clinical ADT Group']), ('pos_id', '=', cls.pos_id)])[0]
        
    def test_Placement_SwapBeds_and_Move(self):
        cr, uid = self.cr, self.uid
        patient_ids = self.patient_ids
        patient_id = fake.random_element(patient_ids)
        patient2_id = fake.random_element(patient_ids)
        while patient2_id == patient_id:
            patient2_id = fake.random_element(patient_ids)
        code = str(fake.random_int(min=1000001, max=9999999))
        spell_data = {
            'patient_id': patient_id,
            'pos_id': self.pos_id,
            'code': code,
            'start_date': dt.now().strftime(DTF)}
        spell2_data = {
            'patient_id': patient2_id,
            'pos_id': self.pos_id,
            'code': str(fake.random_int(min=100001, max=999999)),
            'start_date': dt.now().strftime(DTF)}
        spell_activity_id = self.spell_pool.create_activity(cr, uid, {}, spell_data)
        spell2_activity_id = self.spell_pool.create_activity(cr, uid, {}, spell2_data)
        self.activity_pool.start(cr, uid, spell_activity_id)
        self.activity_pool.start(cr, uid, spell2_activity_id)
        
        # Patient Placement
        placement_data = {
            'suggested_location_id': self.wu_id,
            'patient_id': patient_id
        }
        placement2_data = {
            'suggested_location_id': self.wu_id,
            'patient_id': patient2_id
        }
        location_id = self.location_pool.browse(cr, uid, self.wu_id).child_ids[0].id
        location2_id = self.location_pool.browse(cr, uid, self.wu_id).child_ids[1].id
        placement_activity_id = self.placement_pool.create_activity(cr, uid, {'pos_id': self.pos_id}, placement_data)
        placement2_activity_id = self.placement_pool.create_activity(cr, uid, {'pos_id': self.pos_id}, placement2_data)
        self.activity_pool.submit(cr, self.wmu_id, placement_activity_id, {'location_id': location_id})
        self.activity_pool.submit(cr, self.wmu_id, placement2_activity_id, {'location_id': location2_id})
        check_placement = self.activity_pool.browse(cr, uid, placement_activity_id)
        
        # test placement activity submitted data
        self.assertTrue(check_placement.data_ref.patient_id.id == patient_id, msg="Patient Placement: Patient id was not submitted correctly")
        self.assertTrue(check_placement.data_ref.suggested_location_id.id == self.wu_id, msg="Patient Placement: Suggested location was not submitted correctly")
        self.assertTrue(check_placement.data_ref.location_id.id == location_id, msg="Patient Placement: Location id was not submitted correctly")
        
        # Complete Patient Placement
        self.activity_pool.complete(cr, self.wmu_id, placement_activity_id)
        self.activity_pool.complete(cr, self.wmu_id, placement2_activity_id)
        check_placement = self.activity_pool.browse(cr, uid, placement_activity_id)
        self.assertTrue(check_placement.state == 'completed', msg="Patient Placement not completed successfully")
        self.assertTrue(check_placement.date_terminated, msg="Patient Placement Completed: Date terminated not registered")
        # test spell data
        check_spell = self.activity_pool.browse(cr, uid, spell_activity_id)
        self.assertTrue(check_spell.data_ref.location_id.id == location_id, msg= "Patient Placement Completed: Spell location not registered correctly")
        # test patient data
        check_patient = self.patient_pool.browse(cr, uid, patient_id)
        self.assertTrue(check_patient.current_location_id.id == location_id, msg= "Patient Placement Completed: Patient current location not registered correctly")

        # Swap Beds
        beds_data = {
            'location1_id': location_id,
            'location2_id': location2_id
        }
        swap_activity_id = self.swap_pool.create_activity(cr, uid, {}, beds_data)
        self.activity_pool.submit(cr, uid, swap_activity_id, {})
        check_swap = self.activity_pool.browse(cr, uid, swap_activity_id)

        # test swap activity submitted data
        self.assertTrue(check_swap.data_ref.location1_id.id == location_id, msg="Swap Beds: Location id was not submitted correctly")
        self.assertTrue(check_swap.data_ref.location2_id.id == location2_id, msg="Swap Beds: 2nd Location id was not submitted correctly")

        # Complete Swap Beds
        self.activity_pool.complete(cr, uid, swap_activity_id)
        check_swap = self.activity_pool.browse(cr, uid, swap_activity_id)
        self.assertTrue(check_swap.state == 'completed', msg="Swap Beds not completed successfully")
        self.assertTrue(check_swap.date_terminated, msg="Swap Beds Completed: Date terminated not registered")
        # test spell data
        check_spell = self.activity_pool.browse(cr, uid, spell_activity_id)
        self.assertTrue(check_spell.data_ref.location_id.id == location2_id, msg= "Swap Beds Completed: Spell location not updated correctly")
        check_spell = self.activity_pool.browse(cr, uid, spell2_activity_id)
        self.assertTrue(check_spell.data_ref.location_id.id == location_id, msg= "Swap Beds Completed: 2nd Spell location not updated correctly")
        # test patient data
        check_patient = self.patient_pool.browse(cr, uid, patient_id)
        self.assertTrue(check_patient.current_location_id.id == location2_id, msg= "Swap Beds Completed: Patient current location not updated correctly")
        check_patient = self.patient_pool.browse(cr, uid, patient2_id)
        self.assertTrue(check_patient.current_location_id.id == location_id, msg= "Swap Beds Completed: 2nd Patient current location not updated correctly")

        # Patient Move
        location_id = self.location_pool.browse(cr, uid, self.wt_id).child_ids[0].id
        move_data = {
            'location_id': location_id,
            'patient_id': patient_id
        }
        move_activity_id = self.move_pool.create_activity(cr, uid, {'parent_id': spell_activity_id}, move_data)
        self.activity_pool.submit(cr, uid, move_activity_id, {})
        check_move = self.activity_pool.browse(cr, uid, move_activity_id)
        
        # test move activity submitted data
        self.assertTrue(check_move.data_ref.patient_id.id == patient_id, msg="Patient Move: Patient id was not submitted correctly")
        self.assertTrue(check_move.data_ref.location_id.id == location_id, msg="Patient Move: Location id was not submitted correctly")
        
        # Complete Patient Move
        self.activity_pool.complete(cr, uid, move_activity_id)
        check_move = self.activity_pool.browse(cr, uid, move_activity_id)
        self.assertTrue(check_move.state == 'completed', msg="Patient Move not completed successfully")
        self.assertTrue(check_move.date_terminated, msg="Patient Move Completed: Date terminated not registered")
        # test spell data
        check_spell = self.activity_pool.browse(cr, uid, spell_activity_id)
        self.assertTrue(check_spell.data_ref.location_id.id != location_id, msg= "Patient Move Completed: Spell location unexpectedly updated")
        # test patient data
        check_patient = self.patient_pool.browse(cr, uid, patient_id)
        self.assertTrue(check_patient.current_location_id.id == location_id, msg= "Patient Move Completed: Patient current location not registered correctly")

    def test_patient_following(self):
        cr, uid = self.cr, self.uid
        patient_ids = self.patient_ids
        patient_id = fake.random_element(patient_ids)
        patient2_id = fake.random_element(patient_ids)
        while patient2_id == patient_id:
            patient2_id = fake.random_element(patient_ids)

        # Creating 3 Patient Follow Activities:
        # 1st one to test Patient Follow
        # 2nd one to test open follow activities are cancelled when 'unfollowing' a patient
        # 3rd one to test 2nd case only happens if you created those follow activities
        follow_activity_id = self.follow_pool.create_activity(cr, uid, {'user_id': self.nt_id}, {'patient_ids': [[4, patient_id]]})
        follow_activity_id2 = self.follow_pool.create_activity(cr, uid, {'user_id': self.nt_id}, {'patient_ids': [[6, False, [patient_id, patient2_id]]]})
        follow_activity_id3 = self.follow_pool.create_activity(cr, self.wmu_id, {'user_id': self.nt_id}, {'patient_ids': [[6, False, [patient_id, patient2_id]]]})
        self.assertTrue(follow_activity_id, msg="Patient Follow: Create activity failed")
        self.assertTrue(follow_activity_id2, msg="Patient Follow: Create second activity failed")
        self.assertTrue(follow_activity_id3, msg="Patient Follow: Create second activity failed")

        # Checking System state is OK PRE-COMPLETE the first Follow Activity
        check_follow = self.activity_pool.browse(cr, uid, follow_activity_id)
        self.assertTrue(patient_id in [patient.id for patient in check_follow.data_ref.patient_ids], msg="Patient Follow: Incorrect patient")
        self.assertEqual(check_follow.user_id.id, self.nt_id, msg="Patient Follow: Incorrect user following")
        check_user = self.users_pool.browse(cr, uid, self.nt_id)
        self.assertTrue(patient_id not in [patient.id for patient in check_user.following_ids], msg="Patient Follow: The user is already following that patient")

        # Complete Follow Activity and check System state POST-COMPLETE
        self.activity_pool.complete(cr, uid, follow_activity_id)
        check_user = self.users_pool.browse(cr, uid, self.nt_id)
        self.assertTrue(patient_id in [patient.id for patient in check_user.following_ids], msg="Patient Follow: The user is not following that patient")
        self.assertFalse(patient2_id in [patient.id for patient in check_user.following_ids], msg="Patient Follow: The user should not be following that patient")
        check_patient = self.patient_pool.browse(cr, uid, patient_id)
        check_patient2 = self.patient_pool.browse(cr, uid, patient2_id)
        self.assertTrue(self.nt_id in [user.id for user in check_patient.follower_ids], msg="Patient Follow: The user is not in the patient followers list")
        self.assertFalse(self.nt_id in [user.id for user in check_patient2.follower_ids], msg="Patient Follow: The user should not be in the patient followers list")

        # Create an Unfollow Activity
        unfollow_activity_id = self.unfollow_pool.create_activity(cr, uid, {}, {'patient_ids': [[4, patient_id]]})
        self.assertTrue(follow_activity_id, msg="Patient Unfollow: Create activity failed")

        # Checking System state is OK PRE-COMPLETE the Unfollow Activity
        check_unfollow = self.activity_pool.browse(cr, uid, unfollow_activity_id)
        self.assertTrue(patient_id in [patient.id for patient in check_unfollow.data_ref.patient_ids], msg="Patient Unfollow: Incorrect patient")
        check_user = self.users_pool.browse(cr, uid, self.nt_id)
        self.assertTrue(patient_id in [patient.id for patient in check_user.following_ids], msg="Patient Unfollow: The user is not following that patient")

        # Complete Unfollow Activity and check System state POST-COMPLETE
        self.activity_pool.complete(cr, uid, unfollow_activity_id)
        check_user = self.users_pool.browse(cr, uid, self.nt_id)
        self.assertTrue(patient_id not in [patient.id for patient in check_user.following_ids], msg="Patient Unfollow: The user is still following that patient")
        check_patient = self.patient_pool.browse(cr, uid, patient_id)
        self.assertTrue(self.nt_id not in [user.id for user in check_patient.follower_ids], msg="Patient Unfollow: The user still is in the patient followers list")
        check_follow2 = self.activity_pool.browse(cr, uid, follow_activity_id2)
        self.assertEqual(check_follow2.state, 'cancelled', msg="Patient Unfollow: A follow activity containing the unfollowed patient was not cancelled")
        check_follow3 = self.activity_pool.browse(cr, uid, follow_activity_id3)
        self.assertNotEqual(check_follow3.state, 'cancelled', msg="Patient Unfollow: A follow activity created by a different user was cancelled")