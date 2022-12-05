{
    'name': 'Cheque Management',
    'version': '1.0',
    'category': 'Accounting &amp; Finance',
    'sequence': 14,
    'author': 'wattanadev',
    'company': 'bio',
    'license': 'LGPL-3',
    'website': '',
    'summary': '',
    'depends': ['account', 'mail', 'web'],
    'data': [
        'views/cheque_security.xml',
        'security/ir.model.access.csv',
        'data/demo.xml',
        'report/layout.xml',
        'views/clear_cheque_wizard.xml',
        'views/receive_clear_cheque.xml',
        'views/cheque_master.xml',
        'views/bank_view.xml',
        'views/customer_bank_view.xml',
        'views/receive_cheque_wizard.xml',
        'views/receive_cheque_master.xml',
        'views/receive_cheque.xml',
        'views/cancel_cheque_wizard.xml',
        'views/return_cheque_wizard.xml',
        'views/receive_return_cheque.xml',
        'views/return_reason_view.xml',
        'views/lost_cheque.xml',
        'views/issue_cheque.xml',
        'views/issue_cheque_wizard.xml',
        'views/cheque_config_settings.xml',
        'views/deposit_cheque.xml',
        'views/dishonour_cheque.xml',
        'report/cheque_payment_template.xml',
        'report/cheque_receipt_template.xml',
        'report/cheque_report.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
