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
- [ ]  set-group-title
- [ ]  set-sheet-title
- [ ]  move
- [ ]  copy
- [x]  trash
- [x]  get-item
- [x]  get-root-items
- [ ]  read-sheet
- [ ]  get-quick-look-url
- [ ]  open
- [ ]  open-all, open-recent, open-favorites
- [x]  authorize

## TODO
- Call `xattr -dr com.apple.quarantine "bin/xcall.app"` to authorise unsigned xcall app programatically
