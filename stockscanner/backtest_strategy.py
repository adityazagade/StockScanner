# Run this module to back a strategies that you have coded against historical data
from datetime import datetime
from stockscanner.model.config import Config
from stockscanner.model.strategies.strategy_manager import StrategyManager
import matplotlib.pyplot as plt

config = Config.load_config()

sm: StrategyManager = StrategyManager.get_instance()

strategies = config["backtest"]
reports = {}
for strategy in strategies:
    strategy_name = strategy["strategy_name"]
    date_time_obj = datetime.strptime(strategy["backtest_start_date"], '%d-%m-%Y').date()
    report = sm.back_test_strategy(strategy_name, back_test_start_date=date_time_obj)
    reports[strategy_name] = report

legend = []
for strategy_name, report in reports.items():
    plt.scatter(*zip(*report.performance))
    legend.append(strategy_name)

plt.legend(legend)
plt.show()
