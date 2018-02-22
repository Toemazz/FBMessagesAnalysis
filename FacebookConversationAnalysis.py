# https://i.imgur.com/QfbOt87.png
import math
import pickle
import matplotlib.pyplot as plt
from matplotlib import rcParams
from bs4 import BeautifulSoup
from datetime import datetime as dt
from dateutil import relativedelta
from tqdm import tqdm as tq
from collections import Counter
from itertools import groupby

plt.style.use('ggplot')
rcParams.update({'figure.autolayout': True})


class FacebookConversationAnalysis:
    def __init__(self, html_file, get_data=False):
        # Datetime formats
        self.full_date_format = '%A, %d %B %Y at %H:%M %Z'
        self.date_format = '%d/%m/%y'
        self.time_format = '%H:%M'

        pickle_file_names = ['pickles/senders.pickle', 'pickles/messages.pickle',
                             'pickles/dates.pickle', 'pickles/times.pickle']

        if get_data:
            self.extract_data_from_html_file(html_file)
            data = self.extract_data_from_html_file(html_file)

            for n, name in enumerate(pickle_file_names):
                self.save_pickle(data[n], name)
        else:
            data = []
            for name in pickle_file_names:
                data.append(self.load_pickle(name))

        self.data = data
        self.total_msgs = len(self.data[0])

    # Method: Used to 'pickle' a list of data
    @staticmethod
    def save_pickle(data, name):
        with open(name, 'wb') as f:
            pickle.dump(data, f)
        print('[INFO]: {} saved'.format(name))

    # Method: Used to load a 'pickle'
    @staticmethod
    def load_pickle(name):
        with open(name, 'rb') as f:
            print('[INFO]: {} loaded'.format(name))
            return pickle.load(f)

    # Method: Used to extract message data from Facebook HTML file
    def extract_data_from_html_file(self, html_file):
        print('[INFO]: Extracting data from {}'.format(html_file))
        soup = BeautifulSoup(open(html_file, encoding='utf8'), 'lxml')

        users, msgs, dates, times = [], [], [], []

        # Find 'thread' tags
        for thread in soup.find_all(class_='thread'):
            # Find 'message' tags
            for chat in tq(thread.find_all(class_='message'), desc='Chats'):
                # Extract sender and message
                user = str(chat.find(class_='user').string)
                msg = str(chat.next_sibling.string)

                # Extract date and time
                full_date = dt.strptime(chat.find(class_='meta').string.replace("+01", ""), self.full_date_format)
                date = str(full_date.strftime(self.date_format))
                time = str(full_date.strftime(self.time_format))

                users.append(user)
                msgs.append(msg)
                dates.append(date)
                times.append(time)

        print('[INFO]: Data extracted from {}'.format(html_file))
        return [users, msgs, dates, times]

    # Method: Used to calculate the number of messages by each user
    def calculate_total_messages_per_user(self, users):
        msgs_freq = dict(Counter(users))
        unique_users, messages_per_user = zip(*sorted(msgs_freq.items()))

        for i in range(len(unique_users)):
            msgs_percentage = (messages_per_user[i] / self.total_msgs) * 100
            print('[INFO]: Messages sent by {}: {} ({:.2f}%)'.format(unique_users[i], messages_per_user[i], msgs_percentage))

    # Method: Used to calculate the average number of words per message
    def calculate_average_words_per_message(self, msgs):
        total_words = 0

        for msg in msgs:
            total_words += len(msg.split())

        avg_words_per_msg = float(total_words / self.total_msgs)
        print('[INFO]: Average Words/Message: {:.2f}'.format(avg_words_per_msg))

    # Method: Used to calculate the average number of messages per unit time
    def calculate_average_messages_per_unit_time(self, dates, unit_time='day'):
        first_date = dt.strptime(dates[-1], self.date_format)
        last_date = dt.strptime(dates[0], self.date_format)

        delta_dt = last_date - first_date
        delta_du = relativedelta.relativedelta(last_date, first_date)

        if unit_time not in ['day', 'week', 'month', 'year']:
            print('[ERROR]: Please choose a correct value for unit_time')
        else:
            if unit_time == 'day':
                interval = delta_dt.days
            elif unit_time == 'week':
                interval = math.ceil(delta_dt.days / 7)
            elif unit_time == 'month':
                interval = delta_du.years*12 + delta_du.months
            else:
                interval = delta_du.years

            avg_messages_per_day = float(self.total_msgs / interval)
            print('[INFO]: Average Messages/{}: {:.2f}'.format(unit_time.title(), avg_messages_per_day))

    # Method: Used to find the day with most
    @staticmethod
    def find_most_active_day(dates):
        dates_freq = dict(Counter(dates))

        date = max(dates_freq, key=dates_freq.get)
        num_msgs = max(dates_freq.values())
        seconds_per_msg = 86400 / num_msgs

        print('[INFO]: Most active day was {} with {} messages sent. Thats a message every {:.2f} seconds!'
              .format(date, num_msgs, seconds_per_msg))

    # Method: Used to plot the total messages per hour
    def plot_total_msgs_per_hour(self, times, title, x_label, y_label):
        times = sorted(times)
        msgs_per_hour, hours = [], []

        # Group by hour
        for key, group in groupby(times, key=lambda x: x[:2]):
            msgs_per_hour.append(len(list(group)))
            hours.append(key)

        # Plot number of total messages per hour
        plt.plot(range(len(msgs_per_hour)), msgs_per_hour)
        plt.xticks(range(len(hours)), hours)
        plt.xlim([0, len(hours)-1])
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.show()


if __name__ == '__main__':
    # Create instance and get data
    fb = FacebookConversationAnalysis('171.html')
    fb_data = fb.data

    # Split data
    users, msgs, dates, times = fb_data[0], fb_data[1], fb_data[2], fb_data[3]

    # Calculate some statistics
    # fb.calculate_total_messages_per_user(users)
    # fb.calculate_average_words_per_message(msgs)
    # fb.calculate_average_messages_per_unit_time(dates, 'day')
    # fb.calculate_average_messages_per_unit_time(dates, 'week')
    # fb.calculate_average_messages_per_unit_time(dates, 'month')
    # fb.calculate_average_messages_per_unit_time(dates, 'year')
    # fb.find_most_active_day(dates)

    # Plot some graphs
    fb.plot_total_msgs_per_hour(times, 'Messages/Hour', 'Hour', '# Messages')
