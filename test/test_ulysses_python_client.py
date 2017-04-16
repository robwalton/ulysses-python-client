
# -*- coding: utf-8 -*-
"""
These tests assume Ulysses has an icloud library entry.


The MANUALLY_CONFIGURED_TOKEN setting in this module must be configured with
a valid key. To find this, re-nable the test_authorize() test below and
look for the key in the Exception it throws (after Ulysses has popped up
a dialogue asking if the app should be authorised.)

Many tests look for a group called '/ulysses-python-client-playground' at the
top level of the Ulysses library in which to build and remove content.
"""


import ulysses_python_client as upc
import xcall_ulysses
import pytest
from xcall_ulysses import XCallbackError
import logging
import random
import string
import time
import os.path


logger = logging.getLogger(__name__)


# Only valid for a particular local Ulysses install
MANUALLY_CONFIGURED_TOKEN = 'c6e4ef1a29e44e62acdcee4e5eabc423'


PLAYGROUND_NAME = 'ulysses-python-client-playground'

TESTID = 'v_u1RvMlGjJHqofzWdvCNw'


# pyunit fixture

def setup_module(module):
    xcall_ulysses.token_provider.token = MANUALLY_CONFIGURED_TOKEN


@pytest.fixture(scope='module')
def playground_id():
    """Return id of pre-existing playground group."""

    icloud_grp = upc.get_root_items(recursive=False)[0]
    assert icloud_grp.title == 'iCloud'
    icloud_grp = upc.get_item(icloud_grp.identifier, True)
    return icloud_grp.get_group_by_title(PLAYGROUND_NAME).identifier


@pytest.fixture(scope='module')
def testgroup_id(playground_id):
    """Return if of group for this test run and destroy on completion"""

    identifier = upc.new_group(randomword(8), playground_id)
    yield identifier
    upc.trash(identifier)


def group(identifier):
    return upc.get_item(identifier, recursive=True)


@pytest.fixture(scope='module')
def treename():
    return 'tree-' + randomword(8)


@pytest.fixture(scope='module')
def treegroup(treename):
    treegroup_id = playground_group().get_group_by_title(treename).identifier
    return upc.get_item(treegroup_id, recursive=True)


@pytest.fixture(scope='class')
def random_name():
    return randomword(8)


@pytest.fixture
def playground_group():
    return upc.get_item(playground_id(), recursive=True)


# Test up calls

def test_get_version():
    assert upc.get_version() == '2'


@pytest.mark.skip(reason='re-enable to see a valid token and then put this'
                  ' in MANUALLY_CONFIGURED_TOKEN')
def test_authorize():
    # Raise exception with token (just to help determine it!
    raise Exception('authorisation token: ' + upc.authorize())


def test_get_root_items__non_recursive():
    items = upc.get_root_items(recursive=False)

    assert len(items) >= 1
    assert items[0].title == 'iCloud'
    assert isinstance(items[0], upc.Group)


def test_get_root_items__recursive():
    groups = upc.get_root_items(recursive=True)
    icloud_grp = groups[0]

    assert icloud_grp.title == 'iCloud'


def test_get_root_items_with_wrong_access_token():
    original_token = xcall_ulysses.token_provider.token
    try:
        xcall_ulysses.token_provider.token = 'not_the_right_token'
        with pytest.raises(XCallbackError) as excinfo:
            upc.get_root_items()
        assert 'Access denied. Code = 4' in str(excinfo.value)
    finally:
        xcall_ulysses.token_provider.token = original_token


@pytest.mark.skip(reason='Takes 20s to fail for some reason')
def test_get_item_fails():
    identifier = 'x' * 22
    with pytest.raises(XCallbackError):
        upc.get_item(identifier)


def test_check_playground_exists(playground_id):
    item = upc.get_item(playground_id, recursive=False)
    assert item.type == 'group'
    assert item.title == PLAYGROUND_NAME


def test_new_group(testgroup_id):
    name = 'test_new_group'
    identifier = upc.new_group(name, testgroup_id)

    assert upc.get_item(identifier, False).title == name


