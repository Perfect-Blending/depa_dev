{
    'name': 'PFB Employee Number',
    'version': '12.0.1.0',
    'sequence': 1,
    'category': 'Generic Modules/Human Resources',
    'description':
        """
        This Module add below functionality into odoo

        1.This module helps you to display unique Employee Number on Employee screen

    """,
    'summary': 'Odoo app will add Employee Number on Employee screen',
    'depends': ['hr'],
    'data': [
        'views/employee_sequence.xml',
        'views/employee_view.xml'
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    #author and support Details ==========#
    'author': 'wattanadev',
    'website': 'http://perfecterp.co',
    'maintainer': 'wattanadev',
    'support': '',
}


