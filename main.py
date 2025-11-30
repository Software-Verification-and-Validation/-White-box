"""
FridgeSavvy - Smart kitchen inventory and meal planning assistant
=================================================================

This module implements a simple command-line version of the FridgeSavvy
application as described in the specification.

The program:

* Keeps all data in memory (no databases, no external APIs).
* Accepts commands from standard input (interactive mode) or from a text file.
* Prints human-readable responses to standard output.

Usage
-----

Interactive mode::

    python main.py

Then type commands one per line, for example::

    add Milk Dairy 2025-11-01
    create recipe Pasta
    add ingredient Pasta TomatoSauce 200 ml
    list pantry
    suggest recipes
    exit

Running commands from a file::

    python main.py commands.txt

Where ``commands.txt`` contains one command per line, e.g.::

    add Milk Dairy 2025-11-01
    create recipe Pasta
    add ingredient Pasta Pasta 150 g
    add ingredient Pasta Cheese 50 g
    list recipe Pasta
    plan Pasta 2025-11-03
    generate list

Commands
--------

The following commands are implemented (case-sensitive, single spaces):

* ``add <ItemName> <Category> <ExpiryDate>``
* ``remove <ItemName>``
* ``create recipe <RecipeName>``
* ``remove recipe <RecipeName>``
* ``add ingredient <RecipeName> <IngredientName> <Quantity> <Unit>``
* ``remove ingredient <RecipeName> <IngredientName>``
* ``plan <RecipeName> <Date>``
* ``unplan <RecipeName> <Date>``
* ``list pantry``
* ``list recipe <RecipeName>``
* ``list expiring``
* ``suggest recipes``
* ``generate list``
* ``help`` – show a short help summary
* ``exit`` or ``quit`` – terminate the program

Notes
-----

* Dates are in ``YYYY-MM-DD`` format.
* All data is stored in memory only and is lost when the program exits.
* Item names, recipe names and ingredient names are treated as single words
  (no spaces), as illustrated by the examples in the specification.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Dict, List, TextIO, Tuple


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class PantryItem:
    """Represents a single item stored in the digital pantry.

    Attributes
    ----------
    name:
        The item name, e.g. ``"Milk"``.
    category:
        The category of the item, e.g. ``"Dairy"``.
    expiry:
        Expiration date as a :class:`datetime.date` object.
    """

    name: str
    category: str
    expiry: date


@dataclass
class Ingredient:
    """Represents a single ingredient belonging to a recipe.

    Attributes
    ----------
    name:
        Ingredient name, e.g. ``"TomatoSauce"``.
    quantity:
        Numeric quantity required (stored as ``float``).
    unit:
        Unit of measurement, e.g. ``"ml"``, ``"g"``, ``"head"``.
    """

    name: str
    quantity: float
    unit: str


@dataclass
class MealPlanEntry:
    """Represents a planned recipe on a certain date.

    Attributes
    ----------
    recipe_name:
        Name of the recipe, which must exist in the recipe collection.
    scheduled_date:
        Date when the recipe is planned.
    """

    recipe_name: str
    scheduled_date: date


class FridgeSavvyApp:
    """Encapsulates the in-memory state and command handling logic.

    The class maintains:

    * A list of pantry items.
    * A mapping from recipe name to ingredients.
    * A list of meal plan entries.

    Each public method whose name starts with ``do_`` corresponds to a
    supported command and is invoked by :meth:`handle_command`.
    """

    def __init__(self) -> None:
        # In-memory storage (no database, no files, no external APIs).
        self.pantry: List[PantryItem] = []
        self.recipes: Dict[str, Dict[str, Ingredient]] = {}
        self.meal_plan: List[MealPlanEntry] = []

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_date(value: str) -> date:
        """Parse a ``YYYY-MM-DD`` date string.

        Raises
        ------
        ValueError
            If the string is not a valid date in the expected format.
        """
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(
                f"Invalid date '{value}'. Expected format: YYYY-MM-DD."
            ) from exc

    @staticmethod
    def _parse_quantity(value: str) -> float:
        """Parse a numeric quantity into a float.

        The implementation accepts both integer and decimal numbers.

        Raises
        ------
        ValueError
            If the value cannot be converted to a number.
        """
        try:
            return float(value)
        except ValueError as exc:
            raise ValueError(f"Invalid quantity '{value}'. Expected a number.") from exc

    @staticmethod
    def _today() -> date:
        """Return today's date.

        Implemented as a separate method to make testing easier.
        """
        return date.today()

    # ------------------------------------------------------------------
    # Command dispatch
    # ------------------------------------------------------------------

    def handle_command(self, line: str) -> bool:
        """Parse and execute a single command line.

        Parameters
        ----------
        line:
            The raw command line entered by the user.

        Returns
        -------
        bool
            ``True`` if the program should continue running,
            ``False`` if an ``exit`` or ``quit`` command was processed.

        Notes
        -----
        * Commands are case-sensitive.
        * Words are separated by single spaces as specified.
        """
        stripped = line.strip()
        if not stripped:
            # Empty line: ignore and keep running.
            print("Enter a command")
            return True

        tokens = stripped.split(" ")

        # Exit commands -------------------------------------------------
        if tokens[0] in {"exit", "quit"}:
            print("Goodbye!")
            return False

        # Help command --------------------------------------------------
        if tokens[0] == "help":
            self.print_help()
            return True

        try:
            if tokens[0] == "add":
                self._handle_add(tokens)
            elif tokens[0] == "remove":
                self._handle_remove(tokens)
            elif tokens[0] == "create":
                self._handle_create(tokens)
            elif tokens[0] == "plan":
                self._handle_plan(tokens)
            elif tokens[0] == "unplan":
                self._handle_unplan(tokens)
            elif tokens[0] == "list":
                self._handle_list(tokens)
            elif tokens[0] == "suggest":
                self._handle_suggest(tokens)
            elif tokens[0] == "generate":
                self._handle_generate(tokens)
            else:
                print(f"Error: Unknown command '{tokens[0]}'. Type 'help' for a list of commands.")
        except ValueError as exc:
            # Any parsing-related error is shown to the user in a friendly manner.
            print(f"Error: {exc}")

        return True

    # ------------------------------------------------------------------
    # Command handlers
    # ------------------------------------------------------------------

    # ADD -------------------------------------------------------------

    def _handle_add(self, tokens: List[str]) -> None:
        """Handle all ``add ...`` commands."""
        if len(tokens) < 2:
            raise ValueError("Incomplete 'add' command.")

        if tokens[1] == "ingredient":
            self.do_add_ingredient(tokens)
        else:
            self.do_add_pantry_item(tokens)

    def do_add_pantry_item(self, tokens: List[str]) -> None:
        """Implementation of::

            add <ItemName> <Category> <ExpiryDate>
        """
        if len(tokens) != 4:
            raise ValueError("Usage: add <ItemName> <Category> <ExpiryDate>")

        _, item_name, category, expiry_str = tokens
        expiry = self._parse_date(expiry_str)
        self.pantry.append(PantryItem(name=item_name, category=category, expiry=expiry))
        print(f"Added item '{item_name}' in category '{category}' with expiry {expiry}.")

    def do_add_ingredient(self, tokens: List[str]) -> None:
        """Implementation of::

            add ingredient <RecipeName> <IngredientName> <Quantity> <Unit>
        """
        if len(tokens) != 6:
            raise ValueError(
                "Usage: add ingredient <RecipeName> <IngredientName> <Quantity> <Unit>"
            )

        _, _, recipe_name, ingredient_name, quantity_str, unit = tokens

        if recipe_name not in self.recipes:
            raise ValueError(f"Recipe '{recipe_name}' does not exist. Create it first.")

        quantity = self._parse_quantity(quantity_str)
        ingredient = Ingredient(
            name=ingredient_name,
            quantity=quantity,
            unit=unit,
        )
        # Replace or add ingredient
        self.recipes[recipe_name][ingredient_name] = ingredient
        print(
            f"Added ingredient '{ingredient_name}' to recipe '{recipe_name}': "
            f"{quantity} {unit}."
        )

    # REMOVE ----------------------------------------------------------

    def _handle_remove(self, tokens: List[str]) -> None:
        """Handle all ``remove ...`` commands."""
        if len(tokens) < 2:
            raise ValueError("Incomplete 'remove' command.")

        if tokens[1] == "ingredient":
            self.do_remove_ingredient(tokens)
        elif tokens[1] == "recipe":
            self.do_remove_recipe(tokens)
        else:
            self.do_remove_pantry_item(tokens)

    def do_remove_pantry_item(self, tokens: List[str]) -> None:
        """Implementation of::

            remove <ItemName>

        Removes *one* matching item from the pantry (the earliest added).
        """
        if len(tokens) != 2:
            raise ValueError("Usage: remove <ItemName>")

        _, item_name = tokens
        for idx, item in enumerate(self.pantry):
            if item.name == item_name:
                del self.pantry[idx]
                print(f"Removed item '{item_name}' from pantry.")
                return

        print(f"No pantry item named '{item_name}' found.")

    def do_remove_recipe(self, tokens: List[str]) -> None:
        """Implementation of::

            remove recipe <RecipeName>
        """
        if len(tokens) != 3:
            raise ValueError("Usage: remove recipe <RecipeName>")

        _, _, recipe_name = tokens
        if recipe_name not in self.recipes:
            print(f"No recipe named '{recipe_name}' found.")
            return

        # Remove the recipe
        del self.recipes[recipe_name]

        # Also remove any associated meal plan entries
        before = len(self.meal_plan)
        self.meal_plan = [
            entry for entry in self.meal_plan if entry.recipe_name != recipe_name
        ]
        removed_from_plan = before - len(self.meal_plan)

        msg = f"Removed recipe '{recipe_name}'."
        if removed_from_plan:
            msg += f" Also removed {removed_from_plan} planned occurrence(s)."
        print(msg)

    def do_remove_ingredient(self, tokens: List[str]) -> None:
        """Implementation of::

            remove ingredient <RecipeName> <IngredientName>
        """
        if len(tokens) != 4:
            raise ValueError("Usage: remove ingredient <RecipeName> <IngredientName>")

        _, _, recipe_name, ingredient_name = tokens

        if recipe_name not in self.recipes:
            print(f"No recipe named '{recipe_name}' found.")
            return

        ingredients = self.recipes[recipe_name]
        if ingredient_name in ingredients:
            del ingredients[ingredient_name]
            print(
                f"Removed ingredient '{ingredient_name}' from recipe '{recipe_name}'."
            )
        else:
            print(
                f"Recipe '{recipe_name}' has no ingredient named '{ingredient_name}'."
            )

    # CREATE ----------------------------------------------------------

    def _handle_create(self, tokens: List[str]) -> None:
        """Handle all ``create ...`` commands."""
        if len(tokens) < 2 or tokens[1] != "recipe":
            raise ValueError("Usage: create recipe <RecipeName>")
        self.do_create_recipe(tokens)

    def do_create_recipe(self, tokens: List[str]) -> None:
        """Implementation of::

            create recipe <RecipeName>
        """
        if len(tokens) != 3:
            raise ValueError("Usage: create recipe <RecipeName>")

        _, _, recipe_name = tokens

        if recipe_name in self.recipes:
            print(f"Recipe '{recipe_name}' already exists.")
            return

        self.recipes[recipe_name] = {}
        print(f"Created empty recipe '{recipe_name}'.")

    # PLAN / UNPLAN ---------------------------------------------------

    def _handle_plan(self, tokens: List[str]) -> None:
        """Implementation of::

            plan <RecipeName> <Date>
        """
        self.do_plan_recipe(tokens)

    def do_plan_recipe(self, tokens: List[str]) -> None:
        if len(tokens) != 3:
            raise ValueError("Usage: plan <RecipeName> <Date>")

        _, recipe_name, date_str = tokens
        if recipe_name not in self.recipes:
            raise ValueError(f"Recipe '{recipe_name}' does not exist.")

        scheduled_date = self._parse_date(date_str)
        self.meal_plan.append(MealPlanEntry(recipe_name=recipe_name, scheduled_date=scheduled_date))
        print(f"Planned recipe '{recipe_name}' on {scheduled_date}.")

    def _handle_unplan(self, tokens: List[str]) -> None:
        """Implementation of::

            unplan <RecipeName> <Date>
        """
        self.do_unplan_recipe(tokens)

    def do_unplan_recipe(self, tokens: List[str]) -> None:
        if len(tokens) != 3:
            raise ValueError("Usage: unplan <RecipeName> <Date>")

        _, recipe_name, date_str = tokens
        scheduled_date = self._parse_date(date_str)

        for idx, entry in enumerate(self.meal_plan):
            if entry.recipe_name == recipe_name and entry.scheduled_date == scheduled_date:
                del self.meal_plan[idx]
                print(f"Removed planned recipe '{recipe_name}' on {scheduled_date}.")
                return

        print(f"No planned recipe '{recipe_name}' on {scheduled_date} found.")

    # LIST ------------------------------------------------------------

    def _handle_list(self, tokens: List[str]) -> None:
        """Handle all ``list ...`` commands."""
        if len(tokens) < 2:
            raise ValueError("Usage: list pantry | list recipe <RecipeName> | list expiring")

        if tokens[1] == "pantry":
            self.do_list_pantry(tokens)
        elif tokens[1] == "recipe":
            self.do_list_recipe(tokens)
        elif tokens[1] == "expiring":
            self.do_list_expiring(tokens)
        else:
            raise ValueError("Unknown 'list' command. Use 'pantry', 'recipe', or 'expiring'.")

    def do_list_pantry(self, tokens: List[str]) -> None:
        """Implementation of::

            list pantry
        """
        if len(tokens) != 2:
            raise ValueError("Usage: list pantry")

        if not self.pantry:
            print("Pantry is empty.")
            return

        print("Pantry items:")
        # Sort by expiry date for convenience
        for item in sorted(self.pantry, key=lambda i: i.expiry):
            print(f"- {item.name} ({item.category}) – Expires {item.expiry}")

    def do_list_recipe(self, tokens: List[str]) -> None:
        """Implementation of::

            list recipe <RecipeName>
        """
        if len(tokens) != 3:
            raise ValueError("Usage: list recipe <RecipeName>")

        _, _, recipe_name = tokens
        if recipe_name not in self.recipes:
            print(f"No recipe named '{recipe_name}' found.")
            return

        ingredients = self.recipes[recipe_name]
        if not ingredients:
            print(f"Recipe '{recipe_name}' has no ingredients.")
            return

        print(f"Ingredients for recipe '{recipe_name}':")
        for ingredient in ingredients.values():
            print(f"{ingredient.name} – {ingredient.quantity} {ingredient.unit}")

    def do_list_expiring(self, tokens: List[str]) -> None:
        """Implementation of::

            list expiring

        Shows items expiring within 3 days from *today* (inclusive).
        """
        if len(tokens) != 2:
            raise ValueError("Usage: list expiring")

        today = self._today()
        cutoff = today + timedelta(days=3)

        expiring_items = [
            item for item in self.pantry
            if today <= item.expiry <= cutoff
        ]

        if not expiring_items:
            print("No items expiring within the next 3 days.")
            return

        print(f"Items expiring between {today} and {cutoff}:")
        for item in sorted(expiring_items, key=lambda i: i.expiry):
            days_left = (item.expiry - today).days
            print(f"- {item.name} ({item.category}) – Expires {item.expiry} (in {days_left} day(s))")

    # SUGGEST RECIPES -------------------------------------------------

    def _handle_suggest(self, tokens: List[str]) -> None:
        """Handle the ``suggest recipes`` command."""
        if len(tokens) != 2 or tokens[1] != "recipes":
            raise ValueError("Usage: suggest recipes")
        self.do_suggest_recipes()

    def do_suggest_recipes(self) -> None:
        """Suggest recipes based on current (non-expired) pantry contents.

        A recipe is suggested if **all** its ingredients are present in the
        pantry as non-expired items (ignoring quantities).

        This is a simple rule-based approximation replacing the external
        ChatGPT API mentioned in the original specification, since the
        current implementation must not use external resources.
        """
        if not self.recipes:
            print("No recipes available.")
            return

        today = self._today()
        available_items = {item.name for item in self.pantry if item.expiry >= today}

        if not available_items:
            print("Pantry is empty or all items are expired. No recipe suggestions.")
            return

        matching_recipes: List[str] = []

        for recipe_name, ingredients in self.recipes.items():
            if not ingredients:
                continue  # skip empty recipes
            ingredient_names = {ing.name for ing in ingredients.values()}
            if ingredient_names.issubset(available_items):
                matching_recipes.append(recipe_name)

        if not matching_recipes:
            print("No recipes can be fully prepared with current pantry items.")
            return

        print("You can prepare the following recipes with your current pantry:")
        for name in sorted(matching_recipes):
            print(f"- {name}")

    # GENERATE SHOPPING LIST -----------------------------------------

    def _handle_generate(self, tokens: List[str]) -> None:
        """Handle the ``generate list`` command."""
        if len(tokens) != 2 or tokens[1] != "list":
            raise ValueError("Usage: generate list")
        self.do_generate_list()

    def do_generate_list(self) -> None:
        """Generate a shopping list based on planned meals.

        Logic
        -----
        For each planned meal, we look at the recipe's ingredients.
        If an ingredient is **not** available in the pantry as a
        non-expired item (ignoring quantities), it is added to the
        shopping list.

        Quantities for the same ingredient (with the same unit) are
        summed across all planned meals.
        """
        
        if not self.recipes:
            print("No recipes defined. Shopping list is empty.")
            return
        
        if not self.meal_plan:
            print("No meals planned. Shopping list is empty.")
            return

        

        today = self._today()
        available_items = {item.name for item in self.pantry if item.expiry >= today}

        # Key: (ingredient_name, unit) -> total quantity
        required: Dict[Tuple[str, str], float] = {}

        for entry in self.meal_plan:
            recipe_name = entry.recipe_name
            ingredients = self.recipes.get(recipe_name)
            if not ingredients:
                # Should not happen if commands are used correctly,
                # but we handle it defensively.
                continue

            for ingredient in ingredients.values():
                if ingredient.name in available_items:
                    continue  # already available in pantry
                key = (ingredient.name, ingredient.unit)
                required[key] = required.get(key, 0.0) + ingredient.quantity

        if not required:
            print("All planned ingredients are already available in your pantry. "
                  "No shopping needed!")
            return

        print("Shopping list (missing ingredients for planned meals):")
        for (name, unit), qty in sorted(required.items(), key=lambda kv: kv[0][0]):
            # Remove insignificant decimals if quantity is effectively an integer
            qty_str = str(int(qty))
            print(f"- {name} – {qty_str} {unit}")

    # ------------------------------------------------------------------
    # Helper: help text
    # ------------------------------------------------------------------

    def print_help(self) -> None:
        """Print a concise list of supported commands."""
        print("Available commands:")
        print("  add <ItemName> <Category> <ExpiryDate>")
        print("  remove <ItemName>")
        print("  create recipe <RecipeName>")
        print("  remove recipe <RecipeName>")
        print("  add ingredient <RecipeName> <IngredientName> <Quantity> <Unit>")
        print("  remove ingredient <RecipeName> <IngredientName>")
        print("  plan <RecipeName> <Date>")
        print("  unplan <RecipeName> <Date>")
        print("  list pantry")
        print("  list recipe <RecipeName>")
        print("  list expiring")
        print("  suggest recipes")
        print("  generate list")
        print("  help")
        print("  exit | quit")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Program entry point (interactive mode only)."""

    print("FridgeSavvy – Smart kitchen inventory and meal planning assistant")
    print("Type 'help' to see available commands. Type 'exit' to quit.")

    app = FridgeSavvyApp()

    while True:
        try:
            line = input("> ")
        except EOFError:
            print("\nGoodbye!")
            break

        should_continue = app.handle_command(line)
        if not should_continue:
            break


if __name__ == "__main__":
    main()
