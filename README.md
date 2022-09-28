1. run pull_forum.py to create the json file with the bug reports from the forum
2. run update_kanban.py to use this json file to push the reports to the board
    - supply credentials via enviroment

todo:
 - not only create but also update bugs
 - load a sensible amount of entries from the forum
   - all(?) initially
   - updated since last run on subsequent runs