{
    'name': 'BiOne HR',
    'summary': 'Modify field in HR module',
    'version': '12.0.1.0.0',
    'category': 'Human Resource',
    'website': 'https://bione.co.th',
    'author': 'BiOne',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'hr',
        'hr_expense',
    ],
    'data': [
        'views/hr_expense_sheet_views.xml',
    ],
}
