# The Daily Grind – upgraded ordering + analytics

## Run
1. `pip install -r requirements.txt`
2. `python app.py`
3. Serve the HTML folder from a local web server (for example VS Code Live Server) and open `index.html`.

The backend creates `users.csv` and `orders.csv` on first run. Behaviour events are written to `user_behaviour_data.csv` only for authenticated users, so returning users keep the same user identity and new visits continue updating the CSV.

## Main changes
- Login/signup required before cart/order/analytics activity is recorded.
- Persistent user identity stored in `users.csv` with hashed passwords.
- User Activity dashboard: credits, tier, orders, cart items and product views.
- ₹ pricing throughout the ordering flow.
- Offers and blinking MOST TRENDING badges.
- Credits: 1 per ₹10 spent; Bronze/Silver/Gold progress; checkout redemption at ₹1 per credit.
- Full delivery address, phone, outlet and order notes.
- Pickup, Standard Delivery and Urgent Delivery; urgent fee ₹79; standard delivery free above ₹499.
- Enhanced checkout with quantities, removal, tax, delivery fee, urgent fee, credits and final total.
- Product filters: All, Trending, Offers, Coffee, Food.
- Ratings and Zomato/Swiggy outbound ordering links.
- Outlet locations page.
- Backend order CSV includes phone, address, outlet, order type, delivery fee, urgent fee, credits, notes and totals.
"# web-anaylsis" 
