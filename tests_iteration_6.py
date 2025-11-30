import unittest
import io
import sys
from datetime import date, timedelta
from main import FridgeSavvyApp
import subprocess
from pathlib import Path

MAIN = str(Path(__file__).resolve().parent / "main.py")

class TestFridgeSavvyIteration6(unittest.TestCase):
    """
    ITERATION 6: Edge Cases - Command Validation
    Focus: Argument validation and error handling
    Expected Coverage: ~88-92% branch coverage
    Includes all tests from Iterations 1-5 plus validation edge cases
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
    # FROM ITERATIONS 1-5
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

    def test_F1_no_recipes(self):
        out, _ = self.run_cmds(["suggest recipes"])
        self.assertIn("No recipes available", out)

    def test_F3_recipe_suggested(self):
        today = date.today()
        future = today + timedelta(days=5)
        out, _ = self.run_cmds([
            "add Tomato Veg %s" % future,
            "create recipe Pasta",
            "add ingredient Pasta Tomato 1 g",
            "suggest recipes"
        ])
        self.assertIn("Pasta", out)

    def test_F4_recipe_not_suggested_missing_ing(self):
        out, _ = self.run_cmds([
            "create recipe Pasta",
            "add ingredient Pasta Tomato 1 g",
            "suggest recipes"
        ])
        self.assertIn("Pantry is empty or all items are expired. No recipe suggestions.", out)

    def test_G1_no_plans(self):
        out, _ = self.run_cmds(["generate list"])
        self.assertIn("Shopping list is empty.", out)

    def test_G2_no_recipes_defined(self):
        out, _ = self.run_cmds([
            "plan Soup 2025-10-10"
        ])
        self.assertIn("Recipe 'Soup' does not exist", out)

    def test_G4_missing_ingredient(self):
        out, _ = self.run_cmds([
            "create recipe Pasta",
            "add ingredient Pasta Tomato 2 g",
            "plan Pasta 2025-10-10",
            "generate list"
        ])
        self.assertIn("Tomato", out)

    def test_H1_unknown_command(self):
        out, _ = self.run_cmds(["foobar"])
        self.assertIn("Unknown command", out)

    def test_A2_add_invalid_date(self):
        out, _ = self.run_cmds(["add Milk Dairy WRONG"])
        self.assertIn("Invalid date", out)

    # --------------------------
    # NEW IN ITERATION 6
    # Edge Cases - Command Validation
    # --------------------------

    def test_I2_add_missing_arguments(self):
        """Covers incomplete 'add' command."""
        out, _ = self.run_cmds(["add"])
        self.assertIn("Incomplete 'add' command", out)

    def test_I2_add_wrong_arguments(self):
        """Covers invalid quantity argument."""
        out, _ = self.run_cmds([
            "create recipe Crepes",
            "add ingredient Crepes Egg Two Unit"
        ])
        self.assertIn("Expected a number.", out)

    def test_I2_add_pantry_wrong_arg_count(self):
        """Covers wrong number of tokens."""
        out, _ = self.run_cmds(["add Milk Dairy"])
        self.assertIn("Usage: add ", out)

    def test_I2_add_ingredient_wrong_arg_count(self):
        """Covers empty command."""
        out, _ = self.run_cmds([""])
        self.assertIn("Enter a command", out)

    def test_I2_add_ingredient_too_many_args(self):
        """Covers too many arguments."""
        out, _ = self.run_cmds(["add ingredient R I Q U More"])
        self.assertIn("Usage: add ingredient ", out)

    def test_I2_remove_no_arguments(self):
        """Covers 'remove' with no args."""
        out, _ = self.run_cmds(["remove"])
        self.assertIn("Incomplete 'remove' command", out)

    def test_I2_remove_too_many_args(self):
        """Covers 'remove' with extra args."""
        out, _ = self.run_cmds(["remove egg bread"])
        self.assertIn("Usage: ", out)

    def test_I2_remove_recipe_missing_name(self):
        """Covers 'remove recipe' missing recipe name."""
        out, _ = self.run_cmds(["remove recipe"])
        self.assertIn("Usage: remove recipe", out)

    def test_I2_remove_ingredient_missing_name(self):
        """Covers 'remove ingredient' missing ingredient name."""
        out, _ = self.run_cmds(["remove ingredient R"])
        self.assertIn("Usage: remove ingredient", out)

    def test_I2_remove_ingredient_wrong_recipe_name(self):
        """Covers 'remove ingredient' missing recipe."""
        out, _ = self.run_cmds(["remove ingredient R egg"])
        self.assertIn("No recipe named", out)

    def test_I2_create_wrong_usage(self):
        """Covers create without 'recipe' keyword."""
        out, _ = self.run_cmds(["create"])
        self.assertIn("Usage: create recipe", out)

    def test_I2_create_recipe_missing_name(self):
        """Covers 'create recipe' missing name."""
        out, _ = self.run_cmds(["create recipe"])
        self.assertIn("Usage: create recipe", out)

    def test_I2_plan_missing_arguments(self):
        """Covers 'plan' missing date."""
        out, _ = self.run_cmds(["plan Soup"])
        self.assertIn("Usage: plan", out)

    def test_I2_plan_invalid_date(self):
        """Covers invalid date parsing in 'plan'."""
        out, _ = self.run_cmds([
            "create recipe Soup",
            "plan Soup abc"
        ])
        self.assertIn("Invalid date", out)

    def test_I2_unplan_missing_arguments(self):
        """Covers 'unplan' missing date."""
        out, _ = self.run_cmds(["unplan Soup"])
        self.assertIn("Usage: unplan", out)

    def test_I2_unplan_invalid_date(self):
        """Covers invalid date in unplan."""
        out, _ = self.run_cmds(["unplan Soup bad-date"])
        self.assertIn("Invalid date", out)

if __name__ == "__main__":
    unittest.main()
