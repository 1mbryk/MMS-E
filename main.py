from DateVoiceOver import DateVoiceOver
if __name__ == '__main__':
    dvo = DateVoiceOver()
    dvo.set_date(16, 1, 2024, 3, 20)
    dvo(True)
