{
    'name': "Show Invoices/Bills Journal Items",

    'summary': "",

    'description': """
Invoice journal items
Invoice journal entry
journal items
journal entry
bill journal items
bill journal entry
journal
show journal items
    """,

    'author': 'wattanadev',
    'website': 'https://',
    'license': 'AGPL-3',


    'category': 'Accounting & Finance',
    'version': '12.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['account'],
    # always loaded
    'data': [
        'views/account_invoice_views.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    "installable": True
}
