# Godot Scene

## Nodes
- **FlappyBirdGame** (Node2D)
  - **Floor** (StaticBody2D)
    - **CollisionShape2D** (CollisionShape2D)
    - **ColorRect** (ColorRect)
  - **Camera2D** (Camera2D)
  - **Player** (CharacterBody2D)
    - script: res://flappy_bird_clone/scripts/player.gd
    - settings: res://flappy_bird_clone/default_settings.tres
    - **Sprite2D** (Sprite2D)
    - **CollisionShape2D** (CollisionShape2D)
  - **Obstacle** (res://flappy_bird_clone/obstacle_full.tscn, instanced scene)
  - **Obstacle2** (res://flappy_bird_clone/obstacle_full.tscn, instanced scene)
  - **Obstacle3** (res://flappy_bird_clone/obstacle_full.tscn, instanced scene)
  - **Obstacle4** (res://flappy_bird_clone/obstacle_full.tscn, instanced scene)
  - **Obstacle5** (res://flappy_bird_clone/obstacle_full.tscn, instanced scene)
  - **Obstacle6** (res://flappy_bird_clone/obstacle_full.tscn, instanced scene)
  - **ScreenEdgeCollider** (Area2D)
    - **CollisionShape2D** (CollisionShape2D)

## Connections
