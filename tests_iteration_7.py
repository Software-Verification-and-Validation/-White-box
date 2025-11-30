import unittest
import io
import sys
from datetime import date, timedelta
from main import FridgeSavvyApp
import subprocess
from pathlib import Path

MAIN = str(Path(__file__).resolve().parent / "main.py")

class TestFridgeSavvyIteration7(unittest.TestCase):
    """
    ITERATION 7: Edge Cases - List Commands & Loops
    Focus: Remaining branches in list commands and loop iterations
    Expected Coverage: ~98-100% branch coverage
    Includes all tests from Iterations 1-6 plus final edge cases
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
    # FROM ITERATIONS 1-6
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

    def test_I2_add_missing_arguments(self):
        out, _ = self.run_cmds(["add"])
        self.assertIn("Incomplete 'add' command", out)

    def test_I2_add_wrong_arguments(self):
        out, _ = self.run_cmds([
            "create recipe Crepes",
            "add ingredient Crepes Egg Two Unit"
        ])
        self.assertIn("Expected a number.", out)

    def test_I2_add_pantry_wrong_arg_count(self):
        out, _ = self.run_cmds(["add Milk Dairy"])
        self.assertIn("Usage: add ", out)

    def test_I2_add_ingredient_wrong_arg_count(self):
        out, _ = self.run_cmds([""])
        self.assertIn("Enter a command", out)

    def test_I2_add_ingredient_too_many_args(self):
        out, _ = self.run_cmds(["add ingredient R I Q U More"])
        self.assertIn("Usage: add ingredient ", out)

    def test_I2_remove_no_arguments(self):
        out, _ = self.run_cmds(["remove"])
        self.assertIn("Incomplete 'remove' command", out)

    def test_I2_remove_too_many_args(self):
        out, _ = self.run_cmds(["remove egg bread"])
        self.assertIn("Usage: ", out)

    def test_I2_remove_recipe_missing_name(self):
        out, _ = self.run_cmds(["remove recipe"])
        self.assertIn("Usage: remove recipe", out)

    def test_I2_remove_ingredient_missing_name(self):
        out, _ = self.run_cmds(["remove ingredient R"])
        self.assertIn("Usage: remove ingredient", out)

    def test_I2_remove_ingredient_wrong_recipe_name(self):
        out, _ = self.run_cmds(["remove ingredient R egg"])
        self.assertIn("No recipe named", out)

    def test_I2_create_wrong_usage(self):
        out, _ = self.run_cmds(["create"])
        self.assertIn("Usage: create recipe", out)

    def test_I2_create_recipe_missing_name(self):
        out, _ = self.run_cmds(["create recipe"])
        self.assertIn("Usage: create recipe", out)

    def test_I2_plan_missing_arguments(self):
        out, _ = self.run_cmds(["plan Soup"])
        self.assertIn("Usage: plan", out)

    def test_I2_plan_invalid_date(self):
        out, _ = self.run_cmds([
            "create recipe Soup",
            "plan Soup abc"
        ])
        self.assertIn("Invalid date", out)

    def test_I2_unplan_missing_arguments(self):
        out, _ = self.run_cmds(["unplan Soup"])
        self.assertIn("Usage: unplan", out)

    def test_I2_unplan_invalid_date(self):
        out, _ = self.run_cmds(["unplan Soup bad-date"])
        self.assertIn("Invalid date", out)

    # --------------------------
    # NEW IN ITERATION 7
    # Final Edge Cases & Loops
    # --------------------------

    def test_I2_list_invalid_subcommand(self):
        """Covers list invalid type."""
        out, _ = self.run_cmds(["list wrong"])
        self.assertIn("Unknown 'list' command", out)

    def test_I2_list_recipe_wrong_usage(self):
        """Covers list recipe wrong usage."""
        out, _ = self.run_cmds(["list recipe"])
        self.assertIn("Usage: list recipe", out)

    def test_I2_list_expiring_too_many_args(self):
        """Covers 'list expiring' with extra args."""
        out, _ = self.run_cmds(["list expiring now"])
        self.assertIn("Usage: list expiring", out)

    def test_I2_list_too_few_args(self):
        """Covers list with no subcommand."""
        out, _ = self.run_cmds(["list"])
        self.assertIn("Usage: list pantry |", out)

    def test_I2_list_pantry_too_many_args(self):
        """Covers list pantry with extra args."""
        out, _ = self.run_cmds(["list pantry pantry"])
        self.assertIn("Usage: list pantry", out)

    def test_I2_list_pantry(self):
        """Covers list pantry with items."""
        out, _ = self.run_cmds([
            "add Milk Dairy 2025-11-01",
            "list pantry"
        ])
        self.assertIn("Milk (Dairy) – Expires 2025-11-01", out)

    def test_I2_list_recipe(self):
        """Covers list recipe with ingredients."""
        out, _ = self.run_cmds([
            "create recipe Soup",
            "add ingredient Soup tomato 1 unit",
            "list recipe Soup"
        ])
        self.assertIn("tomato – 1.0 unit", out)

    def test_I2_list_expiring(self):
        """Covers list expiring with items."""
        date = FridgeSavvyApp()._today()
        out, _ = self.run_cmds([
            f"add Milk Dairy {date}",
            "list expiring"
        ])
        self.assertIn("Milk (Dairy) – Expires", out)

    def test_I2_suggest_wrong_usage_missing_keyword(self):
        """Covers suggest alone."""
        out, _ = self.run_cmds(["suggest"])
        self.assertIn("Usage: suggest recipes", out)

    def test_I2_suggest_wrong_usage_recipe(self):
        """Covers suggest recipe wrong usage."""
        out, _ = self.run_cmds(["suggest recipe"])
        self.assertIn("Usage: suggest recipes", out)

    def test_I2_suggest_recipe_empty_ingredient_list(self):
        """Covers recipe with no ingredients should not be suggested."""
        out, _ = self.run_cmds([
            "create recipe EmptyStar",
            "add Egg Dairy 2099-01-01",
            "suggest recipes"
        ])
        self.assertIn("No recipes can be fully prepared with current pantry items.", out)

    def test_I2_suggest_recipe_loop(self):
        """Covers multiple recipe suggestions."""
        out, _ = self.run_cmds([
            "create recipe Tortilla",
            "create recipe Cake",
            "create recipe Snails",
            "add ingredient Cake Egg 3 unit",
            "add ingredient Tortilla Potatoes 4 kg",
            "add ingredient Tortilla Egg 4 unit",
            "add Egg Dairy 2099-01-01",
            "suggest recipes"
        ])
        self.assertIn("You can prepare the following recipes with your current pantry:\n- Cake", out)

    def test_I2_generate_wrong_usage_missing_keyword(self):
        """Covers 'generate' alone."""
        out, _ = self.run_cmds(["generate"])
        self.assertIn("Usage: generate list", out)

    def test_I2_generate_wrong_usage_extra_args(self):
        """Covers 'generate list' extra tokens."""
        out, _ = self.run_cmds(["generate list extra"])
        self.assertIn("Usage: generate list", out)

    def test_I2_generate_list_meal_plan_but_recipe_missing(self):
        """Covers planned recipe removed before generating list."""
        out, app = self.run_cmds([
            "create recipe Pasta",
            "create recipe Soup",
            "add ingredient Pasta Tomato 2 g",
            "plan Pasta 2025-10-10",
            "remove recipe Pasta",
            "generate list"
        ])
        self.assertIn("No meals planned. Shopping list is empty.", out)

    def test_I2_generate_list_no_recipe(self):
        """Covers generating list but without any recipe."""
        out, app = self.run_cmds([
            "generate list"
        ])
        self.assertIn("No recipes defined. Shopping list is empty.", out)

    def test_I2_no_missing_ingredient(self):
        """Covers all ingredients available."""
        out, _ = self.run_cmds([
            "create recipe Pasta",
            "add ingredient Pasta Tomato 2 g",
            "add ingredient Pasta Butter 50 g",
            "add Butter Dairy 2025-12-01",
            "add Tomato Vegetable 2025-12-03",
            "plan Pasta 2025-10-10",
            "generate list"
        ])
        self.assertIn("Tomato", out)

    def test_I2_remove_when_several_itemsin_the_pantry(self):
        """Covers loop in remove when multiple items."""
        out, _ = self.run_cmds([
            "add Milk Dairy 2025-11-01",
            "add Bread Bakery 2025-11-11",
            "add Tomato Vegetables 2025-11-12",
            "remove Bread"
        ])
        self.assertIn("Removed item", out)

    def test_I2_unplan_boucle(self):
        """Covers loop in unplan."""
        out, _ = self.run_cmds([
            "create recipe Soup",
            "create recipe Cake",
            "create recipe Snails",
            "plan Soup 2025-11-28",
            "plan Cake 2025-11-15",
            "plan Snails 2025-12-01",
            "unplan Cake 2025-11-15"
        ])
        self.assertIn("Removed planned recipe", out)

    def test_I2_unknown_full_command(self):
        """Covers default case in handle_command for unknown commands."""
        out, _ = self.run_cmds(["blablabla"])
        self.assertIn("Unknown command", out)

    def test_startup_banner(self):
        """Tests that running main.py prints the startup banner."""
        proc = subprocess.Popen(
            [sys.executable, MAIN],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        out, err = proc.communicate("exit\n")
        self.assertIn("FridgeSavvy – Smart kitchen inventory", out)
        self.assertIn("Type 'help' to see available commands.", out)

if __name__ == "__main__":
    unittest.main()
