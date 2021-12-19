# Run this module to back a strategies that you have coded against historical data
from stockscanner.model.config import Config
from stockscanner.model.strategies.strategy_manager import StrategyManager
import matplotlib.pyplot as plt

config = Config.load_config()

sm: StrategyManager = StrategyManager.get_instance()

strategy_configs = config["backtest"]
reports = {}
for strategy_config in strategy_configs:
    test_name = strategy_config["test_name"]
    report = sm.back_test_strategy(strategy_config)
    reports[test_name] = report

legend = []
for test_name, report in reports.items():
    plt.scatter(*zip(*report.performance))
    legend.append(test_name)

plt.legend(legend)
plt.show()
