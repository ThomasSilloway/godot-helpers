# Godot Scene

## Nodes
- **MainMenu**
  - **ColorRect**
  - **Title**
    - text: "Game Title"
  - **VBoxContainer**
    - **Button_Play**
      - text: "Play"
    - **Button_Exit**
      - text: "Exit"

## Connections
- When signal 'pressed' is emitted from 'VBoxContainer/Button_Play', call method '_play' on 'MainMenu'.
- When signal 'pressed' is emitted from 'VBoxContainer/Button_Exit', call method '_quit' on 'MainMenu'.
