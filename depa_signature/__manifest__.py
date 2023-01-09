# -*- coding: utf-8 -*-
{
    'name': "depa_signature",

    'summary': """
        depa signature for sarabun inherit
    """,

    'description': """
        depa signature for sarabun inherit
    """,

    'author': "depa - MIS",
    'website': "https://www.depa.or.th",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Signature',
    'version': '1.3.7',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'web',
        'mail',
        'pfb_saraban',
        'pfb_saraban_addons'
    ],

    # always loaded
    'data': [
        'security/group_saraban.xml',
        'security/ir.model.access.csv',
        # 'security/group_saraban.xml',
        'views/depa_signature_setting_view.xml',
        'views/book_document_views.xml',
        'views/document_main_internal_need_form_inherit_view.xml',
        'views/hr.xml',
        'views/document_filter_view.xml',
        'views/saraban_send_email_views.xml',
        'wizard/make_approval_wizard_view.xml',
        # 'security/group_saraban.xml',
        # 'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}