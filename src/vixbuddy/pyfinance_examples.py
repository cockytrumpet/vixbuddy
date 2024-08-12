import matplotlib.pyplot as plt
import yfinance as yf

# Plotting
data = yf.download("AAPL", start="2020-01-01", end="2021-01-01")  # interval='1wk'
data["Close"].plot()
plt.title("Apple Stock Prices")
plt.show()

# Most up-to-date
apple = yf.Ticker("AAPL")
print(apple.history(period="1d"))
