import json
import os
import re
from dataclasses import dataclass
from typing import Iterator

from taiga import TaigaAPI
from taiga.models import UserStory


def get_sfos_topic_id_from_taiga_story_subject(subject):
    match = re.match("(\\d+) - .*", subject)
    if match:
        return int(match.group(1))
    else:
        return None

def push_bugs_to_kanban(bugs):
    api = TaigaAPI()

    api.auth(
        username=os.getenv('KANBAN_USERNAME'),
        password=os.getenv('KANBAN_PASSWORD')
    )

    taigaproject = api.projects.get_by_slug(os.getenv('KANBAN_PROJECT'))

    status_to_taigaid = {x.slug:x.id for x in taigaproject.list_user_story_statuses()}
    # taigaid_to_status = {v:k for k,v in status_to_taigaid.items()}
    # defaultprio = taigaproject.priorities.get(name='High').id
    # defaulttype = taigaproject.issue_types.get(name='Bug').id
    # defaultseverity = taigaproject.severities.get(name='Minor').id
    stories_by_sfos_id = {x.sfos_forum_id: x for x in get_existing_bugs_on_board(taigaproject)}
    print("found %d stories on the board" % len(stories_by_sfos_id))
    for bug in bugs:
        status = status_to_taigaid['new']
        if "fixed" in bug['tags']:
            status = status_to_taigaid['fixed']
        elif "tracked" in bug['tags']:
            status = status_to_taigaid['tracked']

        sfos_id = int(bug['id'])
        if int(sfos_id) in stories_by_sfos_id:
            kanban_found:ExistingBugOnKanban = stories_by_sfos_id[sfos_id]
            print("%d already on kanban as %s" % (sfos_id, kanban_found))
            # always set them to fixed or tracked if they are not
            if status != status_to_taigaid['new'] and status != kanban_found.status:
                print("status updated from %s to %s" %(kanban_found.status,status))
                kanban_found.taiga_story.status = status
                kanban_found.taiga_story.update()
        else:
            taigaproject.add_user_story("%s - %s" % (sfos_id, bug['title']), description=bug['description'], status=status)
            print("added %d" % sfos_id)



@dataclass
class ExistingBugOnKanban:
    status : str
    taiga_id: int
    sfos_forum_id: int
    taiga_story: UserStory

def get_existing_bugs_on_board(taigaproject)->Iterator[ExistingBugOnKanban]:
    for story in taigaproject.list_user_stories():
        topic_id = get_sfos_topic_id_from_taiga_story_subject(story.subject)
        if topic_id:
            yield ExistingBugOnKanban(story.status,story.id, topic_id, story)


if __name__ == '__main__':
    base_temp_path = "/tmp/sfos-forum-bug-moderation-tool"

    with open("%s/summary.json" % base_temp_path) as f:
        bugs = json.load(f)
        push_bugs_to_kanban(bugs)