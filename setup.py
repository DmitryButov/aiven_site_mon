from setuptools import setup, find_packages

setup(
    name='aiven_site_mon',
    description='Aiven Site Monitor',
    version='0.1',
    url='https://github.com/DmitryButov/aiven_site_mon',
    author="DmitryButov",
    author_email='bdswork@mail.ru',
    license='MIT',
    packages=find_packages(where='src'),
    package_dir={"": "src"},
    scripts=['scripts/aiven_site_mon'],
    entry_points={
        'console_scripts': [
            'aiven_site_mon_entry_test=aiven_site_mon.common.console_app:main',
        ],
    },
)