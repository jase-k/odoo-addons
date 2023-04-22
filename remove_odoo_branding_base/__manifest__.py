{
    'name': 'Remove Odoo Branding',
    'version': '1.0.0',
    'category': 'Tools',
    'summary': 'Removes Odoo branding from the interface',
    'author': 'Kraft Digital',
    'website': 'https://yourwebsite.com',
    'license': 'LGPL-3',
    'depends': ['web', 'base'],
    'data': [
        'views/webclient_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
}
