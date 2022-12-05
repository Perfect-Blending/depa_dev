{
    'name': "Update product cost on vendor bill",
    'summary': """This module udate product cost price on vendor bill validation. 
               Don't use this module if you use Odoo's dsfault costing methods     
               """,
    'version': '12.0.1.0.0',
    'description': """
       Update cost from purchase invoice
    """,
    'author': 'wattanadev',
    'company': '',
    'website': "",
    'category': 'product',
    'depends': ['base', 'account'],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
