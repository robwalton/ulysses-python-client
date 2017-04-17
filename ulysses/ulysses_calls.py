# encoding: utf-8
#
# Copyright (c) 2016 Rob Walton <dhttps://github.com/robwalton>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-04-17
#

"""Ulysses client.

Provides a 1:1 mapping to Ulysses x-callback-url APi defined at:

    https://ulyssesapp.com/kb/x-callback-url/

as well as classes to represent read only Groups (inlcluding filters and trash)
and Sheets

"""

import ulysses.xcall  # @UnusedImport
from ulysses.xcall import call_ulysses, call


import json
import logging
import urllib


__all__ = ['attach_keywords', 'attach_note', 'authorize', 'call', 'copy',
           'get_item', 'get_quick_look_url', 'get_root_items', 'get_version',
           'insert', 'move', 'new_group', 'new_sheet', 'open', 'open_all',
           'open_favorites', 'open_recent', 'read_sheet', 'remove_keywords',
           'remove_note', 'set_access_token', 'set_group_title',
           'set_sheet_title', 'trash', 'update_note']


logging.basicConfig(filename='ulysses-python-client.log',
                    format='%(asctime)s %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


def set_access_token(token):
    """Set access token required for many Ulysses calls."""
    ulysses.xcall.token_provider.token = token


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


def read_sheet(id, text=False):  # @ReservedAssignment
    """Return a sheet with more detail than get_item().

    id -- id of sheet(not path or name)
    text -- return full text of sheet
    """

    text = 'YES' if text else 'NO'
    reply = call_ulysses('read-sheet', locals(), send_access_token=True)
    sheet_dict = json.loads(urllib.unquote(reply['sheet']))
    assert sheet_dict['type'] == 'sheet'
    return SheetWithContent(**sheet_dict)


def get_quick_look_url(id):  # @ReservedAssignment
    """Get the QuickLook URL for a sheet, i.e. location on the file system.

    id -- id of sheet(not path or name)
    """
    assert isID(id)
    url = call_ulysses('get-quick-look-url', locals())['url']
    uri = urllib.unquote(url).replace('\\', '')
    return uri.replace('file://', '')


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
    call_ulysses('set-sheet-title', locals(), send_access_token=True)


def insert(id, text, format='markdown', position='end',  # @ReservedAssignment
           newline=None):
    """Insert or append text to a sheet.

    id -- id of sheet
    text -- text to append
    format -- 'markdown', 'text' or 'html'
    position -- 'begin' or 'end'
    newline -- 'prepend', 'append', 'enclose' or None

    """
    assert isID(id)
    assert format in ('markdown', 'text', 'html', )
    assert position in ('begin', 'end')
    assert newline in ('prepend', 'append', 'enclose', None)
    call_ulysses('insert', locals(), send_access_token=True)


def attach_keywords(id, keywords):  # @ReservedAssignment
    """Attach keywords to sheet.

    id -- id of sheet to modify
    keywords -- list of keywords
    """
    assert isID(id)
    keywords = ','.join(keywords)
    call_ulysses('attach-keywords', locals())


def remove_keywords(id, keywords):  # @ReservedAssignment
    """Remove keywords from a sheet.

    id -- id of sheet to modify
    keywords -- list of keywords
    """
    assert isID(id)
    keywords = ','.join(keywords)
    call_ulysses('remove-keywords', locals(), send_access_token=True)


def attach_note(id, text, format='markdown'):  # @ReservedAssignment
    """Add a new note attachment to a sheet.

    id -- id of sheet
    text -- text of note
    format -- 'markdown', 'text' or 'html'
    """
    assert format in ('markdown', 'text', 'html')
    call_ulysses('attach-note', locals())


def update_note(id, index, text, format='markdown'):  # @ReservedAssignment
    """Update an existing note attachment on a sheet.

    id -- id of sheet
    index -- index of note on sheet (starting at 0)
    text -- text of note
    format -- 'markdown', 'text' or 'html'
    """
    assert format in ('markdown', 'text', 'html')
    call_ulysses('update-note', locals(), send_access_token=True)


def remove_note(id, index):  # @ReservedAssignment
    """Add a new note attachment to a sheet.

    id -- id of sheet
    index -- index of note on sheet (starting at 0)
    """
    call_ulysses('remove-note', locals(), send_access_token=True)


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

    def __unicode__(self):
        title = self.title
        identifier = self.identifier
        n_sheets = len(self.sheets)
        if self.containers is not None:
            n_containers = len(self.containers)
        else:
            n_containers = '?unknown?'
        return (u"Group(title='%(title)s', n_sheets=%(n_sheets)s, n_containers"
                u"=%(n_containers)s, identifier='%(identifier)s')" % locals())

    def __str__(self):
        return unicode(self).encode('utf-8')


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

        super(Sheet, self).__init__(
            title, type, identifier, hasLifetimeIdentifier)
        if type != 'sheet':
            raise ValueError('Unexpected type: ' + str(type))
        self.changeToken = changeToken
        self.creationDate = creationDate
        self.modificationDate = modificationDate
        self.titleType = titleType

    def __unicode__(self):
        title = self.title
        identifier = self.identifier
        return (u"Sheet(title='%(title)s', identifier='%(identifier)s')"
                % locals())

    def __str__(self):
        return unicode(self).encode('utf-8')


class SheetWithContent(Sheet):
    """Represents a Ulysses sheet in more detail than Sheet

    Attributes (as Sheet and in addition):

    text -- The sheets content encoded as Markdown. This is only available if
            the text parameter was set to True when created with read_sheet()
    keywords -- list of strings representing keywords
    notes -- list of strings representing notes in markdown

    """
    def __init__(self,  title=None, type=None,   # @ReservedAssignment
                 identifier=None, hasLifetimeIdentifier=None,
                 titleType=None, creationDate=None, modificationDate=None,
                 changeToken=None, text=None, keywords=None, notes=None):
        """Create a Sheet.

        Best called with **sheet_dict, where sheet_dict results from a call
        to Ulysses.
        """
        super(SheetWithContent, self).__init__(
            title, type, identifier, hasLifetimeIdentifier, titleType,
            creationDate, modificationDate, changeToken)

        self.text = unicode(text)
        self.keywords = list(keywords)
        self.notes = list(notes)
