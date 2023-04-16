{
    'name': 'Link Tracker QR Code',
    'version': '1.0',
    'category': 'Tools',
    'license': 'LGPL-3',
    'author': 'Kraft Digital',
    'summary': 'Generate QR codes for link trackers',
    'sequence': 100,
    'depends': [
        'base', 
        'link_tracker'
    ],
    'data': [
        'views/link_tracker_views.xml',
    ],
    'external_dependencies': {
        'python': ['qrcode', 'Pillow'],
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
}
