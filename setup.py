from setuptools import setup
from os.path import join, dirname
import sys

assert sys.version_info[0] == 3, "Platonus API Wrapper requires Python 3.x"

setup(
    name='platonus_api_wrapper',
    version='2021.03.23',
    description='Platonus API Wrapper - неофициальная обертка для работы с Платонусом',
    author="Zhymabek Roman",
    author_email="robanokssamit@yandex.ru",
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    url='https://github.com/ZhymabekRoman/platonus-api-wrapper',
    setup_requires=['wheel'],
    install_requires=['requests'],
    packages=['platonus_api_wrapper'],
)
