import tkinter as tk
import random
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class OrderBook:
    def __init__(self):
        self.buy_orders = defaultdict(list)  # Buy side (price -> orders)
        self.sell_orders = defaultdict(list)  # Sell side (price -> orders)
        self.transactions = []  # List to store completed transactions

    def add_order(self, order_type, price, size):
        """ Add a new order and match it if possible """
        if order_type == 'buy':
            self.match_order('buy', price, size)
        elif order_type == 'sell':
            self.match_order('sell', price, size)

    def match_order(self, order_type, price, size):
        """ Match orders against the opposite side of the book """
        if order_type == 'buy':
            # Match with sell orders
            while size > 0 and self.sell_orders and min(self.sell_orders.keys()) <= price:
                lowest_sell_price = min(self.sell_orders.keys())
                sell_order = self.sell_orders[lowest_sell_price][0]
                
                if sell_order['size'] <= size:
                    # Full match
                    self.record_transaction(lowest_sell_price, sell_order['size'])
                    size -= sell_order['size']
                    self.sell_orders[lowest_sell_price].pop(0)
                    if not self.sell_orders[lowest_sell_price]:
                        del self.sell_orders[lowest_sell_price]
                else:
                    # Partial match
                    self.record_transaction(lowest_sell_price, size)
                    sell_order['size'] -= size
                    size = 0
            if size > 0:
                self.buy_orders[price].append({'size': size, 'time': datetime.now()})
        
        elif order_type == 'sell':
            # Match with buy orders
            while size > 0 and self.buy_orders and max(self.buy_orders.keys()) >= price:
                highest_buy_price = max(self.buy_orders.keys())
                buy_order = self.buy_orders[highest_buy_price][0]
                
                if buy_order['size'] <= size:
                    # Full match
                    self.record_transaction(highest_buy_price, buy_order['size'])
                    size -= buy_order['size']
                    self.buy_orders[highest_buy_price].pop(0)
                    if not self.buy_orders[highest_buy_price]:
                        del self.buy_orders[highest_buy_price]
                else:
                    # Partial match
                    self.record_transaction(highest_buy_price, size)
                    buy_order['size'] -= size
                    size = 0
            if size > 0:
                self.sell_orders[price].append({'size': size, 'time': datetime.now()})
    
    def record_transaction(self, price, size):
        """ Record a completed transaction in the transaction list """
        self.transactions.append({
            'price': price,
            'size': size,
            'time': datetime.now()
        })
    
    def get_order_book(self):
        """ Return the current state of the order book """
        return self.buy_orders, self.sell_orders

    def get_transactions(self):
        """ Return the list of transactions """
        return self.transactions
    #all functions to calculate vairables
    def get_bid_price(self):
        """Calculates the highest active buy price b(t)"""
        return max(self.buy_orders.keys()) if self.buy_orders else float('nan')

    def get_ask_price(self):
        """Calculates the lowest active sell price a(t)"""
        return min(self.sell_orders.keys()) if self.sell_orders else float('nan')

    def get_bid_ask_spread(self):
        """Calculates the bid-ask spread s(t)"""
        return self.get_ask_price() - self.get_bid_price()
    
    def get_mid_price(self):
        """Calculates the mid price m(t)"""
        return (self.get_bid_price() + self.get_ask_price()) / 2


