Usage as Python module
=======
You can use CrossPM in python-code:
```python
from crosspm import CrossPM
config_name = 'myconfig.yaml'
dependencies = 'dependencies.txt.lock'
argv = 'download -c "{}" --depslock-path="{}" --no-fails'.format(config_name, dependencies)

# run download and get result
# crosspm_raw_packages - LIST of all downloaded packages (with duplicate)
err, crosspm_raw_packages = CrossPM(argv, return_result='raw').run()

crosspm_unique_packages = set(crosspm_raw_packages)

# crosspm_tree_packages - LIST of first-level packages, with child in package.packages variable
err, crosspm_tree_packages = CrossPM(argv, return_result='tree').run()


package = crosspm_tree_packages[0]
child_packages = package.packages # access to all child packages
duplicate = package.duplicated # TRUE if other package with 'unique' field exist in tree
```