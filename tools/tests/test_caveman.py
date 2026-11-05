import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from links import same_path
from world import ENCODING, World

AGENT = "cavecrew-investigator.md"


class CavemanTest(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.addCleanup(self.world.close)
        self.checkout = self.world.config / "caveman"
        self.agent = self.world.config / "agents" / AGENT

    def test_install_links_the_search_skills_and_copies_the_agents(self):
        done = self.world.run("install.py")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("caveman: installed v4.0.0", done.stdout)
        target = self.checkout / "skills" / "cavecrew"
        self.assertTrue(same_path(self.world.skill_link("cavecrew"), target))
        self.assertTrue(self.world.skill_link("caveman-explore").exists())
        self.assertFalse(self.world.skill_link("caveman").exists())
        self.assertEqual(self.agent.read_text(encoding=ENCODING), "Investigate.\n")
        self.assertFalse((self.world.config / "agents" / "agents.json").exists())
        settings = (self.world.config / "settings.json").read_text(encoding=ENCODING)
        self.assertNotIn("caveman", settings)

    def test_new_release_updates_the_agents(self):
        self.world.run("install.py")
        self.world.caveman_release("v4.1.0", {f"agents/{AGENT}": "Investigate better.\n"})
        done = self.world.run("update.py")
        self.assertIn("caveman: updated v4.0.0 to v4.1.0", done.stdout)
        self.assertIn(f"caveman agent {AGENT}: copied", done.stdout)
        self.assertEqual(self.agent.read_text(encoding=ENCODING), "Investigate better.\n")
        self.assertIn("caveman: up to date (v4.1.0)", self.world.run("update.py").stdout)

    def test_agent_edited_by_hand_is_left_alone(self):
        self.agent.parent.mkdir(parents=True)
        self.agent.write_text("Mine.\n", encoding=ENCODING)
        done = self.world.run("install.py")
        self.assertIn(f"caveman agent {AGENT}: skipped", done.stdout)
        self.assertEqual(self.agent.read_text(encoding=ENCODING), "Mine.\n")

    def test_uninstall_takes_caveman_away(self):
        self.world.run("install.py")
        done = self.world.run("install.py", "--uninstall")
        self.assertIn("caveman: removed", done.stdout)
        self.assertFalse(self.checkout.exists())
        self.assertFalse(self.world.skill_link("cavecrew").exists())
        self.assertFalse(self.agent.exists())
        registry = self.world.clone / ".ia" / "caveman.json"
        self.assertFalse(registry.exists())


if __name__ == "__main__":
    unittest.main()
