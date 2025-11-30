import unittest
import io
import sys
from datetime import date, timedelta
from main import FridgeSavvyApp
import subprocess
from pathlib import Path

MAIN = str(Path(__file__).resolve().parent / "main.py")

class TestFridgeSavvyIteration4(unittest.TestCase):
    """
    ITERATION 4: Meal Planning and Listing
    Focus: Planning/unplanning recipes and basic list commands
    Expected Coverage: ~60-65% branch coverage
    Includes all tests from Iterations 1-3 plus planning/list tests
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
    # FROM ITERATIONS 1-3
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

    def test_C1_add_ingredient_ok(self):
        out, app = self.run_cmds([
            "create recipe Salad",
            "add ingredient Salad Tomato 100 g"
        ])
        self.assertIn("Added ingredient 'Tomato'", out)
        self.assertIn("Tomato", app.recipes["Salad"])

    def test_C2_add_ingredient_missing_recipe(self):
        out, _ = self.run_cmds(["add ingredient Missing Tomato 100 g"])
        self.assertIn("does not exist", out)

    def test_C3_remove_existing_ingredient(self):
        out, app = self.run_cmds([
            "create recipe Salad",
            "add ingredient Salad Tomato 100 g",
            "remove ingredient Salad Tomato"
        ])
        self.assertIn("Removed ingredient", out)
        self.assertNotIn("Tomato", app.recipes["Salad"])

    def test_C4_remove_missing_ingredient(self):
        out, _ = self.run_cmds([
            "create recipe Salad",
            "remove ingredient Salad Tomato"
        ])
        self.assertIn("has no ingredient", out)

    # --------------------------
    # NEW IN ITERATION 4
    # GROUP D — Planning
    # --------------------------

    def test_D1_plan_ok(self):
        out, app = self.run_cmds([
            "create recipe Soup",
            "plan Soup 2025-10-10"
        ])
        self.assertIn("Planned recipe", out)
        self.assertEqual(len(app.meal_plan), 1)

    def test_D2_plan_missing_recipe(self):
        out, _ = self.run_cmds(["plan Missing 2025-10-10"])
        self.assertIn("does not exist", out)

    def test_D3_unplan_ok(self):
        out, app = self.run_cmds([
            "create recipe Soup",
            "plan Soup 2025-10-10",
            "unplan Soup 2025-10-10"
        ])
        self.assertIn("Removed planned recipe", out)
        self.assertEqual(len(app.meal_plan), 0)

    def test_D4_unplan_missing(self):
        out, _ = self.run_cmds([
            "create recipe Soup",
            "unplan Soup 2025-10-10"
        ])
        self.assertIn("No planned recipe", out)

    # --------------------------
    # GROUP E — List Commands
    # --------------------------

    def test_E1_list_pantry_empty(self):
        out, _ = self.run_cmds(["list pantry"])
        self.assertIn("Pantry is empty", out)

    def test_E3_list_recipe_empty(self):
        out, _ = self.run_cmds([
            "create recipe Empty",
            "list recipe Empty"
        ])
        self.assertIn("has no ingredients", out)

    def test_E4_list_recipe_missing(self):
        out, _ = self.run_cmds(["list recipe Nope"])
        self.assertIn("No recipe named", out)

    def test_E5_list_expiring_none(self):
        out, _ = self.run_cmds(["list expiring"])
        self.assertIn("No items expiring", out)

if __name__ == "__main__":
    unittest.main()
