# -*- coding: utf-8 -*-
{
    'name': "depa_tmi",

    'summary': """
        For depa's project tracking and management""",

    'description': """
        For depa's project tracking and management
    """,

    'author': "MIS - depa",
    'website': "https://www.depa.or.th",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0.6',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'fin_system',
    ],

    # always loaded
    'data': [
        'security/depa_tmi_group.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/kpi_master_views.xml',
        'views/budget_master_views.xml',
        'views/kpi_setting_dsm_views.xml',
        'views/kpi_setting_group_views.xml',
        'views/kpi_setting_department_views.xml',
        'views/kpi_setting_pm_views.xml',
        'views/kpi_setting_activity_views.xml',
        'wizards/views/kpi_dsm_make_approval_wizard.xml',
        'wizards/views/kpi_dsm_group_make_approval_wizard.xml',
        'wizards/views/kpi_dsm_department_make_approval_wizard.xml',
        'wizards/views/kpi_dsm_pm_make_approval_wizard.xml',
        'views/hr_department_view.xml',
        'views/source_master_views.xml',
        'views/activity_board_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}