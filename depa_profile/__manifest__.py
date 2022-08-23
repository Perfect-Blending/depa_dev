# -*- coding: utf-8 -*-
{
    'name': "depa Profile",

    'summary': """
        For inherit hr.employee models
        """,

    'description': """
        For inherit hr.employee models
    """,

    'author': "Krittaphas Wisessing, Ratchadaporn Noonil",
    'website': "http://www.depa.or.th",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'employee',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'hr',
        'depa_hr'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/depa_profile_views.xml',
        'views/depa_group_views.xml'
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
}