import tkinter as tk
from tkinter import messagebox
import math, random, requests
import matplotlib.pyplot as plt
import datetime


class ToncoinAdvancedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Статистичний аналіз Toncoin")
        self.root.geometry("580x620")

        self.dates = []
        self.prices = []

        tk.Label(root, text="Статистичний аналіз Toncoin", font=("Arial", 18)).pack(pady=10)

        tk.Button(root, text="Завантажити дані з Binance", command=self.load_data_binance, width=35).pack(pady=6)

        tk.Button(root, text="Описова статистика", command=self.show_stats, width=35).pack(pady=6)
        tk.Button(root, text="Побудувати гістограму", command=self.plot_hist, width=35).pack(pady=6)
        tk.Button(root, text="Перевірка нормальності (χ²)", command=self.chi_square_test, width=35).pack(pady=6)
        tk.Button(root, text="Лінійна регресія (тренд)", command=self.regression, width=35).pack(pady=6)
        tk.Button(root, text="Моделювання Монте-Карло", command=self.monte_carlo, width=35).pack(pady=6)

        self.status = tk.Label(root, text="Дані не завантажені", fg="red")
        self.status.pack(pady=10)


    # -----------------------------------------------------------
    #   Binance API
    # -----------------------------------------------------------

    def load_data_binance(self):
        try:
            url = "https://api.binance.com/api/v3/klines"
            params = {
                "symbol": "TONUSDT",
                "interval": "1d",
                "limit": 400
            }

            r = requests.get(url, params=params)
            data = r.json()

            self.prices = [float(candle[4]) for candle in data]

            self.status.config(text="Дані завантажено!", fg="green")
            messagebox.showinfo("Успіх", "Дані успішно завантажено з Binance!")

        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося завантажити дані\n{str(e)}")

    # -----------------------------------------------------------
    #   Описова статистика
    # -----------------------------------------------------------

    def show_stats(self):
        if not self.check_data(): return

        n = len(self.prices)
        mean = sum(self.prices) / n
        var = sum((x - mean) ** 2 for x in self.prices) / n
        std = math.sqrt(var)

        sorted_data = sorted(self.prices)
        median = sorted_data[n // 2]

        cv = std / mean * 100

        messagebox.showinfo(
            "Описова статистика",
            f"Кількість значень: {n}\n"
            f"Середнє значення: {mean:.5f}\n"
            f"Медіана: {median:.5f}\n"
            f"Дисперсія: {var:.5f}\n"
            f"Стандартне відхилення: {std:.5f}\n"
            f"Коефіцієнт варіації: {cv:.2f}%"
        )

    # -----------------------------------------------------------
    #   Гістограма
    # -----------------------------------------------------------

    def plot_hist(self):
        if not self.check_data(): return

        plt.hist(self.prices, bins=12)
        plt.title("Гістограма ціни Toncoin")
        plt.xlabel("Ціна, $")
        plt.ylabel("Частота")
        plt.ticklabel_format(style='plain')
        plt.gca().yaxis.set_major_formatter(lambda x, pos: f"{x:.2f}")

        plt.grid(True)
        plt.show()

    # -----------------------------------------------------------
    #   χ² тест
    # -----------------------------------------------------------

    def chi_square_test(self):
        if not self.check_data(): return

        n = len(self.prices)
        bins = 10
        min_v = min(self.prices)
        max_v = max(self.prices)
        step = (max_v - min_v) / bins

        observed = [0] * bins

        for x in self.prices:
            idx = int((x - min_v) / step)
            if idx >= bins:
                idx = bins - 1
            observed[idx] += 1

        expected = n / bins

        chi2 = 0
        for o in observed:
            chi2 += (o - expected) ** 2 / expected

        messagebox.showinfo(
            "Перевірка нормальності (χ²)",
            f"Значення χ²: {chi2:.4f}\n"
            f"(спрощений статистичний тест)"
        )

    # -----------------------------------------------------------
    #   Лінійна регресія
    # -----------------------------------------------------------

    def regression(self):
        if not self.check_data(): return

        x = list(range(1, len(self.prices) + 1))
        y = self.prices
        n = len(x)

        x_nums = [i for i in range(n)]
        x_mean = sum(x) / n
        y_mean = sum(y) / n

        a = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n)) / \
            sum((x[i] - x_mean) ** 2 for i in range(n))
        b = y_mean - a * x_mean

        trend = [a * xi + b for xi in x]

        plt.figure(figsize=(10, 5))
        plt.plot(x, y, label="Реальна ціна")
        plt.plot(x, trend, label="Лінійна модель")

        plt.legend()
        plt.title("Лінійна регресія (тренд)")
        plt.xlabel("Дні")
        plt.ylabel("Ціна, $")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    # -----------------------------------------------------------
    #   Monte Carlo
    # -----------------------------------------------------------

    def monte_carlo(self):
        if not self.check_data(): return

        returns = []
        for i in range(1, len(self.prices)):
            r = (self.prices[i] - self.prices[i - 1]) / self.prices[i - 1]
            returns.append(r)

        mean = sum(returns) / len(returns)
        var = sum((r - mean) ** 2 for r in returns) / len(returns)
        std = math.sqrt(var)

        last_price = self.prices[-1]

        days = 30
        simulations = 10
        all_paths = []

        for _ in range(simulations):
            price = last_price
            path = []
            for _ in range(days):
                price *= (1 + random.gauss(mean, std))
                path.append(price)
            all_paths.append(path)

        for path in all_paths:
            plt.plot(range(1, days + 1), path)

        plt.title("Моделювання Монте-Карло для Toncoin")
        plt.xlabel("Дні")
        plt.ylabel("Ціна, $")
        plt.ticklabel_format(style='plain')
        plt.gca().yaxis.set_major_formatter(lambda x, pos: f"{x:.2f}")

        plt.grid(True)
        plt.show()

    # -----------------------------------------------------------
    #   Check
    # -----------------------------------------------------------

    def check_data(self):
        if not self.prices:
            messagebox.showerror("Помилка", "Спочатку завантаж дані!")
            return False
        return True


# -----------------------------------------------------------
#   Run
# -----------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = ToncoinAdvancedApp(root)
    root.mainloop()
