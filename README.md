# AuraGlow E-Commerce - Single Vendor Tech Store

A premium, state-of-the-art Single Vendor E-commerce web application built from scratch with **Python 3**, **Django 5**, and **Stripe Integration** for secure payments.

The interface features custom, glassmorphic dark-theme components, subtle animations, responsive grids, and strict checkout stock validations.

---

## 🚀 Key Features

*   **Premium Visual Design**: Glowing accent buttons, responsive cards, glassmorphic side-panels, and unified modern fonts (Outfit & Inter).
*   **Persistent Cart Manager**: Fully-functional session-backed cart letting users add, remove, and adjust quantities in real-time, bound strictly to current inventory.
*   **Out-of-Stock Enforcements**: Products marked out-of-stock cannot be ordered or added to carts. Real-time inventory limits are verified both on catalog/cart updates and inside the payment transaction boundaries.
*   **Stripe Checkout Integration**: Seamlessly delegates payments to Stripe Checkout Session, verifying completed states before reducing store warehouse stock and recording order states.
*   **Secure Authentication**: Built-in Django encryption for registration, logins, and logouts. Restricts checkout, invoice views, and history lists to logged-in users.
*   **Order Tracking**: Complete client order receipts and purchase histories displaying statuses (Paid/Pending/Failed) and collapsible list details.

---

## 🛠️ Tech Stack

*   **Backend**: Python (>= 3.8), Django (>= 4.2)
*   **Database**: SQLite (Development-ready, local configuration)
*   **Payments**: Stripe API Checkout Sessions
*   **Frontend**: HTML5, CSS3 (Vanilla CSS variables & modern reset), Bootstrap 5, FontAwesome Icons

---

## 📦 Project Structure

```text
OstadProjects/
├── ecom_project/           # Main Django Project Configuration
│   ├── settings.py         # Config files (Loads .env.local, Stripe API, Auth URLs)
│   ├── urls.py             # Main router
│   ├── wsgi.py / asgi.py   # Gateway servers
│   └── __init__.py
├── store/                  # E-commerce Application App
│   ├── management/         # Seeding commands
│   │   └── commands/seed_db.py
│   ├── migrations/         # Database migrations
│   ├── templates/          # App specific/registration pages
│   ├── admin.py            # Model registries in Django Admin
│   ├── apps.py             # Store Configuration
│   ├── cart.py             # Session Cart class logic
│   ├── context_processors.py # Exposes cart context globally
│   ├── forms.py            # User registration/shipping validation
│   ├── models.py           # DB Schemas: Category, Product, Order, OrderItem
│   ├── urls.py             # Routing pathways
│   ├── views.py            # Main logic controllers
│   └── __init__.py
├── static/                 # Static media files
│   └── css/style.css       # Custom high-end dark design system CSS
├── templates/              # Core templates (extends base.html)
│   ├── base.html           # Main template architecture
│   ├── registration/       # Auth templates
│   │   ├── login.html
│   │   └── register.html
│   └── store/              # Page layouts
│       ├── home.html
│       ├── product_detail.html
│       ├── cart_detail.html
│       ├── checkout.html
│       ├── success.html
│       ├── cancel.html
│       └── order_history.html
├── requirements.txt        # Package dependencies
├── .env.example            # Environment variables example template
├── .env.local              # Local secrets configuration (Ignored by Git)
├── .gitignore              # Ignored system / SQLite / Virtualenv files
└── manage.py               # Django CLI utility
```

---

## ⚙️ Local Setup and Installation

Follow these steps to set up and run the e-commerce application locally:

### 1. Prerequisites
Ensure you have **Python 3.8+** installed on your system.

### 2. Set Up a Virtual Environment & Activate
Create and activate a virtual environment in the project directory:
```bash
# Create a virtual environment named .env (or venv)
python3 -m venv .env

# Activate it
source .env/bin/activate  # On Linux/macOS
# OR
.env\Scripts\activate         # On Windows
```

### 3. Install Dependencies
Run pip to install requirements:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env.local` (we use `.env.local` because the virtualenv directory is already named `.env`):
```bash
cp .env.example .env.local
```
Open `.env.local` and add your **Stripe API keys** (which you can obtain for free from your [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys)):
```ini
# Django settings
SECRET_KEY=generate-a-secure-random-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Stripe API Keys (Get from dashboard.stripe.com/test/apikeys)
STRIPE_PUBLISHABLE_KEY=pk_test_51...
STRIPE_SECRET_KEY=sk_test_51...
```

### 5. Run Database Migrations
Create and apply database tables:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Seed Initial Data & Create Administrator
We have provided a custom seed script to create test data and an admin account. Run:
```bash
python manage.py seed_db
```
This script creates:
*   An administrator account: **Username**: `admin` | **Password**: `adminpass123`
*   Three product categories (Computers, Audio, Smart Home)
*   Seven premium products (including one out-of-stock item for testing boundaries)

### 7. Run the Server
Start Django's local development server:
```bash
python manage.py runserver
```
Visit the store at: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)  
Visit the Django admin panel to manage products at: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 💳 Demonstration and Testing Payments

1.  Log in using the seed account (`admin` / `adminpass123`) or create a new user via the **Sign Up** portal.
2.  Add items to the cart, navigate to **Cart**, and select **Proceed to Checkout**.
3.  Fill out the shipping details form and click **Proceed to Stripe Payment**.
4.  You will be redirected to the secure Stripe Checkout site.
5.  To trigger a successful purchase, enter the standard Stripe test card number:
    *   **Card Number**: `4242 4242 4242 4242`
    *   **Expiry**: Any future date (e.g., `12/29`)
    *   **CVC**: Any 3 digits (e.g., `123`)
    *   **Postal Code**: Any 5 digits (e.g., `90210`)
6.  Upon clicking **Pay**, Stripe will process the card and redirect you back to AuraGlow's Success page.
7.  The stock for the purchased items will automatically decrement in the database, and the order will show as `Paid` in your **My Orders** panel.
