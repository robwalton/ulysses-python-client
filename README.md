# ulysses-python-client
A python [x-callback-url](http://x-callback-url.com) client for [Ulysses](https://ulyssesapp.com).

Implements Ulysses' [x-callback-url scheme](https://ulyssesapp.com/kb/x-callback-url/). Destined for use in [Alfred](https://www.alfredapp.com)'s [Ulysses worfklow](https://github.com/robwalton/alfred-ulysses-workflow).

## Implemented so far:

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
- Test all text, title, notes and keywords with: _ a://b.c/d?e=f&g=h / \ + ' " 'quoted text'