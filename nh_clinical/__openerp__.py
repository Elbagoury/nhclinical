# -*- encoding: utf-8 -*-
{
    'name': 'NH Clinical Core',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': '',
    'description': """    """,
    'author': 'Neova Health',
    'website': 'http://www.neovahealth.co.uk/',
    'depends': ['nh_activity', 'hr'],
    'data': ['data/data.xml', 
             'views/pos_view.xml',
             'views/location_view.xml',
             'views/patient_view.xml',
             'views/user_view.xml',
             'views/device_view.xml',
             'views/operations_view.xml',
             'views/user_management_view.xml',
             'views/doctor_view.xml',
             'wizard/placement_wizard_view.xml',
             'wizard/responsibility_allocation_wizard.xml',
             'wizard/user_allocation_view.xml',
             'views/menuitem.xml',
             'security/ir.model.access.csv',
             'security/adt/ir.model.access.csv',
             'security/operations/ir.model.access.csv'],
    'demo': ['data/dev_users.xml',
             'data/pos.xml',
             'data/ward_a/locations.xml',
             'data/ward_b/locations.xml',
             'data/ward_c/locations.xml',
             'data/ward_d/locations.xml',
             'data/ward_e/locations.xml',
             'data/users.xml',
             'data/ward_a/users.xml',
             'data/ward_b/users.xml',
             'data/ward_c/users.xml',
             'data/ward_d/users.xml',
             'data/ward_e/users.xml',
             'data/ward_a/demo_patients.xml',
             'data/ward_b/demo_patients.xml',
             'data/ward_c/demo_patients.xml',
             'data/ward_d/demo_patients.xml',
             'data/ward_e/demo_patients.xml',
             'data/ward_a/demo_spells.xml',
             'data/ward_b/demo_spells.xml',
             'data/ward_c/demo_spells.xml',
             'data/ward_d/demo_spells.xml',
             'data/ward_e/demo_spells.xml',
             'data/ward_a/demo_admissions.xml',
             'data/ward_b/demo_admissions.xml',
             'data/ward_c/demo_admissions.xml',
             'data/ward_d/demo_admissions.xml',
             'data/ward_e/demo_admissions.xml',
             'data/ward_a/demo_placements.xml',
             'data/ward_b/demo_placements.xml',
             'data/ward_c/demo_placements.xml',
             'data/ward_d/demo_placements.xml',
             'data/ward_e/demo_placements.xml',
             ],
    'css': [],
    'js': [],
    'qweb': [],
    'images': [],
    'application': True,
    'installable': True,
    'active': False,
}