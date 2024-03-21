{
    'name': 'Transport',
    'summary': 'Odoo Transport',
    'description': '''
        
    ''',
    'version': '17.0.1.2.1',
    'category': 'Techlead',
    'license': 'LGPL-3',
    'author': 'MuK IT',
    'website': 'https://www.techlead.vn/',
    'live_test_url': 'https://www.techlead.vn/',
    'contributors': [
        '',
    ],
    'depends': ['base', 'web'
                ],
    'excludes': [
        'web_enterprise',
    ],
    'data': [
        'security/transport.xml',
        'security/ir.model.access.csv',
        'view/transport.xml',
        'view/bao_hang.xml',
        'view/khach_hang.xml',
        'view/kho_van_chuyen.xml',
        'view/doi_tac.xml',
        'view/tien_trinh.xml'
    ],
    'assets': {

    },
    'images': [

    ],
}
