
def reward_function(portfolio_value, trade, max_trade_percent=0.1):
    reward = 0
    # Winst of verlies
    reward += trade['profit']  # positief bij winst, negatief bij verlies

    # Straf als trade te groot is
    if trade['amount'] > portfolio_value * max_trade_percent:
        reward -= 0.1

    # Straf als trade te vroeg is (bijv. binnen 1 candle na vorige trade)
    if trade['too_soon']:
        reward -= 0.05

    return reward
