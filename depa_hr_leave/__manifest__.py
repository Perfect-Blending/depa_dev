# -*- coding: utf-8 -*-
{
    'name': "depa_hr_leave",

    'summary': """
        For depa's human resource management""",

    'description': """
        For depa's human resource management
    """,

    'author': "MIS - depa",
    'website': "https://www.depa.or.th",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Leaving',
    'version': '1.1.2',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'fin_system',
    ],

    # always loaded
    'data': [
        'security/depa_hr_leave_group.xml',
        'security/ir.model.access.csv',
        'views/leave_request_views.xml',
        'views/leave_request_types_views.xml',
        'views/leave_request_public_holidays_views.xml',
        'views/leave_setting_employee_views.xml',
        'views/leave_request_state_views.xml',
        'views/leave_overview_views.xml',
        'views/leave_request_approve_views.xml',
        'views/leave_summary_views.xml',
        'views/leave_summary_approver_views.xml',
        'wizards/views/leave_request_reject_wizard.xml',
        'wizards/views/leave_request_cancel_approved_wizard.xml',
        'data/leave_state.xml',
        'data/leave_types.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}