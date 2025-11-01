# Shunting yard algorithm implemented in rust :D

~ and visualized using manim (python) :D

## Building:

```sh
cargo build
```

or

```sh
cargo run -- "3 + 4 * 2 / ( 1 - 5 ) ^ 2"
```

to directly run

## Generating visualization:

```sh
manim -pql shunting_yard.py ShuntingYardVisualization
```
