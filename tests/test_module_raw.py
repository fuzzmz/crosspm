#!/usr/bin/env python
# -*- coding: utf-8 -*-
from crosspm import CrossPM
import sys
from treelib import Tree


def tree_dict(packages, _tree=None, _id=None, _flat=None):
    if _tree is None:
        _tree = Tree()
        _id = '<root>'
        _tree.create_node(_id, _id)
    if _flat is None:
        _flat = {}

    for _pkg in packages:
        _pkg_params = packages[_pkg].get_params(['package', 'version'], merged=True)
        pkg_name = _pkg_params['package']
        pkg_ver = _pkg_params['version']
        ver = _flat.get(pkg_name, [])
        pkg_id = '{} [{}]'.format(pkg_name, pkg_ver)
        _tree.create_node(pkg_name, pkg_id, _id, data=pkg_ver)
        if pkg_ver not in ver:
            ver.append(pkg_ver)
        _flat[pkg_name] = ver
        if packages[_pkg].packages:
            _res = tree_dict(packages[_pkg].packages, _tree, pkg_id, _flat)
            _flat = _res[1]
    return _tree, _flat


argv = 'download -c "Z:\\home\\positive\\crosspm\\test\\test14\\crosspm.yaml" --depslock-path="Z:\\home\\positive\\crosspm\\test\\test14\\dependencies.txt" --no-fails'
err, res = CrossPM(argv, return_result='raw').run()
if err == 0:  # Если не возникло других ошибок
    sys.stderr.write("\nCheck for multiple versions:\n\n")

    tree, flat = tree_dict(res)
    max_len = max(len(tree.nodes[x].tag) for x in tree.nodes)

    success = True
    for node in tree.nodes:
        if node != '<root>':
            node_name = tree.nodes[node].tag
            multi_ver = len(flat.get(node_name, [])) > 1
            spaces = ((tree.depth() - tree.depth(node)) * 4) + (max_len - len(node_name))
            tree.nodes[node].tag += '{}    {}    {}'.format(' ' * spaces,
                                                            tree.nodes[node].data,
                                                            '!!!' if multi_ver else '')
            success = success and (not multi_ver)

    sys.stderr.write(str(tree))

    if success:
        sys.stderr.write("\nAll Ok!\n")
else:
    sys.stderr.write("\n{}\n{}".format(err, res))
