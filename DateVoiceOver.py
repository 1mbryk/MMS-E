import datetime as dt
import pydub as pdub
from pydub.playback import play
import os

HOURS_PATH = 'audio/hours/'
MINUTES_PATH = 'audio/minutes/'
MONTHES_PATH = 'audio/monthes/'
NUMBERS_PATH = 'audio/numbers/'


class DateVoiceOver:
    def __init__(self):
        self.hours = {}
        self.minutes = {}
        self.monthes = {}
        self.numbers = {}
        self.date = ""
        self.time = ""

        def fill_dict(dict, dir: str):
            for path in os.listdir(dir):
                if '.DS_Store' in path:
                    continue
                dict[str(path).removesuffix('.m4a')] = \
                    pdub.AudioSegment.from_file(dir + path)

        fill_dict(self.hours, HOURS_PATH)
        fill_dict(self.minutes, MINUTES_PATH)
        fill_dict(self.monthes, MONTHES_PATH)
        fill_dict(self.numbers, NUMBERS_PATH)

    def __call__(self, use_current_date=True):

        if use_current_date:
            self.__get_current_datetime()
        elif len(self.date) == 0 or len(self.time) == 0:
            self.set_date()
        play(self.__get_audio())

    def set_date(self, day=1, month=1, year=1970, hour=0, minute=0):
        datetime = dt.datetime(day=day, month=month,
                               year=year, hour=hour, minute=minute)
        self.date = datetime.strftime("%d.%m")
        self.time = datetime.strftime("%H:%M")

    def __get_current_datetime(self):
        now = dt.datetime.now()
        self.date = now.strftime("%d.%m")
        self.time = now.strftime("%H:%M")

    def __get_audio(self):
        audio = []
        self.__voice_over_date(audio)
        self.__voice_over_time(audio)

        audio = [self.__delete_silence(x) for x in audio]
        result = audio[0]
        for item in audio[1:]:
            result += item

        return result

    def __voice_over_date(self, audio: list):
        day, month = [int(x) for x in self.date.split('.')]
        # voice over day number
        if day <= 20:
            audio.append(self.numbers[str(day) + 'ое'])
        else:
            audio.append(self.numbers[str(day // 10 * 10)])
            audio.append(self.numbers[str(day % 10)+'ое'])

        # voice over month
        audio.append(self.monthes[str(month)])

    def __voice_over_time(self, audio: list):
        hour, minute = [int(x) for x in self.time.split(':')]

        if hour == 0:
            audio.append(self.numbers['12'])
        else:
            if hour > 20:
                audio.append(self.numbers[str(hour // 10 * 10)])
                hour %= 10
            if hour != 0:
                audio.append(self.numbers[str(hour)])

        if hour < 10 and hour > 20:
            if hour % 10:
                audio.append(self.hours['Час'])
            elif ((hour > 20 or hour < 10) and
                  hour % 10 > 1 and
                  hour % 10 < 5):
                audio.append(self.hours['Часа'])
        else:
            audio.append(self.hours['Часов'])

        # voice over minutes
        if minute >= 20:
            audio.append(self.numbers[str(minute // 10 * 10)])
            minute %= 10

        if minute == 1:
            audio.append(self.numbers['1а'])
            audio.append(self.minutes['Минута'])
        elif minute == 2:
            audio.append(self.numbers['2е'])
            audio.append(self.minutes['Минуты'])
        else:
            if minute != 0:
                audio.append(self.numbers[str(minute)])
            if minute > 0 and minute < 5:
                audio.append(self.minutes['Минуты'])
            else:
                audio.append(self.minutes['Минут'])

    def __detect_leading_silence(self, sound, silence_threshold=-50.0, chunk_size=10):
        '''
        sound is a pydub.AudioSegment
        silence_threshold in dB
        chunk_size in ms

        iterate over chunks until you find the first one with sound
        '''
        trim_ms = 0  # ms

        assert chunk_size > 0  # to avoid infinite loop
        while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
            trim_ms += chunk_size

        return trim_ms

    def __delete_silence(self, sound):
        start_trim = self.__detect_leading_silence(sound)
        end_trim = self.__detect_leading_silence(sound.reverse())

        duration = len(sound)
        return sound[start_trim:duration-end_trim]
