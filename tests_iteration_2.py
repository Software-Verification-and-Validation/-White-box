import unittest
import io
import sys
from datetime import date, timedelta
from main import FridgeSavvyApp
import subprocess
from pathlib import Path

MAIN = str(Path(__file__).resolve().parent / "main.py")

class TestFridgeSavvyIteration2(unittest.TestCase):
    """
    ITERATION 2: Recipe Management Basics
    Focus: Recipe creation and removal
    Expected Coverage: ~30-35% branch coverage
    Includes all tests from Iteration 1 plus recipe tests
    """

    # Utility: run a sequence of commands and capture output
    def run_cmds(self, commands):
        app = FridgeSavvyApp()
        buffer = io.StringIO()
        sys_stdout = sys.stdout
        sys.stdout = buffer
        try:
            for cmd in commands:
                app.handle_command(cmd)
        finally:
            sys.stdout = sys_stdout
        return buffer.getvalue(), app

    # --------------------------
    # FROM ITERATION 1
    # --------------------------

    def test_A1_add_valid_item(self):
        out, app = self.run_cmds(["add Milk Dairy 2025-11-01"])
        self.assertIn("Added item 'Milk'", out)
        self.assertEqual(len(app.pantry), 1)

    def test_A3_remove_existing(self):
        out, app = self.run_cmds([
            "add Milk Dairy 2025-11-01",
            "remove Milk"
        ])
        self.assertIn("Removed item 'Milk'", out)
        self.assertEqual(len(app.pantry), 0)

    def test_A4_remove_missing(self):
        out, _ = self.run_cmds(["remove Unknown"])
        self.assertIn("No pantry item named", out)

    def test_H2_help(self):
        out, _ = self.run_cmds(["help"])
        self.assertIn("Available commands", out)

    def test_H4_exit(self):
        app = FridgeSavvyApp()
        buffer = io.StringIO()
        sys_stdout = sys.stdout
        sys.stdout = buffer
        try:
            result = app.handle_command("exit")
        finally:
            sys.stdout = sys_stdout
        self.assertFalse(result)

    # --------------------------
    # NEW IN ITERATION 2
    # GROUP B — Recipe Creation
    # --------------------------

    def test_B1_create_recipe(self):
        out, app = self.run_cmds(["create recipe Pasta"])
        self.assertIn("Created empty recipe 'Pasta'", out)
        self.assertIn("Pasta", app.recipes)

    def test_B2_create_recipe_twice(self):
        out, _ = self.run_cmds(["create recipe Pasta", "create recipe Pasta"])
        self.assertIn("already exists", out)

    def test_B3_remove_recipe(self):
        out, app = self.run_cmds([
            "create recipe Pasta",
            "remove recipe Pasta"
        ])
        self.assertNotIn("Pasta", app.recipes)
        self.assertIn("Removed recipe 'Pasta'", out)

    def test_B4_remove_missing_recipe(self):
        out, _ = self.run_cmds(["remove recipe NOPE"])
        self.assertIn("No recipe named", out)

if __name__ == "__main__":
    unittest.main()
