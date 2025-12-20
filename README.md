# ChatGPT + Stripe Payment Integration

A conversational AI-powered e-commerce application that allows users to browse and purchase gift cards through a chat interface. Built with Flask, OpenAI's ChatGPT API, and Stripe payment processing.

## 🎯 Features

- **Conversational Shopping**: Chat with an AI assistant to browse products
- **Two Payment Methods**:
  - **Server-Side Payment**: Instant payment processing with test card (no redirect)
  - **Stripe Checkout**: Full Stripe checkout experience in a new tab
- **Function Calling**: ChatGPT intelligently decides when to trigger payment actions
- **Beautiful UI**: Modern chat interface with animations and success modals
- **Real-time Processing**: Immediate payment confirmation and status updates

## 🏗️ Architecture

```
User → Frontend (HTML/JS) → Flask Backend → ChatGPT API → Stripe API
                                    ↓
                                Database (Future)
```

### Components

1. **Frontend** (`index.html`): Interactive chat interface
2. **Backend** (`app.py`): Flask server handling API orchestration
3. **ChatGPT Integration**: Function calling for intelligent payment processing
4. **Stripe Integration**: Payment processing and checkout sessions

## 📋 Prerequisites

- Python 3.8+
- OpenAI API Account
- Stripe Account (Test Mode)
- pip package manager

## 🚀 Installation

### 1. Clone or Create Project Directory

```bash
mkdir chatgpt-stripe-integration
cd chatgpt-stripe-integration
```

### 2. Create Project Structure

```
chatgpt-stripe-integration/
├── app.py              # Flask backend
├── index.html          # Frontend UI
├── .env               # Environment variables (create this)
├── .gitignore         # Git ignore file
└── README.md          # This file
```

### 3. Install Dependencies

```bash
pip install flask openai stripe python-dotenv
```

Or use requirements.txt:

```bash
# Create requirements.txt
cat > requirements.txt << EOF
flask==3.0.0
openai==1.6.1
stripe==7.9.0
python-dotenv==1.0.0
EOF

# Install
pip install -r requirements.txt
```

### 4. Get API Keys

#### OpenAI API Key
1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (starts with `sk-proj-` or `sk-`)

