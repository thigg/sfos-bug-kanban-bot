import unittest

from update_kanban import get_sfos_topic_id_from_taiga_story_subject


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(11252,
                         get_sfos_topic_id_from_taiga_story_subject("11252 - Notes on tagging bug reports"))
        self.assertEqual(22,
                         get_sfos_topic_id_from_taiga_story_subject("22 - About the Bug Reports category"))
        self.assertEqual(None,get_sfos_topic_id_from_taiga_story_subject("teststory"))
        self.assertEqual(22,get_sfos_topic_id_from_taiga_story_subject("22"))
        self.assertEqual(1,get_sfos_topic_id_from_taiga_story_subject("1"))


if __name__ == '__main__':
    unittest.main()
