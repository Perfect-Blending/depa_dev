# -*- coding: utf-8 -*-
{
    'name': "depa_welfare",

    'summary': """
        For Request Expense Depa's welfare
    """,

    'description': """
        For Request Expense Depa's welfare
    """,

    'author': "depa MIS",
    'website': "https://www.depa.or.th",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.1.2',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'fin_system',
    ],

    # always loaded
    'data': [
        # 'data/approval_state.xml',
        # 'data/approval_workflow.xml',
        'security/security.xml',
        'security/group_welfare.xml',
        'security/ir.model.access.csv',
        'wizards/views/depa_welfare_make_approval_wizard.xml',
        'wizards/views/depa_welfare_make_adjustment_wizard.xml',
        'wizards/views/depa_welfare_draft_fin100_wizard.xml',
        'views/depa_welfare_view.xml',
        # 'views/depa_welfare_old_view.xml',
        'views/depa_welfare_request_view.xml',
        'views/depa_welfare_request_all_view.xml',
        'views/depa_welfare_rounds_view.xml',
        'views/welfare_types_view.xml',
        'views/depa_welfare_hr_view.xml',
        #'views/depa_welfare_hr_wizard.xml',
        'views/depa_welfare_basic_view.xml',
        'views/depa_welfare_basic_difference_view.xml',
        'views/fin_100_view.xml',
        'views/fin_201_view.xml',
        'views/templates.xml',
        'views/analytic_account_view.xml',
        'views/depa_welfare_flow_setting_view.xml',
        'views/depa_welfare_state_setting_view.xml',
        'views/depa_welfare_basic_setting_view.xml',
        'views/user_profile.xml',
        'views/hr_employee_view.xml',
        'views/department_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
