## run-godot-game

This script helps you quickly run your Godot game from the command line using `uv`. It assumes you have `uv` installed and configured.

### Usage

1.  Ensure the script is executable if necessary (e.g., for a Python script).
2.  Configure a task in VS Code to run the game.

### VS Code Integration (tasks.json)

You can integrate `run-godot-game` into your VS Code workflow using a `tasks.json` file. This allows you to run the game with a simple command or keybinding (like F5).

Here's an example `tasks.json` configuration:

```jsonc
{
    // See https://go.microsoft.com/fwlink/?LinkId=733558
    // for the documentation about the tasks.json format
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run Godot Game",
            "type": "shell",
            "command": "uv run c:/GithubRepos/Test/run-godot-game.py",
            "problemMatcher": [],
            "group": {
              "kind": "build",
              "isDefault": true
            }
        }
    ]
}
```
**Explanation:**

*   `label`: A descriptive name for the task.
*   `type`: Specifies the task type (in this case, a shell command).
*   `command`: The command to execute. This example uses `uv run` to execute a Python script named `run-godot-game.py` located in `c:/GithubRepos/Test/`. **Important:** Adjust the path to `run-godot-game.py` to match your actual file location.
*   `problemMatcher`: Used for parsing compiler errors. It's empty here, but you can configure it to parse Godot's output if needed.
*   `group`: Defines the task's group. Setting `isDefault` to `true` in the `"build"` group makes this task the default build task, which can be run with `Ctrl+Shift+B` (or `Cmd+Shift+B` on macOS).

**Keybinding (F5):**

To bind this task to the F5 key:

1.  Open VS Code's keyboard shortcuts settings (`File > Preferences > Keyboard Shortcuts` or `Ctrl+K Ctrl+S`).
2.  Click the "Open Keyboard Shortcuts (JSON)" icon in the top right corner.
3.  Add the following entry to your `keybindings.json` file:
```
[
    {
        "key": "f5",
        "command": "workbench.action.tasks.runTask",
        "args": "Run Godot Game",
        "when": "editorTextFocus"
    }
]
```
This will execute the task labeled "Run Godot Game" when you press F5. Make sure the label in `keybindings.json` matches the `label` in your `tasks.json` file.

**Important Considerations:**

*   **Paths:** Ensure that the paths in `tasks.json` and `keybindings.json` are correct for your system and project structure.
*   **uv:** This setup assumes you are using `uv` to run your script. If you're using a different method (e.g., directly calling `python`), adjust the `command` accordingly.
*   **Error Handling:** The provided `tasks.json` doesn't include error handling. You might want to add a `problemMatcher` to parse Godot's output and display errors in VS Code.