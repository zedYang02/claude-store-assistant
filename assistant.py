"""Claude Store Assistant — a conversational CLI that answers questions about a
product catalog (prices, stock, quotes) and places orders, using Claude tool use.

Build it section by section (see the numbered TODOs). Run with:  uv run assistant.py
"""

import json
import anthropic
from dotenv import load_dotenv

with open("products.json") as f:
    CATALOG = json.load(f)

PRODUCTS = list(CATALOG.keys())
# Schema for tools that only need a product name
PRODUCT_SCHEMA = {
    "type": "object",
    "properties": {
        "product": {"type": "string", "enum": PRODUCTS, "description": "name of the product"},
    },
    "required": ["product"],
    "additionalProperties": False,
}

# Schema for tools that need a product name AND a quantity (both required)
ORDER_SCHEMA = {
    "type": "object",
    "properties": {
        "product": {"type": "string", "enum": PRODUCTS, "description": "name of the product"},
        "quantity": {"type": "integer", "description": "how many units"},
    },
    "required": ["product", "quantity"],
    "additionalProperties": False,
}

GET_PRICE = {
    "name": "get_price",
    "description": "Look up the unit price of a product.",
    "input_schema": PRODUCT_SCHEMA,
}
CHECK_STOCK = {
    "name": "check_stock",
    "description": "Check how many units of a product are currently in stock.",
    "input_schema": PRODUCT_SCHEMA,
}
CALCULATE_TOTAL = {
    "name": "calculate_total",
    "description": "Calculate the total price for a quantity of a product. Read-only — use this for price quotes without placing an order.",
    "input_schema": ORDER_SCHEMA,
}
PLACE_ORDER = {
    "name": "place_order",
    "description": "Place a confirmed order for a product. This is a real action with consequences — only call it when the user clearly asks to buy or order.",
    "input_schema": ORDER_SCHEMA,
}

TOOLS = [GET_PRICE, CHECK_STOCK, CALCULATE_TOTAL, PLACE_ORDER]

def run_tool(name, tool_input):
    """Execute a tool. Returns (result_string, is_error)."""
    product = tool_input["product"]
    if name == "get_price":
        return f"${CATALOG[product]['price']:.2f}", False
    elif name == "check_stock":
        return f"{CATALOG[product]['stock']} in stock", False
    elif name == "calculate_total":
        total = tool_input["quantity"] * CATALOG[product]['price']
        return f"${total:.2f}", False
    elif name == "place_order":
        quantity = tool_input["quantity"]
        available = CATALOG[product]['stock']
        if quantity > available:
            return f"Cannot order {quantity} — only {available} {product} in stock.", True
        total = quantity * CATALOG[product]['price']
        return f"Order placed: {quantity} x {product}, total ${total:.2f}", False
    else:
        return f"Unknown tool: {name}", True

SYSTEM = "You are Shopmate, a friendly assistant for an online store. Use the tools to answer questions about products and place orders. Only place an order when the customer clearly asks to buy. Keep replies concise and friendly."

if __name__ == "__main__":
    load_dotenv()
    client = anthropic.Anthropic()
    messages = []
    print("Shopmate — ask about our products, or type 'quit' to exit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit"]:
            break

        messages.append({"role": "user", "content": user_input})
        
        while True:
            response = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=500,
                system=SYSTEM,
                messages=messages,
                tools=TOOLS,
            )
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result, is_error = run_tool(block.name, block.input)
                        flag = " (error)" if is_error else ""
                        print(f"  [tool] {block.name}({block.input}) -> {result}{flag}")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                            "is_error": is_error,
                        })
                messages.append({"role": "user", "content": tool_results})
            else:
                text = next((b.text for b in response.content if b.type == "text"), "")
                print("Shopmate:", text)
                break