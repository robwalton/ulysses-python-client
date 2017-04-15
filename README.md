# ulysses-python-client
A python [x-callback-url](http://x-callback-url.com) client for [Ulysses](https://ulyssesapp.com).

Will provide a python API to Ulysses' [x-callback-url scheme](https://ulyssesapp.com/kb/x-callback-url/). Destined for use in [Alfred](https://www.alfredapp.com)'s [Ulysses worfklow](https://github.com/robwalton/alfred-ulysses-workflow).

## Implemented so far:

- [x]  new-sheet
- [x]  new-group
- [ ]  insert
- [ ]  attach-note
- [ ]  update-note
- [ ]  remove-note
- [ ]  attach-image
- [ ]  attach-keywords
- [ ]  remove-keywords
- [x]  set-group-title
- [ ]  set-sheet-title
- [x]  move
- [x]  copy
- [x]  trash
- [x]  get-item
- [x]  get-root-items
- [ ]  read-sheet
- [x]  get-quick-look-url
- [x]  open
- [x]  open-all, open-recent, open-favorites
- [x]  authorize

## TODO
- get_item and ??? should work with filters too
- rename all if instancdes of identifier, where group, parh or None would also work
