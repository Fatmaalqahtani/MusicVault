from setuptools import setup, find_packages

setup(
    name='file_management_system',
    version='1.0.0',
    description='A Python-based CLI application for file management with Admin and User roles',
    author='Fatima',
    author_email='Fatmaalqah@hotmail.com',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'mysql-connector-python',
        'cryptography',
        'bcrypt'
    ],
    entry_points={
    'console_scripts': [
        'file_management_system= main',
    ],
},
)
