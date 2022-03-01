import argparse
import json
import requests
from bs4 import BeautifulSoup
from scraper import Scraper
from logger import LOGGER

BOSSES_NAMES_FILE = 'bosses_names.txt'


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
                LOGGER.debug('[get_all_bosses_statistics] Error: %s', error)
        return bosses

    def get_statistics_of_boss(self, boss_name):
        bosses = self.get_all_bosses_statistics_objects()
        for boss in bosses:
            if boss.get('name') == boss_name:
                return boss
        return None


def main():
    parser = argparse.ArgumentParser(description='Get kill statistics of a boss or all bosses of a world in Tibia')
    parser.add_argument('--world', dest='tibia_world', type=str, required=True, help='Tibia world')
    parser.add_argument('--boss', dest='boss_name', type=str, required=False, help='Name of the boss (optional)')
    args = parser.parse_args()
    tibia_world = args.tibia_world.capitalize()
    LOGGER.info('Tibia world set to: %s', tibia_world)
    bosses_statistics = BossesStatistics(world=tibia_world)
    if boss_name := args.boss_name:
        boss_statistics = bosses_statistics.get_statistics_of_boss(boss_name)
        if boss_statistics:
            json_formatted_boss_statistics = json.dumps(boss_statistics, indent=4)
            print(json_formatted_boss_statistics)
        else:
            LOGGER.info(f'Boss {boss_name} not found')
    else:
        all_bosses_statistics = bosses_statistics.get_all_bosses_statistics_objects()
        json_all_bosses_statistics = json.dumps(all_bosses_statistics)

        with open(f'bosses_statistics_{tibia_world}.json', 'w+') as json_file:
            json_file.write(json_all_bosses_statistics)
            LOGGER.info('Bosses statistics of world %s saved to bosses_statistics_%s.json', tibia_world, tibia_world)


if __name__ == '__main__':
    main()
