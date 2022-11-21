# -*- coding: utf-8 -*-
{
    'name': "depa_hr_inherit",

    'summary': """
        For inherit hr employee module
        """,

    'description': """
        For inherit hr employee module
    """,

    'author': "MIS - depa",
    'website': "http://www.depa.or.th",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inherit',
    'version': '1.1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'hr',
        'purchase_requisition',
        'purchase_work_acceptance'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_inherit_views.xml',
        'views/hr_department_inherit_views.xml',
        'views/hr_employee_signature_setting_views.xml',
        'views/hr_job_inherit_views.xml',
        'views/vaccine_setting_views.xml',
        'views/work_acceptance_inherit_views.xml',
        'views/account_approver_sign_views.xml',
        # 'security/ir.model.access.csv',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}