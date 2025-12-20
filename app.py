from flask import Flask, request, jsonify
import openai
import stripe
import json
import os
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Add CORS headers manually
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# Configuration - Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

# In-memory conversation history (use database in production)
conversations = {}

# Sample product catalog
PRODUCTS = {
    "gift_card_25": {
        "name": "$25 Gift Card",
        "price": 2500,  # in cents
        "currency": "usd",
        "description": "Perfect starter gift"
    },
    "gift_card_50": {
        "name": "$50 Gift Card",
        "price": 5000,
        "currency": "usd",
        "description": "Most popular choice"
    },
    "gift_card_100": {
        "name": "$100 Gift Card",
        "price": 10000,
        "currency": "usd",
        "description": "Premium gift option"
    }
}

# Define available functions for ChatGPT
tools = [
    {
        "type": "function",
        "function": {
            "name": "list_products",
            "description": "Get list of available products for sale",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_checkout_session",
            "description": "Create a Stripe checkout session for a product (redirects to Stripe)",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "The product ID to purchase"
                    }
                },
                "required": ["product_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "process_test_payment",
            "description": "Process payment immediately server-side using test card credentials (no redirect needed)",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "The product ID to purchase"
                    }
                },
                "required": ["product_id"]
            }
        }
    }
]

def list_products() -> str:
    """Return list of available products"""
    products_info = []
    for pid, product in PRODUCTS.items():
        products_info.append({
            "id": pid,
            "name": product["name"],
            "price": f"${product['price']/100:.2f}",
            "description": product["description"]
        })
    return json.dumps(products_info)

