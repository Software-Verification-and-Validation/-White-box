import unittest
import io
import sys
from datetime import date, timedelta
from main import FridgeSavvyApp
import subprocess
from pathlib import Path

MAIN = str(Path(__file__).resolve().parent / "main.py")

class TestFridgeSavvyIteration8(unittest.TestCase):
    """
    ITERATION 8: Final Push for 100% Coverage
    Expected Coverage: ~97-100% branch coverage
    Includes all 66 tests from Iteration 7 + 7 new targeted tests
    Target: Lines 653, 704-718, 722 (main function and edge cases)
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
    # ALL TESTS FROM ITERATION 7
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

    def test_I2_list_invalid_subcommand(self):
        out, _ = self.run_cmds(["list wrong"])
        self.assertIn("Unknown 'list' command", out)

    def test_I2_list_recipe_wrong_usage(self):
        out, _ = self.run_cmds(["list recipe"])
        self.assertIn("Usage: list recipe", out)

    def test_I2_list_expiring_too_many_args(self):
        out, _ = self.run_cmds(["list expiring now"])
        self.assertIn("Usage: list expiring", out)

    def test_I2_list_too_few_args(self):
        out, _ = self.run_cmds(["list"])
        self.assertIn("Usage: list pantry |", out)

    def test_I2_list_pantry_too_many_args(self):
        out, _ = self.run_cmds(["list pantry pantry"])
        self.assertIn("Usage: list pantry", out)

    def test_I2_list_pantry(self):
        out, _ = self.run_cmds([
            "add Milk Dairy 2025-11-01",
            "list pantry"
        ])
        self.assertIn("Milk (Dairy) – Expires 2025-11-01", out)

    def test_I2_list_recipe(self):
        out, _ = self.run_cmds([
            "create recipe Soup",
            "add ingredient Soup tomato 1 unit",
            "list recipe Soup"
        ])
        self.assertIn("tomato – 1.0 unit", out)

    def test_I2_list_expiring(self):
        date_today = FridgeSavvyApp()._today()
        out, _ = self.run_cmds([
            f"add Milk Dairy {date_today}",
            "list expiring"
        ])
        self.assertIn("Milk (Dairy) – Expires", out)

    def test_I2_suggest_wrong_usage_missing_keyword(self):
        out, _ = self.run_cmds(["suggest"])
        self.assertIn("Usage: suggest recipes", out)

    def test_I2_suggest_wrong_usage_recipe(self):
        out, _ = self.run_cmds(["suggest recipe"])
        self.assertIn("Usage: suggest recipes", out)

    def test_I2_suggest_recipe_empty_ingredient_list(self):
        out, _ = self.run_cmds([
            "create recipe EmptyStar",
            "add Egg Dairy 2099-01-01",
            "suggest recipes"
        ])
        self.assertIn("No recipes can be fully prepared with current pantry items.", out)

    def test_I2_suggest_recipe_loop(self):
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
        out, _ = self.run_cmds(["generate"])
        self.assertIn("Usage: generate list", out)

    def test_I2_generate_wrong_usage_extra_args(self):
        out, _ = self.run_cmds(["generate list extra"])
        self.assertIn("Usage: generate list", out)

    def test_I2_generate_list_meal_plan_but_recipe_missing(self):
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
        out, app = self.run_cmds([
            "generate list"
        ])
        self.assertIn("No recipes defined. Shopping list is empty.", out)

    def test_I2_no_missing_ingredient(self):
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
        out, _ = self.run_cmds([
            "add Milk Dairy 2025-11-01",
            "add Bread Bakery 2025-11-11",
            "add Tomato Vegetables 2025-11-12",
            "remove Bread"
        ])
        self.assertIn("Removed item", out)

    def test_I2_unplan_boucle(self):
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
        out, _ = self.run_cmds(["blablabla"])
        self.assertIn("Unknown command", out)

    def test_startup_banner(self):
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

    # --------------------------
    # NEW IN ITERATION 8
    # Final 3% Coverage - Targeting lines 653, 704-718, 722
    # --------------------------

    def test_I8_all_ingredients_available_no_shopping_needed(self):
        """Covers lines 678-693: All planned ingredients already in pantry."""
        today = date.today()
        future = today + timedelta(days=30)
        out, _ = self.run_cmds([
            "create recipe Pasta",
            "add ingredient Pasta Tomato 200 g",
            "add ingredient Pasta Cheese 50 g",
            "add Tomato Vegetable " + str(future),
            "add Cheese Dairy " + str(future),
            "plan Pasta 2025-12-10",
            "generate list"
        ])
        self.assertIn("All planned ingredients are already available", out)

    def test_I8_generate_list_with_recipe_no_ingredients(self):
        """Covers lines 636-637: Planned recipe exists but has no ingredients."""
        out, _ = self.run_cmds([
            "create recipe EmptyRecipe",
            "plan EmptyRecipe 2025-12-10",
            "generate list"
        ])
        # Empty recipe should not break the system
        self.assertTrue("Shopping list is empty" in out or "No shopping needed" in out or "missing ingredients" in out)

    def test_I8_multiple_ingredients_mixed_availability(self):
        """Covers line 653 and shopping list accumulation."""
        today = date.today()
        future = today + timedelta(days=30)
        out, _ = self.run_cmds([
            "create recipe Salad",
            "add ingredient Salad Lettuce 1 head",
            "add ingredient Salad Tomato 2 unit",
            "add Lettuce Vegetable " + str(future),
            "plan Salad 2025-12-10",
            "generate list"
        ])
        # Check shopping list specifically
        self.assertIn("Tomato", out)
        # Verify Lettuce is NOT in the shopping list section
        shopping_list_section = out.split("Shopping list")[1] if "Shopping list" in out else out
        self.assertNotIn("Lettuce –", shopping_list_section)

    def test_I8_main_function_with_eof(self):
        """Covers lines 704-722: Main function interactive loop with EOF."""
        proc = subprocess.Popen(
            [sys.executable, MAIN],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        out, err = proc.communicate("")
        self.assertIn("FridgeSavvy", out)

    def test_I8_main_function_normal_command(self):
        """Covers lines 704-722: Main function with normal command execution."""
        proc = subprocess.Popen(
            [sys.executable, MAIN],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        out, err = proc.communicate("help\nexit\n")
        self.assertIn("Available commands", out)
        self.assertIn("Goodbye", out)

    def test_I8_suggest_with_expired_items(self):
        """Covers lines 581-607: Suggest recipes with mix of expired and valid items."""
        today = date.today()
        past = today - timedelta(days=10)  # Clearly expired
        future = today + timedelta(days=30)  # Clearly valid
        out, _ = self.run_cmds([
            "add Egg Dairy " + str(past),
            "add Tomato Vegetable " + str(future),
            "create recipe Omelette",
            "add ingredient Omelette Egg 2 unit",
            "create recipe Salad",
            "add ingredient Salad Tomato 1 unit",
            "suggest recipes"
        ])
        # Should only suggest Salad (has valid Tomato), not Omelette (has expired Egg)
        self.assertIn("Salad", out)
        # Check that Omelette is not in the suggestions section
        if "You can prepare the following recipes" in out:
            suggestions_section = out.split("You can prepare the following recipes")[1]
            self.assertNotIn("Omelette", suggestions_section)

    def test_I8_recipe_with_multiple_ingredients_partial_match(self):
        """Covers line 614: Recipe matching logic with partial ingredients."""
        today = date.today()
        future = today + timedelta(days=5)
        out, _ = self.run_cmds([
            "add Tomato Vegetable " + str(future),
            "create recipe ComplexPasta",
            "add ingredient ComplexPasta Tomato 1 unit",
            "add ingredient ComplexPasta Cheese 1 unit",
            "add ingredient ComplexPasta Pasta 1 unit",
            "suggest recipes"
        ])
        self.assertIn("No recipes can be fully prepared", out)

if __name__ == "__main__":
    unittest.main()
