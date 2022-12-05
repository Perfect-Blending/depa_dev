

{
    'name': "BiOne Customer Sequence",
    'version': '12.0.1.0.0',
    'summary': """Unique Customer Code""",
    'description': """
       Each customer have unique number code
    """,
    'author': 'wattanadev',
    'company': 'BiOne Solutions',
    'website': "https://thaiodoo.com/",
    'category': 'Sales',
    'depends': ['sale'],
    'data': [
        'views/res_partner_fom.xml',
        'views/res_company.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'application': False
}
