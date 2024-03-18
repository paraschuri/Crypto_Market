import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import requests
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def fetchData(symbol):
    url = "https://api.binance.com/api/v3/ticker/24hr"
    params = {
        "symbol": symbol+'USDT'
    }
    data = requests.get(url,params=params)
    return data

def on_coin_click(data):
    new_window = tk.Toplevel(root)
    new_window.title(f"Details for {data['symbol'][:-4]}") #string slicing to remove the "USDT" part from end
    
    info_frame = ttk.Frame(new_window, padding="20")
    info_frame.grid(row=0, column=0, sticky="nsew")
    
    info_label = ttk.Label(info_frame, text=f"Details for {data['symbol'][:-4]}", font=("Helvetica", 16, "bold"))
    info_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

    url = 'https://api.binance.com/api/v3/klines'
    params = {
        'interval': '1h',
        'limit': 20,
        'symbol': data['symbol']
    }
    
    graph_data = requests.get(url,params=params).json()
    df = pd.DataFrame(graph_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    fig, ax = plt.subplots(figsize=(12, 4), dpi=100)
    ax.plot(df['timestamp'], df['close'].astype(float), label=f"{data['symbol'][:-4]} Price (USDT)")
    ax.set_title('Price Trend')
    ax.set_xlabel('Time')
    ax.set_ylabel('Price')
    ax.legend()
    canvas = FigureCanvasTkAgg(fig, master=info_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=1, column=0, columnspan=2, pady=(0, 20))

    coin_info = {
        'Symbol': data['symbol'][:-4],
        'Current Price': f"${data['lastPrice']}",
        'Volume (24h)': data['volume'],
        'Opening price': data['openPrice'],
        'High Price': data['highPrice'],
        'Low Price': data['lowPrice'],
        'Price Change': data['priceChange']
    }

    for i, (key, value) in enumerate(coin_info.items(), start=2):
        key_label = ttk.Label(info_frame, text=f"{key}:", font=("Helvetica", 12, "bold"))
        key_label.grid(row=i, column=0, sticky="e", padx=(0, 10))
        value_label = ttk.Label(info_frame, text=value, font=("Helvetica", 12))
        value_label.grid(row=i, column=1, sticky="w")

    new_window.mainloop()

def update_labels():
    for i, (coin_name, symbol) in enumerate(coin_labels, start=2):
        data = fetchData(symbol).json()
        
        price_label = root.grid_slaves(row=i, column=2)[0]
        price_change_label = root.grid_slaves(row=i, column=3)[0]
        volume_label = root.grid_slaves(row=i, column=4)[0]

        price_label.config(text=f"${data['lastPrice']}")
        
        change = "green" if float(data['priceChangePercent']) > 0 else "red"
        price_change_label.config(text=f"{data['priceChangePercent']}%", fg=change)
        volume_label.config(text=f"{data['volume']}")

def search_coin():
    coin_symbol = tk.simpledialog.askstring("Search", "Enter the coin symbol:")
    if coin_symbol:
        data = fetchData(coin_symbol.upper())
        #To check if the entered coin is valid or not
        if data.status_code == 200:
            on_coin_click(data.json())
        else:
            tk.messagebox.showinfo("Error", "Enter a valid coin")
    else:
        tk.messagebox.showinfo("Error","Don't leave it blank")

if __name__=="__main__":
    root = tk.Tk()
    root.title("Crypto Market")
    heading_label = tk.Label(root, text="Crypto Market", font=("Helvetica", 20, "bold"),fg="blue")
    heading_label.grid(row=0, column=0, columnspan=4, pady=20)
    column_headings = ["Coin", "Symbol", "Price", "Price Change","Volume"]
    for i, heading in enumerate(column_headings):
        heading_label = tk.Label(root, text=heading, font=("Helvetica", 14, "bold"))
        heading_label.grid(row=1, column=i, padx=20, pady=10)
    coin_labels = [
        ("Bitcoin", "BTC"),
        ("Ethereum", "ETH"),
        ("Cardano", "ADA"),
        ("Binance Coin", "BNB"),
        ("Solana", "SOL")
    ]
    for i, (coin_name, symbol) in enumerate(coin_labels, start=2):
        #Fetching the api data for the current coin
        data = fetchData(symbol).json()
    
        coin_label = tk.Label(root, text=coin_name, font=("Helvetica", 12, "bold"),cursor="hand2")
        coin_label.grid(row=i, column=0, padx=20, pady=10)
        
        #Binding clickable button to the coin name
        coin_label.bind("<Button-1>", lambda event, data=data: on_coin_click(data))

        symbol_label = tk.Label(root, text=symbol, font=("Helvetica", 12))
        symbol_label.grid(row=i, column=1, padx=20, pady=10)

        price_label = tk.Label(root, text=f"${data['lastPrice']}", font=("Helvetica", 12))
        price_label.grid(row=i, column=2, padx=20, pady=10)
        
        change = "green" if float(data['priceChangePercent'])>0 else "red"
        price_change_label = tk.Label(root, text=f"{data['priceChangePercent']}%", font=("Helvetica", 12),fg=change)
        price_change_label.grid(row=i, column=3, padx=20, pady=10)
        
        volume_label = tk.Label(root, text=f"{data['volume']}", font=("Helvetica", 12))
        volume_label.grid(row=i, column=4, padx=20, pady=10)
    search_button = tk.Button(root, text="Search", command=search_coin, bg="#004080", fg="white", font=("Helvetica", 12,"bold"))
    search_button.grid(row=0, column=3, padx=20, pady=10)
    refresh_button = tk.Button(root, text="Refresh", command=update_labels, bg="#004080", fg="white", font=("Helvetica", 12, "bold"))
    refresh_button.grid(row=0, column=4, padx=20, pady=10)
    root.mainloop()