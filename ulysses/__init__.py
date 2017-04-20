# encoding: utf-8
#
# Copyright (c) 2016 Rob Walton <dhttps://github.com/robwalton>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-04-17
#


import logging

from .calls import *
from ulysses.xcallback import set_access_token


logging.basicConfig(filename='ulysses-python-client.log',
                    format='%(asctime)s %(level): %(message)s',
                    level=logging.DEBUG)


def filter_items(items, title, type_='sheet_or_group'):
    """Filter out items.

    items -- a list of Sheets and/or Groups
    title -- title to match
    type_ -- type to match 'sheet', 'group' or 'sheet_or_group'
    """
    filtered_items = []
    for item in items:
        if (item.title == title and
                (type_ == 'sheet_or_group' or item.type == type_)):
            filtered_items.append(item)
    return filtered_items


def treeview(group, indent=0):
    """"Recursively group structure returning a list of printable lines."""
    lines = []
    lines.append(
        group.identifier + ' - ' + '   ' * indent + group.title + ':')
    for sheet in group.sheets:
        lines.append(
            sheet.identifier + ' - ' + '   ' * (indent + 1) + sheet.title)
    for sub_group in group.containers:
        lines.extend(treeview(sub_group, indent + 1))
    return lines
