# NovaCell — Django Mobile Shop

A complete e-commerce website for a mobile phone shop, built with Django.

## Features

- Product catalog with categories, brands, RAM/storage/color specs, images, stock, and sale pricing
- Product listing page with search, category/brand filters, sorting, and pagination
- Product detail pages with related products
- Session-based shopping cart (add, update quantity, remove)
- Checkout flow that creates an `Order` with line items and reduces stock
- User signup / login / logout (Django's built-in auth)
- Full Django admin for managing products, categories, brands, and orders
- Responsive, custom-designed dark theme (no external CSS framework)

## Project layout

```
mobileshop/
├── manage.py
├── requirements.txt
├── mobileshop/          # project settings, urls, wsgi/asgi
└── shop/                # the app: models, views, cart, templates, static, admin
    ├── models.py        # Category, Brand, Product, ProductImage, Order, OrderItem
    ├── views.py
    ├── cart.py          # session cart logic
    ├── forms.py         # checkout + signup forms
    ├── admin.py
    ├── management/commands/seed_data.py   # loads sample phones
    ├── templates/shop/  # all page templates
    └── static/shop/css/style.css
```

## Setup

1. **Create a virtual environment and install dependencies**

   ```bash
   cd mobileshop
   python -m venv venv
   source venv/bin/activate   # on Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run migrations**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create an admin user**

   ```bash
   python manage.py createsuperuser
   ```

4. **(Optional) Load sample phones** so the store isn't empty:

   ```bash
   python manage.py seed_data
   ```

5. **Run the dev server**

   ```bash
   python manage.py runserver
   ```

   Visit `http://127.0.0.1:8000/` for the storefront and `http://127.0.0.1:8000/admin/` to manage products and orders.

## Adding real products

Go to `/admin/`, log in with your superuser, and add:
1. **Brands** (Apple, Samsung, etc.)
2. **Categories** (Flagship, Budget Phones, etc.)
3. **Products** — set price, optional discount price, specs, stock, and upload a product image.

## Notes for production

- `settings.py` now reads `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL`, and (optionally) S3 credentials from environment variables — see the "Deploying to Vercel" section below for the exact values to set.
- Static files are served via `whitenoise` (works locally and on most hosts, including Vercel).
- Add real payment gateway integration (e.g. Razorpay/Stripe) to the checkout view — currently orders are placed as "Cash on Delivery / Pay on Pickup" style orders with a status field you can update from the admin.

## Deploying to Vercel

Vercel's Python/Django support auto-detects `manage.py` and reads `WSGI_APPLICATION` from your settings — no `vercel.json` needed for a standard layout like this one.

1. **Push this project to GitHub** with `manage.py` at the root of the repo (or of whatever folder you set as Root Directory below).

2. **Import the repo into Vercel.** If `manage.py` isn't at your repo's root (e.g. it's nested inside a `mobileshop/` folder inside the repo), go to **Project Settings → General → Root Directory** and set it to that folder.

3. **Add environment variables** (Project Settings → Environment Variables):

   | Variable | Value |
   |---|---|
   | `SECRET_KEY` | a long random string (generate one, don't reuse the dev default) |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | your Vercel domain, e.g. `myshop.vercel.app` |
   | `DATABASE_URL` | your Postgres connection string (see next step) |

4. **Add a Postgres database.** Vercel's serverless filesystem is ephemeral, so SQLite can't be used in production. Add **Vercel Postgres** (or Neon/Supabase) from the Storage tab — it will set `DATABASE_URL` (or a similarly-named var; copy it into `DATABASE_URL` above if it differs) automatically.

5. **(Optional) Add media storage.** Product images uploaded through the admin also can't be saved to local disk on Vercel. Create an S3-compatible bucket (AWS S3, Cloudflare R2, or Vercel Blob's S3-compatible mode) and set:

   | Variable | Value |
   |---|---|
   | `AWS_ACCESS_KEY_ID` | your access key |
   | `AWS_SECRET_ACCESS_KEY` | your secret key |
   | `AWS_STORAGE_BUCKET_NAME` | your bucket name |
   | `AWS_S3_ENDPOINT_URL` | only needed for non-AWS providers (e.g. R2's endpoint URL) |
   | `AWS_S3_REGION_NAME` | your bucket's region |

   Without these, uploaded images will disappear after each deploy/cold-start — fine for testing, not for real use.

6. **Run migrations against the production database.** Since there's no persistent shell on Vercel by default, either:
   - run `python manage.py migrate` locally with `DATABASE_URL` pointed at your production Postgres instance, or
   - use `vercel env pull` to pull the env vars locally, then run migrations from your machine.

7. **Deploy.** Push to your connected branch (or run `vercel --prod`). Static files are collected automatically by Vercel's build process.
