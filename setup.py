from distutils.core import setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='mjooln',
    packages=['mjooln', 'mjooln.core', 'mjooln.file'],
    version='0.3.1',
    license='MIT',
    description='Environmentally Friendly File Handling',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Vemund Halmø Aarstrand',
    author_email='vemundaa@gmail.com',
    url='https://github.com/vemundaa/mjooln',
    download_url='https://github.com/vemundaa/mjooln/archive/v_031.tar.gz',
    keywords=['os', 'path', 'file', 'folder', 'file handling'],
    install_requires=[
        'python-dateutil',
        'pytz',
        'simplejson',
        'psutil',
        'cryptography',
    ],
  classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
  ],
)
