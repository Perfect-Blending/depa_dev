{
    'name': 'BiOne Account Payment',
    'summary': 'Modify field in account module',
    'version': '12.0.1.0.1',
    'category': 'Account',
    'website': 'https://bione.co.th',
    'author': 'BiOne',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'base',
        'account',
        'account_billing',
        'account_payment_netting',
        # 'account_payment_intransit',
        'l10n_th_withholding_tax_cert',
    ],
    'data': [
        'security/security.xml',
        'views/account_invoice_view.xml',
        'views/account_payment_view.xml',
        'views/account_billing.xml',
    ],
}
