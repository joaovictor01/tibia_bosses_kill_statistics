import os
import sys
import json
import logging
import requests
from bs4 import BeautifulSoup
from scraper import Scraper

BOSSES_NAMES_FILE = 'bosses_names.txt'

LOGGER = logging.getLogger(__name__)
STDOUT_HANDLER = logging.StreamHandler(stream=sys.stdout)
STDOUT_HANDLER.setLevel(logging.DEBUG)
LOGGER.addHandler(STDOUT_HANDLER)
LOGGER.setLevel(logging.INFO)

class BossesStatistics:
    url = 'https://www.tibia.com/community/?subtopic=killstatistics'
    def __init__(self, world):
        self.world = world
        self.soup = self.get_world_soup()
        self.scraper = Scraper()
        self.scraper.set_soup(self.soup)
        super().__init__()
    
    def get_world_soup(self):
        """ Return the bossess kill statistics for the specified world. """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }
        data = {
            'world': self.world
        }
        r = requests.post(self.url, headers=headers, data=data)
        return BeautifulSoup(r.content, 'html.parser')

    def bosses_names(self):
        bosses_names = []
        with open(BOSSES_NAMES_FILE, 'r') as f:
            for line in f.readlines():
                bosses_names.append(line)
        self.bosses_names = bosses_names

    @staticmethod
    def format_td(string):
        return str(string).replace('&nbsp', '').replace('\u00a0', '')

    def get_statistics_table(self):
        return self.scraper.get_first_tag('table')

    def get_all_bosses_statistics_objects(self):
        # table = self.get_statistics_table()
        bosses = []
        for tr in self.soup.find_all('tr'):
            try:
                boss_name = self.format_td(tr.find('td').string)
                killed_players_last_day = self.format_td(tr.find_all('td')[1].string)
                killed_by_players_last_day = self.format_td(tr.find_all('td')[2].string)
                killed_players_last_week = self.format_td(tr.find_all('td')[3].string)
                killed_by_players_last_week = self.format_td(tr.find_all('td')[4].string)
                boss_statistics_object = {
                    'name': boss_name,
                    'killed_players_last_day': killed_players_last_day,
                    'killed_by_players_last_day': killed_by_players_last_day,
                    'killed_players_last_week': killed_players_last_week,
                    'killed_by_players_last_week': killed_by_players_last_week,
                }
                bosses.append(boss_statistics_object)
            except Exception as error:
                LOGGER.debug(error)
        return bosses
    
    def get_statistics_of_boss(self, boss_name):
        bosses = self.get_all_bosses_statistics_objects()
        for boss in bosses:
            if boss.get('name') == boss_name:
                return boss
        return None


def main():
    bosses_statistics_lobera = BossesStatistics(world='Lobera')
    bosses = bosses_statistics_lobera.get_all_bosses_statistics_objects()
    json_bosses = json.dumps(bosses)
    with open('bosses_lobera.json', 'w+') as json_file:
        json_file.write(json_bosses)
    if len(sys.argv) > 1:
        boss_statistics = bosses_statistics_lobera.get_statistics_of_boss(sys.argv[1])
        if boss_statistics:
            json_formatted_boss_statistics = json.dumps(boss_statistics, indent=4)
            print(json_formatted_boss_statistics)


if __name__ == '__main__':
    main()
    