from .ulysses_calls import *


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
