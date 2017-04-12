from xcall_ulysses import call_ulysses
import json
import logging


logging.basicConfig(filename='ulysses-python-client.log', level=logging.INFO)
logger = logging.getLogger(__name__)


# Ulysses-calls

def authorize():
    """Return access-token string."""
    reply = call_ulysses('authorize', {'appname': 'ulysses_python_client.py'})
    return reply['access-token']


def get_version():
    """Return version string."""
    return call_ulysses('get-version')['apiVersion']


def get_root_items(recursive=True):
    """Return root items."""

    recursive_par = 'YES' if recursive else 'NO'
    reply = call_ulysses(
        'get-root-items', {'recursive': recursive_par}, send_access_token=True)

    item_list = json.loads(reply['items'])
    return [Group(**item) for item in item_list]


def new_group(name, parent=None, index=None):
    params = {'name': name}
    if parent:
        params['parent'] = parent
    if index:
        assert str(int(index)) == index, 'index must be an integer'
        params['index'] = index
    return call_ulysses('new-group', params)['targetId']


def new_sheet(text, group=None, format_='markdown', index=None):
    params = {'text': text}
    if format_:
        assert format_ in ('markdown', 'text', 'html')
        params['format'] = format_
    if group:
        params['group'] = group
    if index:
        assert str(int(index)) == index, 'index must be an integer'
        params['index'] = index
    return call_ulysses('new-sheet', params)['targetId']


def get_item(identifier, recursive=False):
    params = {'id': identifier, 'recursive': 'YES' if recursive else 'NO'}
    reply = call_ulysses('get-item', params, send_access_token=True)
    item = json.loads(reply['item'])

    type_ = item['type']
    if type_ == 'group':
        return Group(**item)
    elif type_ == 'sheet':
        return Sheet(**item)
    else:
        raise ValueError('Unsupported type: ' + type_)


def trash(identifier):
    call_ulysses('trash', {'id': identifier}, send_access_token=True)


# Group & Sheet classes

class Item(object):

    def __init__(self, title=None, type=None,   # @ReservedAssignment
                 identifier=None, hasLifetimeIdentifier=None):
        self.title = title
        self.type = type
        self.identifier = identifier
        self.hasLifetimeIdentifier = hasLifetimeIdentifier

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Group(Item):

    def __init__(self, title=None, type=None,  # @ReservedAssignment
                 sheets=None, containers=None, identifier=None,
                 hasLifetimeIdentifier=None,):

        super(Group, self).__init__(title, type, identifier,
                                    hasLifetimeIdentifier)
        assert type == 'group'
        self.sheets = []
        for sheet_dict in sheets:
            self.sheets.append(Sheet(**sheet_dict))
        # containers will be None if group was accessed in Ulysses with a
        # non-recursive query
        if containers is not None:
            self.containers = []
            for container_dict in containers:
                self.containers.append(Group(**container_dict))
        else:
            self.containers = None  # unknown as non-recursive query

    def get_group_by_title(self, title):
        if self.containers is None:
            raise Exception('This group was found non-recursively and'
                            ' therefore has no knowledge of its containers')
        for group in self.containers:
            if group.title == title:
                return group
        raise KeyError("No group called '%s' found" % title)

    def get_sheet_by_title(self, title):
        for sheet in self.sheets:
            if sheet.title == title:
                return sheet
        raise KeyError("No sheet called '%s' found" % title)

    def __str__(self):
        title = self.title
        identifier = self.identifier
        n_sheets = len(self.sheets)
        if self.containers is not None:
            n_containers = len(self.containers)
        else:
            n_containers = '?unknown?'
        return ("Group(title='%(title)s', n_sheets=%(n_sheets)s, n_containers="
                "%(n_containers)s, identifier='%(identifier)s')" % locals())


class Sheet(Item):

    def __init__(self,  title=None, type=None,   # @ReservedAssignment
                 identifier=None, hasLifetimeIdentifier=None,
                 titleType=None, creationDate=None, modificationDate=None,
                 changeToken=None):
        super(Sheet, self).__init__(title, type, identifier,
                                    hasLifetimeIdentifier)
        if type != 'sheet':
            raise ValueError('Unexpected type: ' + str(type))
        self.changeToken = changeToken
        self.creationDate = creationDate
        self.modificationDate = modificationDate
        self.titleType = titleType

    def __str__(self):
        title = self.title
        identifier = self.identifier
        return ("Sheet(title='%(title)s', identifier='%(identifier)s')"
                % locals())


def filter_items(items, title, type_='sheet_or_group'):
    filtered_items = []
    for item in items:
        if (item.title == title and
                (type_ == 'sheet_or_group' or item.type == type_)):
            filtered_items.append(item)
    return filtered_items
