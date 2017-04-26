""" Get data information from assigning family """

import re
import requests

from lxml   import html
from typing import List, Dict


class Family:

    def __init__(self):
        self._url  = "https://www.previred.com/web/previred/indicadores-previsionales"
        self._page = requests.get(self._url)
        self._tree = html.fromstring(self._page.content)

        self._base   = '//*[@id="p_p_id_56_INSTANCE_BAg5Kc9VLFPt_"]/div/div/div[1]/table/tbody/tr['
        self._target = ']/td['

        self._rows    = [3, 4, 5, 6]
        self._columns = [2, 3]

        self._entries = {}

    @property
    def values(self) -> Dict:
        for row in self._rows:
            tramo = self._tree.xpath(self._base + str(row) + self._target + str(1) + ']/text()')

            self._entries[tramo[0]] = self._information(row)

        return self._entries

    def _information(self, row: int) -> List:
        list = []

        for column in self._columns:
            result = self._tree.xpath(self._base + str(row) + self._target + str(column) + ']/strong/text()')

            if column == 2:
                list.append(self._amount(result=result[0]))
            if column == 3:
                list.append(self._requisited(result[0])[0])
                list.append(self._requisited(result[0])[1])

        return list

    def _amount(self, result: str) -> int:
        replace = re.sub("\s", "", result)
        match   = re.match("^[$]([\d]+.[\d]+)$", replace)
        amount  = 0

        if match:
            for group in match.groups():
                amount = int(group.replace(".", ""))
        else:
            amount = 0

        return amount

    def _requisited(self, result: str) -> List:
        list    = []
        replace = re.sub("Renta", "", re.sub("\s", "", result))

        if self._requisitedA(replace=replace):
            list.append(self._requisitedA(replace=replace)[0])
            list.append(self._requisitedA(replace=replace)[1])

        if self._requisitedBC(replace=replace):
            list.append(self._requisitedBC(replace=replace)[0])
            list.append(self._requisitedBC(replace=replace)[1])

        if self._requisitedD(replace=replace):
            list.append(self._requisitedD(replace=replace)[0])
            list.append(self._requisitedD(replace=replace)[1])

        return list

    def _requisitedA(self, replace: str) -> List:
        list  = []
        match = re.match("^(<ó=)[$]([\d]+.[\d]+)$", replace)

        if match is not None:
            for group in match.groups():
                if group is None:
                    continue

                if group == "<ó=":
                    continue

                amount = int(group.replace(".", ""))

                list.append(0)
                list.append(amount)
        return list

    def _requisitedBC(self, replace: str) -> List:
        list  = []
        match = re.match("^(>)[$]([\d]+.[\d]+)(<=)[$]([\d]+.[\d]+)$", replace)

        if match is not None:
            for group in match.groups():
                if group == ">":
                    continue

                if group == "<=":
                    continue

                number = re.match("^([\d]+.[\d]+)$", group)
                if number:
                    list.append(int(number.string.replace(".", "")))
        return list

    def _requisitedD(self, replace: str) -> List:
        list  = []
        match = re.match("^(>)[$]([\d]+.[\d]+)$", replace)

        if match is not None:
            for group in match.groups():
                if group == ">":
                    continue

                list.append(int(group.replace(".", "")))
                list.append(0)
        return list


if __name__ == '__main__':
    family = Family()

    for key, value in family.values.items():
        print(key, value)
