# Copyright 2020 BiOne Solutions Co., Ltd (https://bione.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'PFB Purchase Agreement',
    'category': 'Extra Tools',
    'summary': 'Add Filed Purchase Agreement',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'wattanadev',
    'website': 'https://perfecterp.co',
    'depends': [
        'base_setup', 'purchase_requisition'
    ],
    'data': [
        'views/purchase_agreement.xml',
    ],
    'installable': True,
}
