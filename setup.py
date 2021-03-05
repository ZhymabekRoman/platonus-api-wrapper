from setuptools import setup
from os.path import join, dirname

setup(
    name='platonus_api_wrapper',
    version='0.02a',
    description='Platonus API Wrapper - неофициальная обертка для работы с Платонусом',
    author="Zhymabek Roman",
    author_email="robanokssamit@yandex.ru",
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    url='https://github.com/ZhymabekRoman/platonus-api-wrapper',
    setup_requires=['wheel'],
    install_requires=['munch', 'requests'],
    packages=['platonus_api_wrapper'],
)
