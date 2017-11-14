from openerp.tests.common import TransactionCase


class TestGetRecursiveCreatedIds(TransactionCase):
    """ Test get_recursive_created_ids() method of nh_activity model """
    
    def setUp(self):
        """ Set up the tests """
        super(TestGetRecursiveCreatedIds, self).setUp()
        self.activity_model = self.env['nh.activity']
        
    def test_includes_activity_id(self):
        """
        Test that get_recursive_created_ids includes the id of the activity
        """
        activity_id = self.activity_model.create(
            {
                'data_model': 'test.activity.data.model'
            }
        )
        created_ids = self.activity_model.get_recursive_created_ids(
            activity_id
        )
        self.assertEquals(activity_id, created_ids[0])

    def test_sorted_by_id_asc(self):
        """
        Test that get_recursive_created_ids returns the activity ids are
        returned in ascending order
        """
        activity_id = self.activity_model.create(
            {
                'data_model': 'test.activity.data.model'
            }
        )
        activity2_id = self.activity_model.create(
            {
                'creator_id': activity_id,
                'data_model': 'test.activity.data.model'
            }
        )
        activity3_id = self.activity_model.create(
            {
                'creator_id': activity2_id,
                'data_model': 'test.activity.data.model'
            }
        )
        rc_ids = self.activity_model.get_recursive_created_ids(activity_id)
        self.assertEqual(
            set(rc_ids), {activity_id, activity2_id, activity3_id})

    def test_offset_ids(self):
        """
        Test that when there are multiple activities that
        get_recursive_created_ids returns the ids offset from the activity id
        (i.e. it doesn't return the ids for activities before it)
        """
        activity_id = self.activity_model.create(
            {
                'data_model': 'test.activity.data.model'
            }
        )
        activity2_id = self.activity_model.create(
            {
                'creator_id': activity_id,
                'data_model': 'test.activity.data.model'
            }
        )
        activity3_id = self.activity_model.create(
            {
                'creator_id': activity2_id,
                'data_model': 'test.activity.data.model'
            }
        )
        rc_ids = self.activity_model.get_recursive_created_ids(activity3_id)
        self.assertEqual(set(rc_ids), {activity3_id})
