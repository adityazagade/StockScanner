# Run this module to back a strategies that you have coded against historical data
from datetime import datetime
from stockscanner.model.config import Config
from stockscanner.model.strategies.strategy_manager import StrategyManager

config = Config.load_config()

sm: StrategyManager = StrategyManager.get_instance()
date_time_obj = datetime.strptime(config["backtest"]["backtest_start_date"], '%d-%m-%Y').date()
report = sm.back_test_strategy(config["backtest"]["strategy_name"], back_test_start_date=date_time_obj)
print(report)
