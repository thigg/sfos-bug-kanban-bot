import json
import os
from taiga import TaigaAPI


def push_bugs_to_kanban(bugs):
    api = TaigaAPI()

    api.auth(
        username=os.getenv('KANBAN_USERNAME'),
        password=os.getenv('KANBAN_PASSWORD')
    )

    taigaproject = api.projects.get_by_slug('KANBAN_PROJECT')

    stati = {x.slug:x.id for x in taigaproject.list_user_story_statuses()}
    # defaultprio = taigaproject.priorities.get(name='High').id
    # defaulttype = taigaproject.issue_types.get(name='Bug').id
    # defaultseverity = taigaproject.severities.get(name='Minor').id
    for bug in bugs:
        status = stati['new']
        if "fixed" in bug['tags']:
            status = stati['fixed']
        elif "tracked" in bug['tags']:
            status = stati['tracked']

        taigaproject.add_user_story("%s - %s"%(bug['id'],bug['title']),description=bug['description'],status=status)
        print("added %d" % bug['id'])

base_temp_path = "/tmp/sfos-forum-bug-moderation-tool"

with open("%s/summary.json" % base_temp_path) as f:
    bugs = json.load(f)
    push_bugs_to_kanban(bugs)
