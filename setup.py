from setuptools import setup, find_packages

setup(
    name='consensus',
    version='2.1.1',
    packages=find_packages(),
    install_requires=['progressbar2==3.39.3', 'termcolor==1.1.0', 'yaspin==0.14.3', 'pandas==1.2.3'],
    python_requires='>=3.7.1',
    author='Mariska Slofstra',
    license='GNU Lesser General Public License 3.0',
    test_suite='nose.collector',
    tests_require=['nose', 'parameterized', 'mock']
)