class GUI:
    def __init__(self, root, order_book):
        self.order_book = order_book
        self.root = root
        self.root.title("Limit Order Book")

        #Dynamic variable to track 
        self.total_buy_orders = 0
        self.total_sell_orders = 0
        self.total_transactions = 0


        # GUI elements for order input
        self.label_type = tk.Label(root, text="Order Type (buy/sell):")
        self.label_type.grid(row=0, column=0)
        self.entry_type = tk.Entry(root)
        self.entry_type.grid(row=0, column=1)

        self.label_price = tk.Label(root, text="Price:")
        self.label_price.grid(row=1, column=0)
        self.entry_price = tk.Entry(root)
        self.entry_price.grid(row=1, column=1)

        self.label_size = tk.Label(root, text="Size:")
        self.label_size.grid(row=2, column=0)
        self.entry_size = tk.Entry(root)
        self.entry_size.grid(row=2, column=1)

        self.variable_frame = tk.Frame(root)
        self.variable_frame.grid(row=1, column=4)
        self.bid_price = 0
        self.ask_price = 0
        self.bid_ask_spread = 0

        self.label_bid_price = tk.Label(self.variable_frame, text=f"Bid Price: {self.bid_price:.2f}")
        self.label_ask_price = tk.Label(self.variable_frame, text=f"Ask Price: {self.ask_price:.2f}")
        self.label_bid_ask_spread = tk.Label(self.variable_frame, text=f"Bid-Ask Spread: {self.bid_ask_spread:2f}")
    

        # Pack labels
        self.label_bid_price.pack()
        self.label_ask_price.pack()
        self.label_bid_ask_spread.pack()


        self.submit_button = tk.Button(root, text="Submit Order", command=self.submit_order)
        self.submit_button.grid(row=3, column=0, columnspan=2)

        # GUI elements for displaying the order book
        self.label_buy_orders = tk.Label(root, text=f"Buy Orders (Total: {self.total_buy_orders})")
        self.label_buy_orders.grid(row=4, column=0)
        self.label_sell_orders = tk.Label(root, text=f"Sell Orders (Total: {self.total_sell_orders})")
        self.label_sell_orders.grid(row=4, column=1)

        self.buy_orders_text = tk.Text(root, height=10, width=30)
        self.buy_orders_text.grid(row=5, column=0)
        self.sell_orders_text = tk.Text(root, height=10, width=30)
        self.sell_orders_text.grid(row=5, column=1)
    

        # GUI elements for displaying the transaction list
        self.label_transactions = tk.Label(root, text = f"Transactions (Total: {self.total_transactions})")
        self.label_transactions.grid(row=6, column=0, columnspan=2)
        self.transactions_text = tk.Text(root, height=10, width=60)
        self.transactions_text.grid(row=7, column=0, columnspan=2)

        # Adjusted Matplotlib figure for plotting orders (smaller size)
        self.fig, self.ax = plt.subplots(figsize=(4, 2))  # Adjust figure size here
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().grid(row=8, column=0, columnspan=2)
        self.update_plot()

        # Initialise all variable (eg bid_price, ask_price, etc)
        self.bid_price = None
        self.ask_price = None
        self.bid_ask_spread = None


        # Automatically generate random orders
        self.generate_random_order()

    def submit_order(self):
        """ Handle order submission from the GUI """
        order_type = self.entry_type.get().lower()
        price = float(self.entry_price.get())
        size = int(self.entry_size.get())
        
        self.order_book.add_order(order_type, price, size)
        self.update_order_book_display()
        self.update_transactions_display()
        self.update_plot()

    def update_order_book_display(self):
        """ Update the display of buy and sell orders """
        buy_orders, sell_orders = self.order_book.get_order_book()

        self.buy_orders_text.delete(1.0, tk.END)
        self.sell_orders_text.delete(1.0, tk.END)

        # Cakuclate dynamic changes
        self.total_buy_orders = sum(len(orders) for orders in buy_orders.values())
        self.label_buy_orders.config(text=f"Buy Orders (Total: {self.total_buy_orders})")
        

        self.total_sell_orders = sum(len(orders) for orders in sell_orders.values())
        self.label_sell_orders.config(text=f"Sell Orders (Total: {self.total_sell_orders})")

        self.total_transactions = len(self.order_book.get_transactions())
        self.label_transactions.config(text=f"Transactions (Total: {self.total_transactions})")

         #update variable
        self.bid_price = self.order_book.get_bid_price()
        self.label_bid_price.config(text=f"Bid Price: {self.bid_price:.2f}" if self.bid_price else "Bid Price: N/A")

        self.ask_price = self.order_book.get_ask_price()
        self.label_ask_price.config(text=f"Ask Price: {self.ask_price:.2f}" if self.ask_price else "Ask Price: N/A")

        self.bid_ask_spread = self.order_book.get_bid_ask_spread()
        self.label_bid_ask_spread.config(text=f"Bid-Ask Spread: {self.bid_ask_spread:.2f}" if self.bid_ask_spread else "Bid-Ask Spread: N/A")

        # Display buy orders
        for price, orders in sorted(buy_orders.items(), reverse=True):
            for order in orders:
                self.buy_orders_text.insert(tk.END, f"Price: {price}, Size: {order['size']}\n")

        # Display sell orders
        for price, orders in sorted(sell_orders.items()):
            for order in orders:
                self.sell_orders_text.insert(tk.END, f"Price: {price}, Size: {order['size']}\n")

       

    def update_transactions_display(self):
        """ Update the display of transactions """
        transactions = self.order_book.get_transactions()

        self.transactions_text.delete(1.0, tk.END)

        for transaction in transactions:
            self.transactions_text.insert(tk.END, f"Price: {transaction['price']}, "
                                                  f"Size: {transaction['size']}, "
                                                  f"Time: {transaction['time']}\n")

    
        



    def update_plot(self):
        """ Update the plot for buy and sell prices with volume """
        self.ax.clear()
        buy_orders, sell_orders = self.order_book.get_order_book()

        buy_prices = []
        buy_volumes = []
        sell_prices = []
        sell_volumes = []

        for price, orders in sorted(buy_orders.items(), reverse=True):
            total_size = sum(order['size'] for order in orders)
            buy_prices.append(price)
            buy_volumes.append(total_size)

        for price, orders in sorted(sell_orders.items()):
            total_size = sum(order['size'] for order in orders)
            sell_prices.append(price)
            sell_volumes.append(total_size)

        if buy_prices and buy_volumes:
            self.ax.bar(buy_prices, buy_volumes, color='green', label='Buy Orders', alpha=0.5)
        if sell_prices and sell_volumes:
            self.ax.bar(sell_prices, sell_volumes, color='red', label='Sell Orders', alpha=0.5)

        self.ax.set_xlabel('Price')
        self.ax.set_ylabel('Volume')
        self.ax.legend()
        self.ax.set_title('Order Book - Price vs Volume')

        self.canvas.draw()



    def generate_random_order(self):
        """ Generate a random buy or sell order periodically """
        order_type = random.choice(['buy', 'sell'])
        price = round(random.uniform(90, 110), 2)
        size = random.randint(1, 10)
        
        self.order_book.add_order(order_type, price, size)
        self.update_order_book_display()
        self.update_transactions_display()
        self.update_plot()

        # Generate a new order every 2 seconds
        self.root.after(200, self.generate_random_order)

if __name__ == "__main__":
    root = tk.Tk()
    order_book = OrderBook()
    gui = GUI(root, order_book)
    root.mainloop()
