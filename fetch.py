# Copyright 2020 Lin Wang
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env python3

import requests
import json
import difflib
import pandas as pd
import sys


def print_text(name_authors, title, name_venue,
                acr_venue, volume, number, pages, year):
  
  for name in name_authors:
    print(name, end='')
    if name != name_authors[-1]:
      print(', ', end='')
    else:
      print('. ', end='')
  print(title + '. ', end='')
  print(name_venue, end='')
  print(' (' + acr_venue + '), ', end='')
  if volume != None:
    print('vol. ' + volume, end='')
  if number != None:
    print('(' + number + '), ', end='')
  print('pp. ' + pages + ', ', end='')
  print(year + '.')


def print_bib(type_pub, name_authors, title, name_venue,
              acr_venue, volume, number, pages, year):
  
  if type_pub == 1:
    print('@inproceedings{REF_NAME,')
  if type_pub == 2:
    print('@article{REF_NAME,')
  print('  authors = {', end='')
  for name in name_authors:
    if name == name_authors[0]:
      print(name + ' and')
    elif name != name_authors[-1]:
      print('             ' + name + ' and')
    else:
      print('             ' + name + '},')
  print('  title = {' + title + '}',)
  if type_pub == 1:
    print('  booktitle = {' + name_venue + ' (' + acr_venue + ')' + '},')
  if type_pub == 2:
    print('  journal = {' + name_venue + ' (' + acr_venue + ')' + '},')
    print('  volume = {' + volume + '},')
    print('  number = {' + number + '},')
  print('  pages = {' + pages + '},')
  print('  year = {' + year + '}')
  print('}')
  
    


def inquire_dblp(keyword):

  # read journal list
  with open('journals.csv', 'r') as file_journals:
    df_journals = pd.read_csv(file_journals).T
    name_journals = list(df_journals.values[0])
    acr_journals = list(df_journals.values[1])

  # read conference list
  with open('conferences.csv', 'r') as file_conferences:
    df_conferences = pd.read_csv(file_conferences).T
    name_conferences = list(df_conferences.values[0])
    acr_conferences = list(df_conferences.values[1])


  api_pub = "http://dblp.org/search/publ/api"
  req_url = api_pub + '?q=' + keyword + '&format=json'

  req = requests.get(req_url)
  tab_hits = req.json()['result']['hits']['hit']

  # with open('res_dblp.json', 'w') as file_res:
  #   json.dump(tab_hits, file_res)

  # conference: 1, journal: 2
  type_pub = 0

  for hit in tab_hits:

    item = hit['info']

    if item['type'] == "Conference and Workshop Papers":
      type_pub = 1
    elif item['type'] == "Journal Articles":
      type_pub = 2
    else:
      continue

    # authors list
    if 'authors' in item:
      authors = item['authors']
    else:
      continue

    list_authors = authors['author']
    name_authors = []
    for author in list_authors:
      name = author['text'].rstrip('0123456789 ')
      name_authors.append(name)

    # title
    title = item['title'].capitalize().replace(' -', ':')[:-1]

    # venue
    venue = item['venue']

    if type_pub == 1:
      match = difflib.get_close_matches(venue, acr_conferences)[0]
      index = acr_conferences.index(match)
      name_venue = name_conferences[index]
      acr_venue = match
    
    volume = None
    number = None
    if type_pub == 2:
      match = difflib.get_close_matches(venue, name_journals)[0]
      index = name_journals.index(match)
      name_venue = match
      acr_venue = acr_journals[index]
      volume = item['volume']
      number = item['number']

    
    pages = item['pages']
    year = item['year']
    
    print_text(name_authors,title,name_venue,acr_venue,volume,number,pages,year)
    print_bib(type_pub, name_authors,title,name_venue,acr_venue,volume,number,pages,year)
    

if __name__ == "__main__":
    inquire_dblp(sys.argv[1])