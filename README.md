# Claude Store Assistant

A conversational command-line store assistant powered by [Claude](https://www.anthropic.com/) tool use. Ask it about products in plain English — prices, stock, quotes — and it can place orders, calling real tools to do the work.

## What it demonstrates

- **Tool use / function calling** — Claude decides which tool to call and with what arguments.
- **A multi-tool agentic loop** — chaining several tools to complete a task.
- **Tool design** — read-only lookups vs. side-effecting actions, schema-constrained inputs.
- **Multi-turn conversation** — it remembers the context of the chat.

## Setup

```bash
uv sync
cp .env.example .env   # then paste your Anthropic API key into .env
```

## Usage

```bash
uv run assistant.py
```

```
Shopmate — ask about our products, or type 'quit' to exit.
You: how much is the blender?
  [tool] get_price({'product': 'X200 blender'}) -> $49.99
Shopmate: The X200 blender is $49.99.
You: how many are in stock?
  [tool] check_stock({'product': 'X200 blender'}) -> 5 in stock
Shopmate: We have 5 in stock.
You: order 2
  [tool] place_order({'product': 'X200 blender', 'quantity': 2}) -> Order placed: 2 x X200 blender, total $99.98
Shopmate: Done — 2 X200 blenders ordered, total $99.98.
You: can I get 5 ZephyrPro headphones?
  [tool] place_order({'product': 'ZephyrPro headphones', 'quantity': 5}) -> Cannot order 5 — only 0 in stock. (error)
Shopmate: Sorry, the ZephyrPro headphones are out of stock right now.
```

> Note how *"how many are in stock?"* and *"order 2"* never name the product — the assistant remembers "the blender" from earlier turns.

## How it works

On each turn the assistant sends the full conversation plus the tool definitions to Claude. If Claude needs data, it replies with a `tool_use` request; the app runs the matching Python function — a catalog lookup, a total calculation, or an order — and feeds the result back. Claude keeps going, calling more tools if needed, until it has a final answer. Read-only tools (price, stock, quote) run freely; `place_order` is treated as a real action and only fires when you clearly ask to buy.

The catalog lives in `products.json`, so adding products needs no code changes.

## License

MIT
