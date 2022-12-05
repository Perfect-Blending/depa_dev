# Copyright 2020 BiOne Solutions Co., Ltd (https://bione.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'BiOne Base Library',
    'category': 'Generic Modules',
    'summary': 'Library for extension module',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'BiOne',
    'website': 'https://bione.co.th',
    'depends': [
        'l10n_th_thaiodoo_c1',
        'bione_account_accountant',
        'web_responsive',
        'date_range',
        'document_sidebar',
        'report_xlsx',
        'report_xlsx_helper',
        'report_xlsx_helper_demo',
        'excel_import_export',
        'excel_import_export_demo',
        'base_technical_features',
        'base_technical_user',
        'base_user_role',
        'base_user_role_profile',
        'auto_backup',
        'base_suspend_security',
        'base_user_role_history',
        'base_user_locale',
        'base_tier_validation',
        'base_tier_validation_formula',
        'base_location_geonames_import',
        'base_location_thailand',
        'mis_builder',
        'jasper_reports',
        # 'bi_hide_show_menu_app',
        'auditlog',
        'ts_dashboard',
        'crm',
        'project',
        'point_of_sale',
        'note',
        'hr_attendance',
        'hr_recruitment',
        'hr_holidays',
        'maintenance',
        'fleet',
        'hr_payroll',

    ],
    'data': [
        # 'views/bo_ir_seq.xml',
    ],
    'installable': True,
    "active": False,
    "description": """

BiOne Library modules
====================================

Contain libary shared for BiOne modules

Change logs:
------------------------------------

* 2020-01-05(1) BO add running seq

""",
}
