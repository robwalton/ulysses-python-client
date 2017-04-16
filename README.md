# ulysses-python-client
A python [x-callback-url](http://x-callback-url.com) client for [Ulysses](https://ulyssesapp.com).

Implements Ulysses' [x-callback-url scheme](https://ulyssesapp.com/kb/x-callback-url/). Destined for use in [Alfred](https://www.alfredapp.com)'s [Ulysses worfklow](https://github.com/robwalton/alfred-ulysses-workflow).


## Software compatability
Requires:
- macOS
- [Ulysses](https://ulyssesapp.com)
- python 2.7
- Uses macOS [xcall](https://github.com/martinfinke/xcall) (included) for x-callback-url support (Thanks Martin Finke!)
- Needs pytest for testing

## Installation
Check it out:
```bash
$ git clone https://github.com/robwalton/ulysses-python-client.git
Cloning into 'ulysses-python-client'...
```

## Try it out
```python

>>> from ulysses_client import ulysses
>>> ulysses.get_version()
u'2'
>>> token = ulysses.authorize()
>>> ulysses.set_access_token(token)
>>> library = ulysses.get_root_items(recursive=True)
>>> print library[0]
Group(title='iCloud', n_sheets=0, n_containers=4, identifier='4A14NiU-iGaw06m2Y2DNwA')
>>> print '\n'.join(ulysses.treeview(library[0]))
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

## TODO

- Add links up to parent groups
- Logging should go somwhere sensible and include level
- Add to PiPy
  - add tox
  - create setup.py
  - document testing
  - add license
- implement attach-image call
- Do something useful with this
  
