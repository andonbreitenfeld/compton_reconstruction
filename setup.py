from glob import glob

from setuptools import find_packages, setup

package_name = 'compton_reconstruction'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        (f'share/{package_name}', ['package.xml']),
        (f'share/{package_name}/config', glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Andon Breitenfeld',
    maintainer_email='andonbreitenfeld@utexas.edu',
    description='3D LM-MLEM Compton image reconstruction with Scene Data Fusion for the M400 detector on Spot.',
    license='TBD',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'record_bag = compton_reconstruction.record_bag:main',
            'replay_bag = compton_reconstruction.replay_bag:main',
        ],
    },
)
