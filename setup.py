
from distutils.core import setup
from distutils.command.build_ext import build_ext

import yuvist


setup(
    name='yuvist',
    version=yuvist.__version__,
    author='luuvish',
    author_email='luuvish@gmail.com',
    url='https://github.com/luuvish/yuvist',
    license='LGPL',
    description=(
        'A software library for rapid development of '
        'hardware-accelerated multitouch applications.'
    ),
    ext_modules=[],
    cmdclass={'build_ext': build_ext},
    packages=[
        'yuvist',
        'yuvist.core',
        'yuvist.core.video',
        'yuvist.tools',
        'yuvist.uix'
    ],
    package_dir={'yuvist': 'yuvist'},
    package_data={'yuvist': [
        'data/skins/*.kv',
        'data/skins/movist/*.tiff',
        'data/skins/movist/*.icns',
        'data/images/*.ico',
        'data/images/*.png'
    ]},
    scripts=['tools/yuvist']
)
