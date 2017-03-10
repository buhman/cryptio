import alabaster

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'alabaster'
]

html_theme = 'alabaster'
html_theme_path = [alabaster.get_path()]
source_suffix = '.rst'

master_doc = 'index'

project = 'cryptio'
copyright = '2017 ptpb'

pygments_style = 'sphinx'

highlight_language = 'python3'

html_theme_options = {
    'description': 'authenticated file encryption library',
    'github_user': 'ptpb',
    'github_repo': 'cryptio',
    'github_button': True,
    'github_type': 'star',
    'github_banner': True,
    'pre_bg': '#FFF6E5',
    'note_bg': '#E5ECD1',
    'note_border': '#BFCF8C',
    'body_text': '#482C0A',
    'sidebar_text': '#49443E',
    'sidebar_header': '#4B4032',
    'shield_list': [
        {
            'image': 'https://img.shields.io/circleci/project/github/ptpb/cryptio.svg',
            'target': 'https://circleci.com/gh/ptpb/cryptio'
        },
        {
            'image': 'https://img.shields.io/codecov/c/github/ptpb/cryptio.svg',
            'target': 'https://codecov.io/gh/ptpb/cryptio'
        },
        {
            'image': 'https://img.shields.io/pypi/v/cryptio.svg',
            'target': 'https://pypi.org/project/cryptio/'
        }
    ]
}

html_sidebars = {
    '**': [
        'about.html', 'navigation.html', 'searchbox.html',
    ]
}
