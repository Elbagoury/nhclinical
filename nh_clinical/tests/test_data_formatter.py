# Part of NHClinical. See LICENSE file for full copyright and licensing details
# -*- coding: utf-8 -*-
from openerp.tests import common


class TestPatientDataFormatter(common.TransactionCase):
    """
    Test the formatting of patient's data.

    This formatting is executed while creating / updating patient's data
    and it's particularly useful when accepting data from external sources,
    like importing data from CSV files generated by third party systems.
    """

    def setUp(self):
        super(TestPatientDataFormatter, self).setUp()
        self.patient = self.registry('nh.clinical.patient')

    # Test related to Hospital Number formatting
    def test_formatting_hospital_number_with_whitespaces(self):
        fields = [
            'other_identifier',
        ]
        data = [
            ('HOSP NUMB 007',)
        ]
        self.patient.format_data(fields, data)
        self.assertIn('other_identifier', fields)
        self.assertEqual(data[0][0], 'HOSPNUMB007')

    def test_formatting_hospital_number_with_hyphens(self):
        fields = [
            'other_identifier',
        ]
        data = [
            ('HOSP-NUMB-007',)
        ]
        self.patient.format_data(fields, data)
        self.assertIn('other_identifier', fields)
        self.assertEqual(data[0][0], 'HOSPNUMB007')

    def test_formatting_hospital_number_with_non_alphanumeric_characters(self):
        fields = [
            'other_identifier',
        ]
        data = [
            ('£H-O/S+P_N%U@M#B=0)0(7$',)
        ]
        self.patient.format_data(fields, data)
        self.assertIn('other_identifier', fields)
        self.assertEqual(data[0][0], 'HOSPNUMB007')

    # Test related to NHS Number formatting
    def test_formatting_NHS_number_with_whitespaces(self):
        fields = [
            'patient_identifier',
        ]
        data = [
            ('NHS NUMB 047',)
        ]
        self.patient.format_data(fields, data)
        self.assertIn('patient_identifier', fields)
        self.assertEqual(data[0][0], 'NHSNUMB047')

    def test_formatting_NHS_number_with_hyphens(self):
        fields = [
            'patient_identifier',
        ]
        data = [
            ('NHS-NUMB-047',)
        ]
        self.patient.format_data(fields, data)
        self.assertIn('patient_identifier', fields)
        self.assertEqual(data[0][0], 'NHSNUMB047')

    def test_formatting_NHS_number_with_non_alphanumeric_characters(self):
        fields = [
            'patient_identifier',
        ]
        data = [
            (r'^N_H+S-N=U"!M|~B*0/4£7\&',)
        ]
        self.patient.format_data(fields, data)
        self.assertIn('patient_identifier', fields)
        self.assertEqual(data[0][0], 'NHSNUMB047')

    # Test related to date formatting
    def test_formatting_dob_with_no_time_specified(self):
        fields = [
            'dob',
        ]
        data = [
            ('2013-10-28',)
        ]
        self.patient.format_data(fields, data)
        self.assertIn('dob', fields)
        self.assertEqual(data[0][0], '2013-10-28 00:00:00')

    def test_formatting_dob_with_time(self):
        fields = [
            'dob',
        ]
        data = [
            ('2013-10-28 13:05:09',)
        ]
        self.patient.format_data(fields, data)
        self.assertIn('dob', fields)
        self.assertEqual(data[0][0], '2013-10-28 13:05:09')

    def test_formatting_dob_supplied_as_day_month_year(self):
        fields = [
            'dob',
        ]
        data = [
            ('29-01-2004',)
        ]
        self.patient.format_data(fields, data)
        self.assertIn('dob', fields)
        self.assertEqual(data[0][0], '2004-01-29 00:00:00')

    def test_formatting_dob_supplied_as_month_day_year(self):
        fields = [
            'dob',
        ]
        data = [
            ('01-28-2015',)
        ]
        self.patient.format_data(fields, data)
        self.assertIn('dob', fields)
        self.assertEqual(data[0][0], '2015-01-28 00:00:00')

    def test_formatting_dob_with_year_first_option(self):
        """
        Test formatting a date of birth while passing the 'Year First' option.

        Because the values for day, month and year cannot be misunderstood,
        specifying the 'Year First' option should not have any effect.
        """
        fields = [
            'dob',
        ]
        data = [
            ('05-30-1998',)
        ]
        ctx = {
            'dateformat': 'YMD'
        }
        self.patient.format_data(fields, data, context=ctx)
        self.assertIn('dob', fields)
        self.assertEqual(data[0][0], '1998-05-30 00:00:00')

    def test_formatting_dob_with_day_first_option(self):
        """
        Test formatting a date of birth while passing the 'Day First' option.

        Because the values for day, month and year cannot be misunderstood,
        specifying the 'Day First' option should not have any effect.
        """
        fields = [
            'dob',
        ]
        data = [
            ('04-29-2002',)
        ]
        ctx = {
            'dateformat': 'DMY'
        }
        self.patient.format_data(fields, data, context=ctx)
        self.assertIn('dob', fields)
        self.assertEqual(data[0][0], '2002-04-29 00:00:00')

    def test_formatting_ambiguous_dob_with_no_options(self):
        """
        Test formatting an ambiguous date of birth while passing no options
        for date formatting.
        """
        fields = [
            'dob',
        ]
        data = [
            ('03-07-09',)
        ]
        # If no options are passed to the formatter,
        # even in case of ambiguous date,
        # the input is expected to be read as month-day-year
        self.patient.format_data(fields, data)
        self.assertIn('dob', fields)
        self.assertEqual(data[0][0], '2009-03-07 00:00:00')

    def test_formatting_ambiguous_dob_with_day_first_option(self):
        """
        Test formatting an ambiguous date of birth while passing 'Day First'
        option for date formatting.
        """
        fields = [
            'dob',
        ]
        data = [
            ('03-07-09',)
        ]
        ctx = {
            'dateformat': 'DMY'
        }
        self.patient.format_data(fields, data, context=ctx)
        self.assertIn('dob', fields)
        self.assertEqual(data[0][0], '2009-07-03 00:00:00')

    def test_formatting_ambiguous_dob_with_year_first_option(self):
        """
        Test formatting an ambiguous date of birth while passing 'Year First'
        option for date formatting.
        """
        fields = [
            'dob',
        ]
        data = [
            ('03-07-09',)
        ]
        ctx = {
            'dateformat': 'YMD'
        }
        self.patient.format_data(fields, data, context=ctx)
        self.assertIn('dob', fields)
        self.assertEqual(data[0][0], '2003-07-09 00:00:00')

    # Test related to formatting all fields at once
    def test_formatting_patient_multiple_data_with_no_options_for_date(self):
        """
        Test formatting patient multiple data while passing no options
        for date formatting.
        """
        fields = [
            'other_identifier',
            'patient_identifier',
            'dob',
        ]
        data = [
            ('£H-O/S+P_N%U@M#B=0)0(7$', '^N_H+S-N=U"!M|~B*0/4£7&', '03-07-09',)
        ]
        self.patient.format_data(fields, data)
        self.assertIn('other_identifier', fields)
        self.assertIn('patient_identifier', fields)
        self.assertIn('dob', fields)
        self.assertEqual(data[0][0], 'HOSPNUMB007')
        self.assertEqual(data[0][1], 'NHSNUMB047')
        self.assertEqual(data[0][2], '2009-03-07 00:00:00')

    def test_formatting_patient_multiple_data_with_year_first_option(self):
        """
        Test formatting patient multiple data while passing 'Year First'
        option for date formatting.
        """
        fields = [
            'other_identifier',
            'patient_identifier',
            'dob',
        ]
        data = [
            ('£H-O/S+P_N%U@M#B=0)0(7$', '^N_H+S-N=U"!M|~B*0/4£7&', '03-07-09',)
        ]
        ctx = {
            'dateformat': 'YMD'
        }
        self.patient.format_data(fields, data, context=ctx)
        self.assertIn('other_identifier', fields)
        self.assertIn('patient_identifier', fields)
        self.assertIn('dob', fields)
        self.assertEqual(data[0][0], 'HOSPNUMB007')
        self.assertEqual(data[0][1], 'NHSNUMB047')
        self.assertEqual(data[0][2], '2003-07-09 00:00:00')

    def test_formatting_patient_multiple_data_with_day_first_option(self):
        """
        Test formatting patient multiple data while passing 'Day First'
        option for date formatting.
        """
        fields = [
            'other_identifier',
            'patient_identifier',
            'dob',
        ]
        data = [
            ('£H-O/S+P_N%U@M#B=0)0(7$', '^N_H+S-N=U"!M|~B*0/4£7&', '03-07-09',)
        ]
        ctx = {
            'dateformat': 'DMY'
        }
        self.patient.format_data(fields, data, context=ctx)
        self.assertIn('other_identifier', fields)
        self.assertIn('patient_identifier', fields)
        self.assertIn('dob', fields)
        self.assertEqual(data[0][0], 'HOSPNUMB007')
        self.assertEqual(data[0][1], 'NHSNUMB047')
        self.assertEqual(data[0][2], '2009-07-03 00:00:00')