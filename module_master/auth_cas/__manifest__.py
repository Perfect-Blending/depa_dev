# -*- coding: utf-8 -*-


{
    'name': 'CAS Authentication',
    'version': '12.0.1.0.0',
    'category': 'Authentication',
    'summary': 'CAS Authentication',
    'author': 'wattanadev',
    'license': 'AGPL-3',
    'support': '',
    'website': 'https://www.perfectblending.com/',
    'depends': [
        'base_setup',
        'web'
    ],
    'data': [
        'wizard/res_config_view.xml',
        'views/auth_cas_view.xml'
    ],
    'installable': True,
    'application': True,
}
