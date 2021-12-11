class Report:
    def __init__(self, p) -> None:
        self.p = p

    def __str__(self) -> str:
        tp1 = f"Total Invested: ${self.p.total_invested()}, Current Value: ${self.p.get_current_value()}"
        return '\r\n'.join(map(str, self.p.get_change_logs())) + "\n" + tp1
