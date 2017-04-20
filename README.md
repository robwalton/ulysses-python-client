# ulysses-python-client
A python [x-callback-url](http://x-callback-url.com) client for [Ulysses](https://ulyssesapp.com).

Implements Ulysses' [x-callback-url scheme](https://ulyssesapp.com/kb/x-callback-url/). Destined for use in [Alfred](https://www.alfredapp.com)'s [Ulysses worfklow](https://github.com/robwalton/alfred-ulysses-workflow).


## Software compatability
Requires:
- macOS
- [Ulysses](https://ulyssesapp.com) 2.8
- python 2.7
- Uses macOS' [xcall](https://github.com/martinfinke/xcall) (included) for x-callback-url support (Thanks Martin Finke!)
- Uses [python-xcall](https://github.com/robwalton/python-xcall) (included) to simplify calls to xcall
- Needs pytest for testing

## Installation
Check it out:
```bash
$ git clone https://github.com/robwalton/ulysses-python-client.git
Cloning into 'ulysses-python-client'...
```

## Try it out
```python

>>> import ulysses
>>> ulysses.get_version()
u'2'
>>> token = ulysses.authorize()
>>> ulysses.set_access_token(token)

>>> library = ulysses.get_root_items(recursive=True)
>>> print library[0]
Group(title='iCloud', n_sheets=0, n_containers=4, identifier='4A14NiU-iGaw06m2Y2DNwA')

>>> print '\n'.join(ulysses.treeview(library[0]))
4A14NiU-iGaw06m2Y2DNwA - iCloud:
hZ7IX2jqKbVmPGlYUXkZjQ -    Inbox:
aFV99jXk9_AHHqZJ6znb8w -       test
d5TuSlVXQwZnIWMN0DusKQ -    ulysses-python-client-playground:
dULx6YXeWVqCZzrpsH7-3A -       test sheet
YHlYv7PlYgtm626haxAF4A -    Project:
...
```

## Testing
Running the tests requires the `pytest` and `mock` packages and Ulysses. Code your 
access-token into the top of `test_calls.py`. Get the access token removing the @skip
mark from test_authorise() in this file. 

From the root package folder call:
```bash
MacBook:ulysses-python-client walton$ pytest
...
```

## API calls implemented

- [x]  new-sheet
- [x]  new-group
- [x]  insert
- [x]  attach-note
- [x]  update-note
- [x]  remove-note
- [ ]  attach-image
- [x]  attach-keywords
- [x]  remove-keywords
- [x]  set-group-title
- [x]  set-sheet-title
- [x]  move
- [x]  copy
- [x]  trash
- [x]  get-item
- [x]  get-root-items
- [x]  read-sheet
- [x]  get-quick-look-url
- [x]  open
- [x]  open-all, open-recent, open-favorites
- [x]  authorize


## Licensing & thanks

The code and the documentation are released under the MIT and Creative Commons Attribution-NonCommercial licences respectively. See LICENCE.txt for details.

## TODO

- Do something useful with this
- Add links up to parent groups
- Logging should go somwhere sensible and include level
- Add to PiPy
  - complete setup.py
  - document testing
- implement attach-image call

  
