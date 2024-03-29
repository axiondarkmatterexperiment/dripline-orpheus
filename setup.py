from setuptools import setup, find_namespace_packages, find_packages

packages = find_namespace_packages('.', include=['dripline.extensions.*'])
print('packages are: {}'.format(packages))

setup(
    name="dripline-orpheus",
    version='v1.0.0',
    packages=packages,
    include_package_data=True
)