def test_trash(testgroup_id):
    identifier = upc.new_group('test_trash', testgroup_id)
    group(testgroup_id).get_group_by_title('test_trash')

    upc.trash(identifier)

    with pytest.raises(KeyError):
        group(testgroup_id).get_group_by_title('test_trash')


def test_set_group_title(testgroup_id):
    name = 'test_set_group_title'
    identifier = upc.new_group(name, testgroup_id)

    upc.set_group_title(identifier, name + '_modified')

    group = upc.get_item(identifier, False)
    assert group.title == name + '_modified'


def test_set_sheet_title_with_unicode(testgroup_id):
    title = 'test-set-sheet-title'
    identifier = upc.new_sheet(title, testgroup_id)
    new_title = title + u""" -- abcd () / ? & xyz ' " ‘quoted text’ - end"""
    # shows up as # test_set_sheet_title%20abc%01/2%273%40

    upc.set_sheet_title(identifier, new_title, 'heading2')

    sheet = upc.get_item(identifier)
    assert sheet.title == new_title
    assert sheet.titleType == 'heading2'


def test_move__to_group(testgroup_id):
    sheetid = upc.new_sheet('test_move__to_group-sheet', testgroup_id)
    groupid = upc.new_group('test_move__to_group-group', testgroup_id)

    upc.move(sheetid, groupid)

    group(groupid).get_sheet_by_title('test_move__to_group-sheet')


def test_move__to_index(testgroup_id):
    group_id = upc.new_group('test_move__to_index-group', testgroup_id)
    sheet1_id = upc.new_sheet('sheet1', group_id)
    upc.new_sheet('sheet2', group_id)
    group_ = group(group_id)
    assert group_.sheets[0].title == 'sheet2'
    assert group_.sheets[1].title == 'sheet1'

    upc.move(sheet1_id, index=0, silent_mode=True)

    group_ = group(group_id)
    assert group_.sheets[0].title == 'sheet1'
    assert group_.sheets[1].title == 'sheet2'


def test_copy__to_index(testgroup_id):
    group_id = upc.new_group('test_copy__to_index-group', testgroup_id)
    sheet1_id = upc.new_sheet('sheet0', group_id)
    upc.new_sheet('sheet2', group_id)
    upc.new_sheet('sheet1', group_id)

    upc.copy(sheet1_id, group_id, 1, silent_mode=True)

    group_ = group(group_id)
    assert group_.sheets[0].title == 'sheet1'
    assert group_.sheets[1].title == 'sheet0'
    assert group_.sheets[2].title == 'sheet2'


def test_get_quick_look_url__with_sheet(testgroup_id):
    sht_id = upc.new_sheet('test_get_quick_look_url__with_sheet', testgroup_id)

    path = upc.get_quick_look_url(sht_id)

    assert os.path.exists(path)


@pytest.mark.skip('visual check')
def test__open__open_all__open_recent__open_favorites(testgroup_id):

    sheet_id = upc.new_sheet('test_open\n\nand some text', testgroup_id)
    upc.open(sheet_id)
    time.sleep(5)

    upc.open_all()
    time.sleep(5)

    upc.open_recent()
    time.sleep(5)

    upc.open_favorites()
    time.sleep(5)


class TestItemConstructors():

    def test_sheet(self):
        d = {
            'changeToken': '1|1E9A917F|unfpAQAAAAADAAAA',
            'creationDate': 513446267,
            'hasLifetimeIdentifier': True,
            'identifier': 'ENYa9PBxg3Vj7ws4MO_SWA',
            'modificationDate': 513446268.980628,
            'title': 'upcsheet',
            'titleType': None,
            'type': 'sheet'}
        sheet = upc.Sheet(**d)
        assert sheet.title == 'upcsheet'
        exp = "Sheet(title='upcsheet', identifier='ENYa9PBxg3Vj7ws4MO_SWA')"
        assert str(sheet) == exp