#### Stripe API Key
1. Go to [https://dashboard.stripe.com/test/apikeys](https://dashboard.stripe.com/test/apikeys)
2. Make sure you're in **Test Mode**
3. Copy the **Secret key** (starts with `sk_test_`)

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=sk-proj-your-openai-key-here
STRIPE_SECRET_KEY=sk_test_your-stripe-key-here
STRIPE_WEBHOOK_SECRET=whsec_dummy_for_testing
```

**Important**: 
- Never commit `.env` to Git
- Use test keys only for development

### 6. Create .gitignore

```bash
cat > .gitignore << EOF
.env
__pycache__/
*.pyc
venv/
.vscode/
.idea/
EOF
```

## 💻 Usage

### Start the Server

```bash
python app.py
```

You should see:
```
✅ OpenAI API Key loaded
✅ Stripe API Key loaded
✅ Stripe Key starts with: sk_test_...
✅ Stripe is in TEST MODE (safe for development)
* Running on http://127.0.0.1:5000
```

### Open the Frontend

1. Open `index.html` in your browser
2. Or use: `open index.html` (Mac) / `start index.html` (Windows)

### Try the Chat

**Browse Products:**
```
You: "What gift cards do you have?"
Bot: Lists available gift cards
```

**Instant Payment (Default):**
```
You: "I want to buy a $50 gift card"
Bot: [Processes payment instantly]
     [Success modal appears]
```

**Checkout Link:**
```
You: "Give me a checkout link for the $25 card"
Bot: [Provides button that opens Stripe checkout]
```

## 🧪 Testing

### Test Card Numbers

Use these cards in Stripe Checkout:

| Card Number | Scenario |
|-------------|----------|
| `4242 4242 4242 4242` | Success |
| `4000 0000 0000 0002` | Card declined |
| `4000 0000 0000 9995` | Insufficient funds |

**Additional Details:**
- Expiry: Any future date (e.g., `12/34`)
- CVC: Any 3 digits (e.g., `123`)
- ZIP: Any 5 digits (e.g., `12345`)

### View Test Payments

Go to [https://dashboard.stripe.com/test/payments](https://dashboard.stripe.com/test/payments)

## 🔧 Configuration

### Product Catalog

Edit `PRODUCTS` dictionary in `app.py`:

```python
PRODUCTS = {
    "gift_card_25": {
        "name": "$25 Gift Card",
        "price": 2500,  # in cents
        "currency": "usd",
        "description": "Perfect starter gift"
    },
    # Add more products...
}
```

### ChatGPT Model

Change model in `app.py`:

```python
model="gpt-4o-mini",  # Fast and efficient
# Or use: "gpt-4o" for more advanced features
```

## 📁 Project Files

### app.py

Flask backend that:
- Handles chat requests
- Manages ChatGPT function calling
- Processes Stripe payments
- Maintains conversation history

### index.html

Frontend that provides:
- Chat interface
- Message display
- Payment success modal
- Checkout button handling

## 🔐 Security Notes

### For Development (Current Setup)
✅ Test mode only
✅ API keys in `.env` file
✅ No real charges

### For Production (Future)
- [ ] Use environment variables (not `.env`)
- [ ] Add user authentication
- [ ] Implement rate limiting
- [ ] Add HTTPS
- [ ] Validate all inputs
- [ ] Add CSRF protection
- [ ] Use production Stripe keys
- [ ] Set up proper webhook verification

## 🌐 API Endpoints

### POST /chat
Process chat messages and handle payments

**Request:**
```json
{
  "message": "I want to buy a gift card",
  "session_id": "unique_session_id"
}
```

**Response:**
```json
{
  "response": "Payment successful!",
  "session_id": "unique_session_id",
  "checkout_url": "https://checkout.stripe.com/..." (optional)
}
```

### POST /webhook
Handle Stripe webhook events (payment confirmations)

### GET /health
Health check endpoint

## 🎨 Customization

### Change Colors

Edit CSS in `index.html`:

```css
/* Main gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Change to your brand colors */
background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
```

### Modify System Prompt

Edit in `app.py`:

```python
{
    "role": "system",
    "content": "You are a helpful sales assistant..."
}
```

## 🚧 Roadmap / Future Enhancements

- [ ] Add database (SQLite/PostgreSQL) for order storage
- [ ] Implement user authentication
- [ ] Add email confirmations
- [ ] Generate actual gift card codes
- [ ] Add order history page
- [ ] Support multiple payment methods
- [ ] Add discount codes
- [ ] Deploy to production (Heroku/Railway/AWS)
- [ ] Add webhook handling for payment confirmations
- [ ] Implement inventory management

## 🐛 Troubleshooting

### "API key not found" Error
- Check `.env` file exists in project root
- Verify no spaces around `=` in `.env`
- Restart Flask server after changing `.env`

### "Model not found" Error
- Update to `gpt-4o-mini` or `gpt-3.5-turbo`
- Check OpenAI account has credits

### Checkout Link Doesn't Open
- Check browser console for errors (F12)
- Verify button click handler is working
- Try copying URL and pasting in new tab

### CORS Errors
- Backend already handles CORS
- If issues persist, check browser console
- Try different browser

### Stripe "Indian regulations" Error
- Use a US Stripe account for testing
- Stay in Test Mode
- Use test API keys (`sk_test_`)

## 📚 Documentation Links

- [OpenAI API Docs](https://platform.openai.com/docs)
- [Stripe API Docs](https://stripe.com/docs/api)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Stripe Testing](https://stripe.com/docs/testing)

## 🤝 Contributing

Feel free to fork and submit pull requests!

## 📄 License

MIT License - feel free to use for personal or commercial projects

## 👨‍💻 Author

Built with ❤️ using ChatGPT, Flask, and Stripe

## 🙏 Acknowledgments

- OpenAI for ChatGPT API
- Stripe for payment processing
- Flask for the web framework

---

**Happy Building! 🚀**

For questions or issues, please refer to the troubleshooting section or check the documentation links above.