def create_checkout_session(product_id: str) -> str:
    """Create Stripe checkout session"""
    if product_id not in PRODUCTS:
        return json.dumps({"error": "Product not found"})
    
    product = PRODUCTS[product_id]
    
    try:
        print(f"Creating checkout session for product: {product_id}")
        print(f"Using Stripe API Key: {stripe.api_key[:20]}...")
        
        # Create Stripe Checkout Session with proper configuration
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': product['currency'],
                    'product_data': {
                        'name': product['name'],
                        'description': product['description'],
                    },
                    'unit_amount': product['price'],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://example.com/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://example.com/cancel',
            metadata={
                'product_id': product_id
            },
        )
        
        print(f"✅ Checkout session created successfully!")
        print(f"✅ Session ID: {session.id}")
        print(f"✅ Checkout URL: {session.url}")
        print(f"✅ Payment status: {session.payment_status}")
        
        return json.dumps({
            "success": True,
            "checkout_url": session.url,
            "session_id": session.id
        })
    except stripe.error.AuthenticationError as e:
        error_msg = "Authentication failed. Please check your Stripe API key."
        print(f"❌ Authentication Error: {str(e)}")
        return json.dumps({"error": error_msg})
    except stripe.error.StripeError as e:
        error_msg = str(e)
        print(f"❌ Stripe Error: {error_msg}")
        return json.dumps({"error": f"Stripe error: {error_msg}"})
    except Exception as e:
        print(f"❌ General Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return json.dumps({"error": str(e)})

def process_test_payment(product_id: str) -> str:
    """Process payment server-side with test card credentials"""
    if product_id not in PRODUCTS:
        return json.dumps({"error": "Product not found"})
    
    product = PRODUCTS[product_id]
    
    try:
        print(f"🔄 Processing server-side payment for: {product['name']}")
        
        # Create a test payment method with test card
        payment_method = stripe.PaymentMethod.create(
            type='card',
            card={
                'number': '4242424242424242',  # Test card
                'exp_month': 12,
                'exp_year': 2034,
                'cvc': '123',
            },
        )
        
        print(f"✅ Payment method created: {payment_method.id}")
        
        # Create a payment intent
        payment_intent = stripe.PaymentIntent.create(
            amount=product['price'],
            currency=product['currency'],
            payment_method=payment_method.id,
            confirm=True,  # Automatically confirm the payment
            automatic_payment_methods={
                'enabled': True,
                'allow_redirects': 'never'
            },
            metadata={
                'product_id': product_id,
                'product_name': product['name']
            }
        )
        
        print(f"✅ Payment Intent created: {payment_intent.id}")
        print(f"✅ Payment Status: {payment_intent.status}")
        
        if payment_intent.status == 'succeeded':
            return json.dumps({
                "success": True,
                "payment_id": payment_intent.id,
                "amount": payment_intent.amount / 100,
                "currency": payment_intent.currency.upper(),
                "status": "succeeded",
                "message": f"Payment successful! You purchased {product['name']}"
            })
        else:
            return json.dumps({
                "success": False,
                "status": payment_intent.status,
                "message": "Payment requires additional action"
            })
            
    except stripe.error.CardError as e:
        print(f"❌ Card Error: {str(e)}")
        return json.dumps({"error": f"Card error: {str(e)}"})
    except stripe.error.StripeError as e:
        print(f"❌ Stripe Error: {str(e)}")
        return json.dumps({"error": f"Stripe error: {str(e)}"})
    except Exception as e:
        print(f"❌ General Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return json.dumps({"error": str(e)})

def execute_function(function_name: str, arguments: Dict) -> str:
    """Execute the requested function"""
    if function_name == "list_products":
        return list_products()
    elif function_name == "create_checkout_session":
        return create_checkout_session(arguments.get("product_id"))
    elif function_name == "process_test_payment":
        return process_test_payment(arguments.get("product_id"))
    else:
        return json.dumps({"error": "Unknown function"})

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    # Initialize conversation history
    if session_id not in conversations:
        conversations[session_id] = [
            {
                "role": "system",
                "content": """You are a helpful sales assistant for a gift card store. 
                
Help users browse and purchase gift cards. When they want to buy something:
1. Use the create_checkout_session function to generate a payment link
2. The function will return a JSON with "checkout_url"
3. Share that URL with the user in a friendly way

Important: When you receive the checkout URL, present it to the user like this:
"Great! I've created your checkout session. Click here to complete your payment: [URL]"

Always be friendly and helpful!"""
            }
        ]
    
    # Add user message
    conversations[session_id].append({
        "role": "user",
        "content": user_message
    })
    
    try:
        # Call OpenAI API with new client
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Updated to use gpt-4o-mini (cheaper and available)
            messages=conversations[session_id],
            tools=tools,
            tool_choice="auto"
        )
        
        assistant_message = response.choices[0].message
        
        # Check if function call is needed
        if assistant_message.tool_calls:
            # Add assistant's function call to history
            conversations[session_id].append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": assistant_message.tool_calls
            })
            
            # Execute each function call
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                print(f"🔧 Executing function: {function_name}")
                print(f"📝 Arguments: {arguments}")
                
                # Execute function
                function_response = execute_function(function_name, arguments)
                print(f"📤 Function response: {function_response}")
                
                # Add function result to conversation
                conversations[session_id].append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": function_response
                })
            
            # Get final response from ChatGPT
            final_response = client.chat.completions.create(
                model="gpt-4o-mini",  # Updated to use gpt-4o-mini
                messages=conversations[session_id]
            )
            
            final_message = final_response.choices[0].message.content
            conversations[session_id].append({
                "role": "assistant",
                "content": final_message
            })
            
            print(f"💬 Final response: {final_message}")
            
            return jsonify({
                "response": final_message,
                "session_id": session_id
            })
        else:
            # No function call, just return response
            conversations[session_id].append({
                "role": "assistant",
                "content": assistant_message.content
            })
            
            return jsonify({
                "response": assistant_message.content,
                "session_id": session_id
            })
            
    except Exception as e:
        print(f"❌ Error in chat endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Stripe webhooks"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    # Handle different event types
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Fulfill the order (save to database, send email, etc.)
        print(f"Payment successful! Session ID: {session['id']}")
        print(f"Product ID: {session['metadata'].get('product_id')}")
        
        # TODO: Save order to database
        # TODO: Send confirmation email
        # TODO: Generate and deliver gift card code
        
    return jsonify({"status": "success"}), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # Validate API keys before starting
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ ERROR: OPENAI_API_KEY not found in environment variables")
        exit(1)
    
    if not os.getenv('STRIPE_SECRET_KEY'):
        print("❌ ERROR: STRIPE_SECRET_KEY not found in environment variables")
        exit(1)
    
    print("✅ OpenAI API Key loaded")
    print("✅ Stripe API Key loaded")
    print(f"✅ Stripe Key starts with: {stripe.api_key[:12]}...")
    
    # Check if in test mode
    if stripe.api_key.startswith('sk_test_'):
        print("✅ Stripe is in TEST MODE (safe for development)")
    elif stripe.api_key.startswith('sk_live_'):
        print("⚠️  WARNING: Stripe is in LIVE MODE (real charges will be made!)")
    else:
        print("❌ ERROR: Invalid Stripe API key format")
        exit(1)
    
    app.run(debug=True, port=5000)