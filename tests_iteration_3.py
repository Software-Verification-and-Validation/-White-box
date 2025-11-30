import unittest
import io
import sys
from datetime import date, timedelta
from main import FridgeSavvyApp
import subprocess
from pathlib import Path

MAIN = str(Path(__file__).resolve().parent / "main.py")

class TestFridgeSavvyIteration3(unittest.TestCase):
    """
    ITERATION 3: Ingredient Management
    Focus: Adding/removing ingredients to recipes
    Expected Coverage: ~45-50% branch coverage
    Includes all tests from Iterations 1-2 plus ingredient tests
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
    # FROM ITERATIONS 1-2
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

    # --------------------------
    # NEW IN ITERATION 3
    # GROUP C — Ingredients
    # --------------------------

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

if __name__ == "__main__":
    unittest.main()
