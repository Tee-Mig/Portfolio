# build

python setup.py sdist bdist_wheel

# Installation

pip install dist/ft_package-0.0.1-py3-none-any.whl

# Show informations

pip show -v ft_package

# Test

python tester.py

# Uninstallation

pip uninstall ft_package

# Cleanup build files

rm -rf build dist ft_package.egg-info
