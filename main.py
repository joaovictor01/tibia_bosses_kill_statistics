from typing import Dict

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException

from logger import LOGGER
from scraper import Scraper

app = FastAPI()


class BossesStatistics:
    url = "https://www.tibia.com/community/?subtopic=killstatistics"

    def __init__(self, world):
        self.world = world

    def scrap(self):
        LOGGER.info("Starting to scrap...")
        self.soup = self.get_world_soup()
        self.scraper = Scraper()
        self.scraper.set_soup(self.soup)

    def get_world_soup(self):
        """Return the bossess kill statistics for the specified world."""
        LOGGER.info("Making request and scraping...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
        }
        data = {"world": self.world}
        r = requests.post(self.url, headers=headers, data=data)
        return BeautifulSoup(r.content, "html.parser")

    @staticmethod
    def format_td(string):
        return str(string).replace("&nbsp", "").replace("\u00a0", "")

    def get_all_bosses_statistics_objects(self):
        LOGGER.info(
            "[get_all_bosses_statistics_objects] - Starting to get bosses statistics..."
        )
        bosses = []
        for tr in self.soup.find_all("tr"):
            try:
                boss_name = self.format_td(tr.find("td").string)
                killed_players_last_day = self.format_td(tr.find_all("td")[1].string)
                killed_by_players_last_day = self.format_td(tr.find_all("td")[2].string)
                killed_players_last_week = self.format_td(tr.find_all("td")[3].string)
                killed_by_players_last_week = self.format_td(
                    tr.find_all("td")[4].string
                )
                boss_statistics_object = {
                    "name": boss_name,
                    "killed_players_last_day": killed_players_last_day,
                    "killed_by_players_last_day": killed_by_players_last_day,
                    "killed_players_last_week": killed_players_last_week,
                    "killed_by_players_last_week": killed_by_players_last_week,
                }
                bosses.append(boss_statistics_object)
            except IndexError:
                pass
            except Exception as error:
                LOGGER.debug("[get_all_bosses_statistics] Error: %s", error)
                return []
        return bosses

    def get_statistics_of_boss(self, boss_name: str) -> Dict[str, str]:
        bosses = self.get_all_bosses_statistics_objects()
        for boss in bosses:
            if boss.get("name").lower() == boss_name.lower():
                return boss
        return None


@app.get("/")
def read_root():
    return {"Tibia": "Bosses API"}


@app.get("/world/{world_name}")
def get_bosses_statistics_from_world(world_name: str):
    tibia_world = world_name.capitalize()
    LOGGER.info("Tibia world set to: %s", tibia_world)
    bosses_statistics = BossesStatistics(world=tibia_world)
    bosses_statistics.scrap()
    all_bosses_statistics = bosses_statistics.get_all_bosses_statistics_objects()
    return all_bosses_statistics


@app.get("/world/{world_name}/{boss_name}")
async def get_boss_statistics_world(world_name: str, boss_name: str):
    tibia_world = world_name.capitalize()
    LOGGER.info("Tibia world set to: %s", tibia_world)
    bosses_statistics = BossesStatistics(world=tibia_world)
    bosses_statistics.scrap()
    boss_statistics = bosses_statistics.get_statistics_of_boss(boss_name.capitalize())
    if boss_statistics:
        return boss_statistics
    else:
        LOGGER.info(f"Boss {boss_name.capitalize()} not found")
        raise HTTPException(status_code=404, detail="No boss statistics found.")
