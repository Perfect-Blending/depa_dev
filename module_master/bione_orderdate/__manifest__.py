{
    'name': 'Bione Order Date',
    'version': '12.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Edit Order Date',
    'sequence': '10',
    'license': 'AGPL-3',
    'author': 'wattanadev',
    'maintainer': 'wattanadev',
    'website': 'https://odoo.com',
    'live_test_url': 'https://www.youtube.com/',
    'depends': ['base', 'sale'],
    'demo': [],
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
        # 'data/ir_sequence_data.xml',
        # 'data/data.xml',

        # 'wizards/create_appointment.xml',
        'views/views.xml',

        #
        #
        # 'reports/report.xml',

        # 'data/mail_template.xml',
    ],
    # 'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
