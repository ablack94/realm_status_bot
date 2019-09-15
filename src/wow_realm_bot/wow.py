import logging
import json
from enum import Enum

import requests
import attr
from expiringdict import ExpiringDict


@attr.s
class RealmStatus:
    slug = attr.ib(type=str)
    name = attr.ib(type=str)
    population = attr.ib(type=str)

@attr.s
class RealmStatusMap:
    statuses = attr.ib(factory=list)

    def getAllRealmStatuses(self):
        return list(mapping.values())
    
    def getAllRealmNames(self):
        return [x.name for x in self.mapping.values()]
    
    def getAllRealmSlugs(self):
        return [x.slug for x in self.mapping.values()]
    
    def getStatusBySlug(self, slug):
        status = next((x for x in self.statuses if x.slug == slug), None)
        if status is None:
            raise KeyError(f"No status for slug '{slug}'")
        return status
    
    def getStatusByName(self, name):
        status = next((x for x in self.statuses if x.name.lower() == name.lower()), None)
        if status is None:
            raise KeyError(f"No status for name '{name}'")
        return status


@attr.s
class RealmStatusProvider:
    def _getAllRealmStatuses(self, game_slug):
        url = "https://worldofwarcraft.com/graphql"
        operation = {
            "operationName": "GetInitialRealmStatusData",
            "variables": {"input": {"compoundRegionGameVersionSlug": game_slug}},
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "7b3ba73c1458c52eec129aaf0c64d8be62f5496754f1143f8147da317fdd2417",
                }
            },
        }
        response = requests.post(url, json=operation)
        raw_status = response.json()
        # Get realm status
        statuses = []
        for realm_status in raw_status['data']['Realms']:
            slug = realm_status['slug']
            name = realm_status['name']
            population = realm_status['population']['name']
            statuses.append(RealmStatus(slug, name, population))

        return statuses
    
    def getClassicRealmStatuses(self):
        return RealmStatusMap(self._getAllRealmStatuses('classic-us'))
    
    def getVanillaRealmStatuses(self):
        return RealmStatusMap(self._getAllRealmStatuses('us'))
    
    def getAllRealmStatuses(self):
        return RealmStatusMap(self.getClassicRealmStatuses().statuses + self.getVanillaRealmStatuses().statuses)

@attr.s
class CachedRealmStatusProvider(RealmStatusProvider):
    max_age = attr.ib(type=int)
    cache = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.cache = ExpiringDict(max_len=2, max_age_seconds=self.max_age)
        self.log = logging.getLogger(self.__class__.__name__)

    def getClassicRealmStatuses(self):
        self.log.info("Getting classic realm status")
        statuses = self.cache.get('classic', None)
        if statuses is None:
            self.log.info("Not cached. Fetching...")
            statuses = super().getClassicRealmStatuses()
            self.cache['classic'] = statuses
        else:
            self.log.info("Result cached!")
        self.log.debug(f"Got status {statuses}")
        return statuses
    
    def getVanillaRealmStatuses(self):
        statuses = self.cache.get('vanilla', None)
        if statuses is None:
            statuses = self.cache['vanilla'] = super().getVanillaRealmStatuses()
        return statuses

