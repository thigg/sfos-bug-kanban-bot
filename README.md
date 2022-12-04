1. run pull_forum.py to create the json file with the bug reports from the forum
2. run update_kanban.py to use this json file to push the reports to the board
    - supply credentials via enviroment
    - updates bugs if they are tagged in the forum but not in the proper lane on the board

It is regularly run with this script:
```shell
#!/bin/sh
python /opt/sfos-bug-kanban-bot/src/pull_forum.py

KANBAN_USERNAME=yourTaigaId KANBAN_PASSWORD=yourPassword KANBAN_PROJECT=thigg-sfos-bug-mod python update_kanban.py

rm -rf /tmp/sfos-forum-bug-moderation-tool/
```


todo:
- run parallel
- detect gaps between refreshes
- do not load the default number of reports from the forum
  - has now a numPages parameter to pull more from the forum
- add link to description
 - load a sensible amount of entries from the forum
   - all(?) initially
   - updated since last run on subsequent runs