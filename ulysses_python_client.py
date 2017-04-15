"""Ulysses client.

Provides a 1:1 mapping to Ulysses x-callback-url APi defined at:

    https://ulyssesapp.com/kb/x-callback-url/

as well as classes to represent read only Groups (inlcluding filters and trash)
and Sheets

"""


from xcall_ulysses import call_ulysses, call
import json
import logging
import urllib


logging.basicConfig(filename='ulysses-python-client.log',
                    format='%(asctime)s %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


def isID(value):
    """Checks if value looks like a Ulysses ID; i.e. is 22 char long.

    Not an exact science; but good enougth to prevent most mistakes.
    """
    return len(value) == 22


# Ulysses-calls

def authorize():
    """Return access-token string."""
    reply = call_ulysses('authorize', {'appname': 'ulysses_python_client.py'})
    return reply['access-token']


def get_version():
    """Return version string."""
    return call_ulysses('get-version')['apiVersion']


def get_root_items(recursive=True):
    """Return root items.

    recursive -- recurse tree below each root item if True
    """

    recursive = 'YES' if recursive else 'NO'
    reply = call_ulysses('get-root-items', locals(), send_access_token=True)

    item_list = json.loads(reply['items'])
    return [Group(**item) for item in item_list]


def new_group(name, parent=None, index=None):
    """Create new group and return id.

    parent -- Name, path or id of parent. Create in top-level if None
    index -- Position of group in parent. 0 is first.
    """
    identifier = call_ulysses('new-group', locals())['targetId']
    assert isID(identifier)
    return identifier


def set_group_title(group, title):
    """Change group's title and return id.

    group -- Name, path or id of group
    title -- New title string
    """
    call_ulysses('set-group-title', locals(), send_access_token=True)


def set_sheet_title(sheet, title, type):  # @ReservedAssignment
    """Change first paragraph of sheet.

    sheet -- Identifier of sheet to chang
    title -- New title string. Will be URL-encoded
    type -- The markup type of the title. Will be 'heading1'...'heading6',
            'comment' or 'filename' (on external folders with title
            e.g '@: My Filename'
    """
    assert type in ('heading1', 'heading2', 'heading3', 'heading4', 'heading5',
                    'heading6', 'comment', 'filename')
    # title = urllib.quote(title)  # seems not tp be unencoded
    call_ulysses('set-sheet-title', locals(), send_access_token=True)


def new_sheet(text, group=None, format='markdown',  # @ReservedAssignment
              index=None):
    """Create new sheet and return id.

    parent -- Name, path or id of parent. Create in top-level if None
    index -- Position of group in parent. 0 is first.
    format_ -- 'markdown', 'text' or 'html'
    """
    assert format in ('markdown', 'text', 'html', None)
    identifier = call_ulysses('new-sheet', locals())['targetId']
    assert isID(identifier)
    return identifier


def get_item(id, recursive=False):  # @ReservedAssignment
    """Return Group or Sheet instance.

    identifier -- id of sheet (not name or path)
    recursive -- return sub-groups of group if True
    """
    assert isID(id)
    recursive = 'YES' if recursive else 'NO'
    reply = call_ulysses('get-item', locals(), send_access_token=True)
    item = json.loads(urllib.unquote(reply['item']))

    type_ = item['type']
    if type_ == 'group':
        return Group(**item)
    elif type_ == 'sheet':
        return Sheet(**item)
    else:
        raise ValueError('Unsupported type: ' + type_)


def trash(id):  # @ReservedAssignment
    """Move item to trash.

    identifier -- id of sheet (not name or path)
    """
    assert isID(id)
    call_ulysses('trash', locals(), send_access_token=True)


def move(id, targetGroup=None, index=None,  # @ReservedAssignment
         silent_mode=False):
    """Move item to group and/or index (order in a group)

    identifier -- id of sheet to move
    targetGroup -- id, path or group-name to move to. Optional if index
                   provided
    index -- integer position in group to mve to. Optional if targetIdentifier
             provided
    """
    assert targetGroup or (index is not None)
    params = dict(locals())
    del params['silent_mode']
    call_ulysses(
        'move', params, send_access_token=True, silent_mode=silent_mode)


def copy(id, targetGroup=None, index=None,  # @ReservedAssignment
         silent_mode=False):
    """Copy item to group and/or index (order in a group)

    identifier -- id of sheet to move
    targetGroup -- id, path or group-name to move to. Optional if index
                   provided
    index -- integer position in group to mve to. Optional if targetIdentifier
             provided
    """
    assert targetGroup or index
    params = dict(locals())
    del params['silent_mode']
    call_ulysses(
        'copy', params, send_access_token=True, silent_mode=silent_mode)


def get_quick_look_url(id):  # @ReservedAssignment
    """Get the QuickLook URL for a sheet, i.e. location on the file system.

    id -- id of sheet(not path or name)
    """
    assert isID(id)
    url = call_ulysses('get-quick-look-url', locals())['url']
    uri = urllib.unquote(url).replace('\\', '')
    return uri.replace('file://', '')


def open(id):  # @ReservedAssignment
    """Open item, bringing Ulysses forward

    identifier -- id of sheet to move
    id -- id, path or group-name to open
    """
    assert isID(id)
    # Open directly rather than via xcall, as xcall will not bring Ulysses
    # forward
    call('ulysses://x-callback-url/open?id=%s' % id)


def open_all():  # @ReservedAssignment
    """Open special group 'All', bringing Ulysses forward."""
    call('ulysses://x-callback-url/open-all')


def open_recent():  # @ReservedAssignment
    """Open special group 'Last 7 Days', bringing Ulysses forward."""
    call('ulysses://x-callback-url/open-all')


def open_favorites():  # @ReservedAssignment
    """Open special group 'All', bringing Ulysses forward."""
    call('ulysses://x-callback-url/open-favorites')


# Group & Sheet classes

class AbstractItem(object):

    def __init__(self, title=None, type=None,   # @ReservedAssignment
                 identifier=None, hasLifetimeIdentifier=None):
        self.title = urllib.unquote(title)
        self.type = type
        self.identifier = identifier
        self.hasLifetimeIdentifier = hasLifetimeIdentifier

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Group(AbstractItem):
    """Represents a Ulysses Group, Filter or Trash.

    Attributes:

        title -- Name of group
        type -- always 'group', 'filter' or 'trash'
        identifier -- Ulysses id
        hasLifetimeIdentifier -- True if id is unchanged after a move
        sheets -- list of Sheets, empty for filter.
        containers -- list of Groups. Will be None if group_dict resulted from
                      a non-recursive call to Ulysses.

    """

    def __init__(self, title=None, type=None,  # @ReservedAssignment
                 sheets=None, containers=None, identifier=None,
                 hasLifetimeIdentifier=None,):
        """Create a Group and possible the tree below it.

        Best called with **group_dict, where group_dict results from a call
        to Ulysses.

        """
        super(Group, self).__init__(title, type, identifier,
                                    hasLifetimeIdentifier)

        if type not in ('group', 'filter', trash):
            raise AssertionError(
                "type was not group, filter or trash but '%s'" % type)
        self.sheets = []
        for sheet_dict in sheets:
            self.sheets.append(Sheet(**sheet_dict))
        # containers will be None if group was accessed in Ulysses with a
        # non-recursive query
        if containers is not None:
            self.containers = []
            for container_dict in containers:
                if container_dict['type'] == 'filter':
                    logger.warn(
                        "Ignoring filter '%s'" % container_dict['title'])
                    continue
                self.containers.append(Group(**container_dict))
        else:
            self.containers = None  # unknown as non-recursive query

    def get_group_by_title(self, title):
        """Return a group contained immediately within this group.

        Will fail if this Group was accessed non-recursively.

        title -- name of group to return
        """
        if self.containers is None:
            raise Exception('This group was found non-recursively and'
                            ' therefore has no knowledge of its containers')
        for group in self.containers:
            if group.title == title:
                return group
        raise KeyError("No group called '%s' found" % title)

    def get_sheet_by_title(self, title):
        """Return a sheet contained immediately within this group.

        title -- name of sheet to return
        """
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


class Sheet(AbstractItem):

    """Represents a Ulysses Sheet.

    Attributes:

    title -- Name (first line) of sheet
    type -- always 'sheet'
    identifier -- Ulysses id
    hasLifetimeIdentifier -- True if id is unchanged after a move
    titleType -- The markup type of the title. Will be heading1...heading6,
                 comment if the title is a heading or comment. Will be set to
                 filename on external folders or Dropbox if the title is the
                 sheet's filename (e.g. @: My Filename). If no title is given
                 this value is set to None
    creationDate -- The timestamp when the sheet was last modified. The
                    timestamp is given as the number of seconds relative to
                    00:00:00 UTC on 1 January 2001
    modificationDate -- The timestamp when the sheet was created
    changeToken -- a string which change when the sheet is modified

    """
    def __init__(self,  title=None, type=None,   # @ReservedAssignment
                 identifier=None, hasLifetimeIdentifier=None,
                 titleType=None, creationDate=None, modificationDate=None,
                 changeToken=None):
        """Create a Sheet.

        Best called with **sheet_dict, where sheet_dict results from a call
        to Ulysses.
        """

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


