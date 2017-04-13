

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


logger = logging.getLogger(__name__)


# Only valid for a particular local Ulysses install
MANUALLY_CONFIGURED_TOKEN = 'c6e4ef1a29e44e62acdcee4e5eabc423'


PLAYGROUND_NAME = 'ulysses-python-client-playground'


# [x]  new-sheet
# [x]  new-group
# [ ]  insert
# [ ]  attach-note
# [ ]  update-note
# [ ]  remove-note
# [ ]  attach-image
# [ ]  attach-keywords
# [ ]  remove-keywords
# [ ]  set-group-title
# [ ]  set-sheet-title
# [ ]  move
# [ ]  copy
# [x]  trash
# [x]  get-item
# [x]  get-root-items
# [ ]  read-sheet
# [ ]  get-quick-look-url
# [ ]  open
# [ ]  open-all, open-recent, open-favorites
# [x]  authorize


# pyunit fixture

def setup_module(module):
    xcall_ulysses.token_provider.token = MANUALLY_CONFIGURED_TOKEN


@pytest.fixture('module')
def playground_id():
    groups = upc.get_root_items(recursive=False)
    icloud_grp = groups[0]
    assert icloud_grp.title == 'iCloud'
    # get it directly in order to access its containers
    icloud_grp = upc.get_item(icloud_grp.identifier, True)
    playground_grp = icloud_grp.get_group_by_title(PLAYGROUND_NAME)
    return playground_grp.identifier


@pytest.fixture
def playground_group():
    return upc.get_item(playground_id(), recursive=True)


@pytest.fixture(scope='class')
def random_name():
    return randomword(8)


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
        assert 'Access denied.. Code = 4' in str(excinfo.value)
    finally:
        xcall_ulysses.token_provider.token = original_token


def test_check_play_ground_exists(playground_id):
    item = upc.get_item(playground_id, recursive=False)
    assert item.type == 'group'
    assert item.title == PLAYGROUND_NAME


class TestNewGroupAndTrashing:

    def test_new_group__parent_id(self, random_name, playground_id):
        name = 'new-group-by-id-' + random_name
        self.new_group(name, playground_id)
        self.trash(name)

    def test_new_group__parent_abs_path(self, random_name):
        name = 'new-group-by-abs-path-' + random_name
        self.new_group(name, '/ulysses-python-client-playground')
        self.trash(name)

    def test_new_group__parent_rel_path(self, random_name):
        name = 'new-group-by-rel-path-' + random_name
        self.new_group(name, 'ulysses-python-client-playground')
        self.trash(name)

    def new_group(self, name, parent):
        identifier = upc.new_group(name, parent)
        newgroup = playground_group().get_group_by_title(name)
        assert newgroup.title == name
        assert newgroup.identifier == identifier

    def trash(self, name):
        identifier = playground_group().get_group_by_title(name).identifier
        upc.trash(identifier)


@pytest.fixture(scope='module')
def treename():
    return 'tree-' + randomword(8)


@pytest.fixture(scope='module')
def treegroup(treename):
    treegroup_id = playground_group().get_group_by_title(treename).identifier
    return upc.get_item(treegroup_id, recursive=True)
    #     tree-abhejdgy
    #         upcsheet
    #         group1
    #             sheet1a
    #             sheet1b
    #         group2


@pytest.mark.incremental
class TestBuildAndReadTestTree:

    def test_build_tree_groups(self, treename):
        tree_path = '/' + PLAYGROUND_NAME + '/' + treename
        upc.new_group(treename, PLAYGROUND_NAME)
        # Note reverse order as manually sortd and new ones go to top
        upc.new_group('group2', tree_path)
        upc.new_group('group1', tree_path)

    def test_build_tree_sheets(self, treename):
        tree_path = '/' + PLAYGROUND_NAME + '/' + treename
        upc.new_sheet('upcsheet', tree_path)
        # Note reverse order as manually sortd and new ones go to top
        upc.new_sheet('sheet1b', tree_path + '/group1')
        upc.new_sheet('sheet1a', tree_path + '/group1')

    def test_get_item__group_non_recursive(self, treename):
        treegrp_id = playground_group().get_group_by_title(treename).identifier
        return upc.get_item(treegrp_id, recursive=False)
        assert treegroup.title == treename
        assert treegroup.sheets[0].title == 'upcsheet'
        assert treegroup.containers is None  # unknown

    def test_get_item__group_recursive(self, treename, treegroup):
        assert treegroup.title == treename

        # upcsheet
        assert treegroup.sheets[0].title == 'upcsheet'

        # group1
        group1 = treegroup.containers[0]
        assert group1.title == 'group1'
        assert len(group1.sheets) == 2
        assert group1.containers == []

        # sheet1a
        sheet1a = group1.sheets[0]
        assert sheet1a.title == 'sheet1a'

        # sheet1b
        sheet1b = group1.sheets[1]
        assert sheet1b.title == 'sheet1b'

        # group2
        group2 = treegroup.containers[1]
        assert group2.title == 'group2'
        assert group2.sheets == []
        assert group2.containers == []

    def test_get_item_sheet(self, treename, treegroup):
        upcsheet_id = treegroup.sheets[0].identifier
        upcsheet = upc.get_item(upcsheet_id)
        assert upcsheet.title == 'upcsheet'
        assert upcsheet.type == 'sheet'

    def test_trash_tree(self, treename):
        treegrp_id = playground_group().get_group_by_title(treename).identifier
        upc.trash(treegrp_id)
        with pytest.raises(KeyError):
            playground_group().get_group_by_title(treename)


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
