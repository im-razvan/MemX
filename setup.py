from setuptools import setup, find_packages

setup(
    name='memx',
    version='1.0.7',
    author="Iacob Razvan Mihai",
    author_email="razvan.iacob@protonmail.com",
    description='A Python Library to Manipulate macOS Processes.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'psutil'
    ],
    keywords=['memory', 'macos', 'hacking'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: MIT License',
        "Operating System :: MacOS :: MacOS X"
    ],

    license='MIT'
)