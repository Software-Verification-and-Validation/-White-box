# FridgeSavvy – Command-Line Implementation

This is a simple **Python** implementation of the program described in the
*FridgeSavvy – Smart kitchen inventory and meal planning assistant* specification.

All data is kept **in memory** using Python lists and dictionaries.
There are **no external dependencies**, no databases, and no APIs.

---

## Requirements

- Python **3.9** or newer.
- No third-party libraries are required.

---

## Files

- `main.py` – main program implementation.
- `sample_commands.txt` – example input file with a small scenario.

---

## How to Run

### 1. Interactive Mode

From a terminal in this folder:

```bash
python main.py
```

You will see a prompt like:

```text
FridgeSavvy – Smart kitchen inventory and meal planning assistant
Type 'help' to see available commands. Type 'exit' to quit.
> 
```

Now you can type commands, one per line. For example:

```text
add Milk Dairy 2025-11-01
create recipe Pasta
add ingredient Pasta TomatoSauce 200 ml
add ingredient Pasta Pasta 150 g
list pantry
list recipe Pasta
suggest recipes
exit
```

### 2. Run Commands from a File

You can also store commands in a text file (one command per line) and run them
in batch mode.

Example:

```bash
python main.py sample_commands.txt
```

The program will execute each line from `sample_commands.txt` and print the
results to the screen.

---

## Supported Commands

Commands are **case-sensitive** and use **single spaces** between arguments.

- `add <ItemName> <Category> <ExpiryDate>`
- `remove <ItemName>`
- `create recipe <RecipeName>`
- `remove recipe <RecipeName>`
- `add ingredient <RecipeName> <IngredientName> <Quantity> <Unit>`
- `remove ingredient <RecipeName> <IngredientName>`
- `plan <RecipeName> <Date>`
- `unplan <RecipeName> <Date>`
- `list pantry`
- `list recipe <RecipeName>`
- `list expiring`
- `suggest recipes`
- `generate list`
- `help`
- `exit` or `quit`

### Date Format

All dates must use the format:

```text
YYYY-MM-DD
```

Example: `2025-11-01`.

---

## Notes & Assumptions

- Item names, recipe names and ingredient names are treated as **single words**
  (no spaces), e.g. `TomatoSauce`, `Tomato_Sauce`, or `Tomato-Sauce`.
- For `list expiring`, the program shows items expiring **within 3 days**
  from *today* (inclusive).
- Recipe suggestions are based on a simple rule:
  a recipe is suggested if **all** its ingredients are present as
  **non-expired** items in the pantry (quantities are ignored).
- The shopping list is generated from all planned meals, and contains the
  ingredients that are **not currently available** in the pantry.

---

## Example Scenario (sample_commands.txt)

```text
add Milk Dairy 2025-11-01
add Cheese Dairy 2025-11-02
add TomatoSauce Vegetables 2025-11-03

create recipe Pasta
add ingredient Pasta Pasta 150 g
add ingredient Pasta TomatoSauce 200 ml
add ingredient Pasta Cheese 50 g

list pantry
list recipe Pasta
plan Pasta 2025-11-05
generate list
suggest recipes
list expiring
```

You can modify `sample_commands.txt` or create your own scenario files.
# -White-box
