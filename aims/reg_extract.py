#!/usr/bin/python3

from bs4 import BeautifulSoup # type: ignore

with open("/home/jon/proj/aims/registrations.html") as t:
    soup = BeautifulSoup(t, 'html.parser')
    table = soup.find("tbody")
    output = []
    for c, row in enumerate(table.find_all("tr")[2:-1]):
        s = list(row.strings)
        if s[0] == "R" or s[0] == "N": s = s[1:]
        output.append("\"{}\": \"A{}\"".format(s[5], s[7].split("-")[0]))
        if c % 3 == 2:
            output.append(", \n    ")
        else:
            output.append(", ")
    print("".join(output))
