from openerp.tests.common import TransactionCase


class TestCompleteUi(TransactionCase):
    """
    Test the complete_ui method on the nh.activity.data model
    """

    def setUp(self):
        """
        Set up the tests
        """
        super(TestSubmit, self).setUp()
        self.test_model = self.env['test.activity.data.model']
        activity_id = self.test_model_pool.create_activity(
            {}, {'field1': 'test'})
        self.activity = self.activity_pool.browse(activity_id)

    def test_complete_ui_with_context(self):
        """
        Test complete_ui with passing the active_id in the context
        """
        response = self.test_model_pool\
            .with_content({'active_id': self.activity.id})\
            .complete_ui([self.activity.data_ref.id])
        self.assertEqual(response, {'type': 'ir.actions.act_window_close'})
        self.assertEqual(self.activity.state, 'completed')

    def test_complete_ui_without_context(self):
        """
        Test complete_ui without passing a context
        """
        response = self.test_model_pool\
            .complete_ui([self.activity.data_ref.id])
        self.assertEqual(response, {'type': 'ir.actions.act_window_close'})
        self.assertNotEqual(self.activity.state, 'completed')
