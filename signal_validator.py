# signal_validator.py

class SignalValidator:
    def __init__(self, min_win_prob=0.9, min_risk_reward=1.0, min_confidence=0.9):
        self.min_win_prob = min_win_prob
        self.min_risk_reward = min_risk_reward
        self.min_confidence = min_confidence

    def validate(self, signal):
        # Only pass signals that meet all criteria
        if signal['win_probability'] < self.min_win_prob:
            return False
        if signal['risk_reward'] < self.min_risk_reward:
            return False
        if signal['confidence'] < self.min_confidence:
            return False
        return True