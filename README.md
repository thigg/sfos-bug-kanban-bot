1. run pull_forum.py to create the json file with the bug reports from the forum
2. run update_kanban.py to use this json file to push the reports to the board
    - supply credentials via enviroment
    - updates bugs if they are tagged in the forum but not in the proper lane on the board

todo:
- run parallel
- detect gaps between refreshes
- do not load the default number of reports from the forum
- add link to description
 - load a sensible amount of entries from the forum
   - all(?) initially
   - updated since last run on subsequent runs