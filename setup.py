from distutils.core import setup

with open('README') as f:
    long_description = f.read()

setup(
    name='mjooln',
    packages=['mjooln', 'mjooln.atom', 'mjooln.core', 'mjooln.tree'],
    version='0.4.0',
    license='MIT',
    description='Environmentally Friendly File Handling',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Vemund Halmø Aarstrand',
    author_email='vemundaa@gmail.com',
    # url='https://github.com/vemundaa/mjooln',
    url='https://mjooln.readthedocs.io/en/latest/',
    download_url='https://github.com/vemundaa/mjooln/archive/v_040.tar.gz',
    keywords=['JSON', 'PATH', 'FILE', 'FOLDER', 'FILE HANDLING',
              'ENCRYPTION', 'COMPRESSION', 'AES', 'GZIP', 'UUID', 'UTC',
              'MD5 CHECKSUM'],
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
