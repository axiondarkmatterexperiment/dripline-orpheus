from setuptools import setup, find_namespace_packages

packages = find_namespace_packages('.', include=['dripline.extensions.*'])
print('packages are: {}'.format(packages))

setup(
    name="jitter_plugin",
    version='v1.0.0',
    packages=packages,
)