# Test read only item classes

    def test_group_with_no_containers(self):
        d = {
            'hasLifetimeIdentifier': True,
            'identifier': '4A14NiU-iGaw06m2Y2DNwA',
            'sheets': [],
            'title': 'iCloud',
            'type': 'group',
            'sheets': [{'changeToken': '1|1E9A917F|unfpAQAAAAADAAAA',
                        'creationDate': 513446267,
                        'hasLifetimeIdentifier': True,
                        'identifier': 'ENYa9PBxg3Vj7ws4MO_SWA',
                        'modificationDate': 513446268.980628,
                        'title': 'sheet',
                        'titleType': None,
                        'type': 'sheet'}]}
        group = upc.Group(**d)
        assert group.title == 'iCloud'
        assert group.sheets == [upc.Sheet(**d['sheets'][0])]
        assert group.containers is None
        expected = ("Group(title='iCloud', n_sheets=1, n_containers=?unknown?,"
                    " identifier='4A14NiU-iGaw06m2Y2DNwA')")
        assert str(group) == expected

    def test_group_with_containers(self):
        d = {
            'containers': [{
                'containers': [],
                'hasLifetimeIdentifier': True,
                'identifier': 'wjdPFC0ayV4PGjPEMofEgQ',
                'sheets': [{
                    'changeToken': '1|1E9A91A4|mnjpAQAAAAADAAAA',
                    'creationDate': 513446305,
                    'hasLifetimeIdentifier': True,
                    'identifier': 'tv6FBiPRaSBUZ1eJCdUZIA',
                    'modificationDate': 513446307.663547,
                    'title': 'sheet1a',
                    'titleType': None,
                    'type': 'sheet',
                    }, {
                    'changeToken': '1|1E9A91A8|AXnpAQAAAAADAAAA',
                    'creationDate': 513446309,
                    'hasLifetimeIdentifier': True,
                    'identifier': '5uN0A6hqjbO4QWHMV7tkkg',
                    'modificationDate': 513446311.753698,
                    'title': 'sheet1b',
                    'titleType': None,
                    'type': 'sheet',
                    }],
                'title': 'group1',
                'type': 'group',
                }, {
                'containers': [],
                'hasLifetimeIdentifier': True,
                'identifier': 'WrDEUsU7eoFxCDpizAwtNw',
                'sheets': [],
                'title': 'group2',
                'type': 'group',
                }],
            'hasLifetimeIdentifier': True,
            'identifier': 'S_8htbpgEo0KJiXDLXVtdg',
            'sheets': [{
                'changeToken': '1|1E9A9D95|JoTpAQAAAAADAAAA',
                'creationDate': 513446267,
                'hasLifetimeIdentifier': True,
                'identifier': 'ENYa9PBxg3Vj7ws4MO_SWA',
                'modificationDate': 513449353.343165,
                'title': 'upcsheet',
                'titleType': None,
                'type': 'sheet',
                }],
            'title': 'upcgroup',
            'type': 'group',
            }
        upcgroup = upc.Group(**d)
        upcsheet = upc.Sheet(**d['sheets'][0])
        group1 = upc.Group(**d['containers'][0])
        group2 = upc.Group(**d['containers'][1])
        sheet1a = upc.Sheet(**d['containers'][0]['sheets'][0])
        sheet1b = upc.Sheet(**d['containers'][0]['sheets'][1])

        assert upcgroup.title == 'upcgroup'
        assert upcgroup.sheets == [upcsheet]
        assert upcgroup.containers == [group1, group2]
        assert str(upcgroup) == (
            "Group(title='upcgroup', n_sheets=1, n_containers=2,"
            " identifier='S_8htbpgEo0KJiXDLXVtdg')")

        assert group1.title == 'group1'
        assert group1.sheets[0] == sheet1a
        assert group1.sheets[1] == sheet1b
        assert group1.containers == []
        assert str(group1) == (
            "Group(title='group1', n_sheets=2, n_containers=0, identifier="
            "'wjdPFC0ayV4PGjPEMofEgQ')")

        assert group2.title == 'group2'
        assert group2.sheets == []
        assert group2.containers == []
        assert str(group2) == (
            "Group(title='group2', n_sheets=0, n_containers=0, "
            "identifier='WrDEUsU7eoFxCDpizAwtNw')")

        assert upcgroup.get_group_by_title('group1') == group1
        assert upcgroup.get_sheet_by_title('upcsheet') == upcsheet


# http://stackoverflow.com/questions/2030053/random-strings-in-python
def randomword(length):
    return ''.join(random.choice(string.lowercase) for _ in range(length))
