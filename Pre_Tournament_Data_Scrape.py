#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 19:11:27 2020

@author: ryansalsbury
"""
#import libraries
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
    
from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import pandas as pd
import re


########## get all schools ##########
url = "https://www.sports-reference.com/cbb/seasons/" + str(2020) + "-school-stats.html"
page = urlopen(url).read()
#print(page)
soup = BeautifulSoup(page)
count  = 0
table = soup.find("tbody")
school_dict = dict()
for row in table.findAll('td', {"data-stat": "school_name"}):
    school_name = row.getText()
    for a in row.find_all('a', href=True):
        link = a['href'].strip()
        name = link[13:].split("/")[0]
        school_dict[name] = school_name
        
        


########## get rosters and total player stats for each season ##########
roster_df_all=pd.DataFrame()
totals_df_all=pd.DataFrame()

season = ['2019']
for s in season:
    for school in school_dict:
        url = "https://www.sports-reference.com/cbb/schools/" + school + "/" + str(s) + ".html"
        try:
            urllib2.urlopen(url)
        except HTTPError as err:
            if err.code == 404:
                continue
        page = urlopen(url).read()
        soup = BeautifulSoup(page)
        count = 0 
            
#get totals table    
        table = soup.find_all('div', {'id':'all_totals'}, {'class':'table_wrapper setup_commented commented'})[0]
        comment = table(text=lambda x: isinstance(x, Comment))[0]
        newsoup = BeautifulSoup(comment, 'html.parser')
        table = newsoup.find('table')
        totals_body = table.find("tbody")
        totals_rows = totals_body.find_all('tr')

        totals_dict={}
        totals_cols = {'player','g', 'mp', 'pts'}

        for row in totals_rows:
            if (row.find('th', {"scope":"row"}) != None):
                for t in totals_cols:
                    if t == 'player':
                        cell = row.find("td",{"data-stat": t})
                        a = cell.text.strip().encode()
                        text=a.decode("utf-8")
                        href = row.find("a").attrs['href']
                        player_id = re.findall(r'(?<=cbb/players/)(.*)(?=\.html)', href)[0]
                        if t in totals_dict:
                            totals_dict[t].append(text)
                            totals_dict['player_id'].append(player_id)
                        else: 
                            totals_dict[t] = [text]
                            totals_dict['player_id'] = [player_id]
                    else:
                        cell = row.find("td",{"data-stat": t})
                        a = cell.text.strip().encode()
                        text=a.decode("utf-8")
                        if t in totals_dict:
                            totals_dict[t].append(text)
                        else:
                            totals_dict[t]=[text]
                            totals_dict['season'] = s
                            totals_dict['url_school'] = school
                            totals_dict['school'] = school_dict[school]
                            
        
        totals_df = pd.DataFrame.from_dict(totals_dict)
        totals_df_all=pd.concat([totals_df_all,totals_df])
            
#get roster table    
        roster_table = soup.find_all("table", id="roster")
        roster_body = roster_table[0].find("tbody")    
        roster_dict = {}
        roster_cols = {'player', 'rsci'}
            
        roster_rows = roster_body.find_all('tr')
        for row in roster_rows:
            if (row.find('th', {"scope":"row"}) != None):
                for r in roster_cols:
                    if r == 'player':
                        cell = row.find("th",{"data-stat": r})
                        a = cell.text.strip().encode()
                        text=a.decode("utf-8")
                        href = row.find("a").attrs['href']
                        player_id = re.findall(r'(?<=cbb/players/)(.*)(?=\.html)', href)[0]
                        if r in roster_dict:
                            roster_dict[r].append(text)
                            roster_dict['player_id'].append(player_id)
                        else:
                                roster_dict[r]=[text]
                                roster_dict['player_id'] = [player_id]
                                roster_dict['season'] = s
                                roster_dict['url_school'] = school
                                roster_dict['school'] = school_dict[school]
                    else:
                        if (row.find("td",{"data-stat": r}) != None):
                            cell = row.find("td",{"data-stat": r})
                            a = cell.text.strip().encode()
                            text=a.decode("utf-8")
                            if r in roster_dict:
                                roster_dict[r].append(text)
                            else:
                                roster_dict[r]=[text]
                        else:
                            roster_dict[r]= 'NA'
        roster_df = pd.DataFrame.from_dict(roster_dict)
        roster_df_all=pd.concat([roster_df_all,roster_df])
 
#export to csv               
#roster_df_all.to_csv("roster_2019.csv", index=False)         
#totals_df_all.to_csv("totals_2019.csv", index=False)   



########### get tournament player data by season ##########
tourney_df_all=pd.DataFrame()       
for r in range(0, 8400, 100):          
    url = "https://www.sports-reference.com/cbb/play-index/tourney_pgl_finder.cgi?request=1&match=single&year_min=2008&year_max=2019&round=&school_id=&opp_id=&person_id=&game_month=&game_result=&is_starter=&pos_is_g=Y&pos_is_gf=Y&pos_is_f=Y&pos_is_fg=Y&pos_is_fc=Y&pos_is_c=Y&pos_is_cf=Y&c1stat=&c1comp=&c1val=&c2stat=&c2comp=&c2val=&c3stat=&c3comp=&c3val=&c4stat=&c4comp=&c4val=&is_dbl_dbl=&is_trp_dbl=&order_by=mp&order_by_asc=&offset=" + str(r) +""
    page = urlopen(url).read()
    soup = BeautifulSoup(page)
    count  = 0
    body = soup.find("tbody")
    tourney_rows = body.find_all('tr')

    tourney_dict={}
    tourney_cols = {'player', 'school_name', 'year_id', 'mp', 'pts'}

    for row in tourney_rows:
        if (row.find('th', {"scope":"row"}) != None):
            for t in tourney_cols:
                if t == 'player':
                    cell = row.find("td",{"data-stat": t})
                    a = cell.text.strip().encode()
                    text=a.decode("utf-8")
                    href = row.find("a").attrs['href']
                    player_id = re.findall(r'(?<=cbb/players/)(.*)(?=\.html)', href)[0]
                    if t in tourney_dict:
                        tourney_dict[t].append(text)
                        tourney_dict['player_id'].append(player_id)
                    else: 
                        tourney_dict[t] = [text]
                        tourney_dict['player_id'] = [player_id]
                elif t == 'school_name':
                    if (row.find('th', {"scope":"row"}) != None):
                        cell = row.find("td",{"data-stat": t})
                        a = cell.text.strip().encode()
                        text1=a.decode("utf-8")
                        href = cell.find("a").attrs['href']
                        text2 = re.findall(r'(?<=cbb/schools/)(.*)(?=\/)', href)[0]
                        if t in tourney_dict:
                            tourney_dict[t].append(text1)
                            tourney_dict['url_school'].append(text2)
                        else:
                            tourney_dict[t] = [text1]
                            tourney_dict['url_school'] = [text2]
                else:
                    cell = row.find("td",{"data-stat": t})
                    a = cell.text.strip().encode()
                    text=a.decode("utf-8")
                    if t in tourney_dict:
                        tourney_dict[t].append(text)
                    else: 
                        tourney_dict[t] = [text]
            
    tourney_df = pd.DataFrame.from_dict(tourney_dict)
    tourney_df_all=pd.concat([tourney_df_all,tourney_df])

#export to csv
#tourney_df_all.to_csv("tourney_df_all_2008_2019.csv", index=False)   
 

########## get coaches by season ##########  
coaches_df_all=pd.DataFrame()  
for s in range(1975, 2020, 1):
    url = "https://www.sports-reference.com/cbb/seasons/" + str(s) + "-coaches.html"   
    page = urlopen(url).read()          
    soup = BeautifulSoup(page)

    table = soup.find_all("table", id="coaches")[0]
    body = table.find_all("tbody")


    rows = body[0].find_all('tr')
    coach_dict = {}
    cols = {'coach', 'school', 'since_cur_schl', 'ap_pre', 'tourney_note', 'w_car', 'l_car', 'ncaa_apps_car', 'sweet16_apps_car','final4_apps_car', 'natl_champs_car'}
    for row in rows:
        for c in cols:
            if c == 'coach':
                if (row.find('th', {"scope":"row"}) != None):
                    cell = row.find("th",{"data-stat": c})
                    a = cell.text.strip().encode()
                    text1=a.decode("utf-8")
                    href = cell.find("a").attrs['href']
  
                    text2 = re.findall(r'(?<=cbb/coaches/)(.*)(?=\.html)', href)[0]
                    if c in coach_dict:
                        coach_dict[c].append(text1)
                        coach_dict['coach_id'].append(text2)
                    else:
                        coach_dict[c] = [text1]
                        coach_dict['coach_id'] = [text2]
            elif c == 'school':
                if (row.find('th', {"scope":"row"}) != None):
                    cell = row.find("td",{"data-stat": c})
                    a = cell.text.strip().encode()
                    text1=a.decode("utf-8")
                    href = cell.find("a").attrs['href']
                    text2 = re.findall(r'(?<=cbb/schools/)(.*)(?=\/)', href)[0]
                    if c in coach_dict:
                        coach_dict[c].append(text1)
                        coach_dict['url_school'].append(text2)
                        
                    else:
                        coach_dict[c] = [text1]
                        coach_dict['url_school'] = [text2]
                        
            else:
                if (row.find('th', {"scope":"row"}) != None):
                    cell = row.find("td",{"data-stat": c})
                    a = cell.text.strip().encode()
                    text= a.decode("utf-8")
                    if c in coach_dict:
                        coach_dict[c].append(text)
                    else:
                        coach_dict[c] = [text]
                        coach_dict['season'] = s
    coaches_df = pd.DataFrame.from_dict(coach_dict) 
    coaches_df_all=pd.concat([coaches_df_all,coaches_df])

#coaches_df_all.to_csv("coaches_1975_2019.csv", index=False)   


########## get tournament results/location ##########  
games_df_all=pd.DataFrame()  
for r in range(0, 1600, 100):
    url = "https://www.sports-reference.com/cbb/play-index/tourney.cgi?request=1&match=single&year_min=2008&year_max=&round=&region=&location=&school_id=&conf_id=&opp_id=&opp_conf=&seed=&seed_cmp=eq&opp_seed=&opp_seed_cmp=eq&game_result=&pts_diff=&pts_diff_cmp=eq&order_by=date_game&order_by_single=date_game&order_by_combined=g&order_by_asc=&offset=" + str(r) +""   
    #url = "https://www.sports-reference.com/cbb/play-index/tourney.cgi?request=1&match=single&year_min=2008&year_max=&round=&region=&location=&school_id=&conf_id=&opp_id=&opp_conf=&seed=&seed_cmp=eq&opp_seed=&opp_seed_cmp=eq&game_result=&pts_diff=&pts_diff_cmp=eq&order_by=date_game&order_by_single=date_game&order_by_combined=g&order_by_asc=&offset=0"
    page = urlopen(url).read()          
    soup = BeautifulSoup(page)

    count  = 0
    body = soup.find("tbody")
    games_rows = body.find_all('tr')

    games_dict={}
    games_cols = {'year_id', 'region', 'round', 'school_name', 'pts', 'opp_name', 'opp_pts', 'overtimes', 'pts_diff', 'location'}
    t = 'school_name'
    for row in games_rows:
        if (row.find('th', {"scope":"row"}) != None):
            for t in games_cols:
                if t == 'school_name':
                    cell = row.find("td",{"data-stat": t})
                    seed = cell.get_text().split()[0]
                    href = cell.find_all("a")[0]
                    text1 = href.text
                    href2 = href.attrs['href']
                    text2 = re.findall(r'(?<=cbb/schools/)(.*)(?=\/)', href2)[0]
                    if 'school' in games_dict:
                        games_dict['school'].append(text1)
                        games_dict['url_school'].append(text2)
                        games_dict['seed'].append(seed)
                    else: 
                        games_dict['school'] = [text1]
                        games_dict['url_school'] = [text2]
                        games_dict['seed'] = [seed]
                elif t == 'opp_name':
                    if (row.find('th', {"scope":"row"}) != None):
                        cell = row.find("td",{"data-stat": t})
                        opp_seed = cell.get_text().split()[0]
                        href = cell.find_all("a")[0]
                        text1 = href.text
                        href2 = href.attrs['href']
                        text2 = re.findall(r'(?<=cbb/schools/)(.*)(?=\/)', href2)[0]
                        if 'opp_school' in games_dict:
                            games_dict['opp_school'].append(text1)
                            games_dict['opp_url_school'].append(text2)
                            games_dict['opp_seed'].append(opp_seed)
                        else:
                            games_dict['opp_school'] = [text1]
                            games_dict['opp_url_school'] = [text2]
                            games_dict['opp_seed'] = [opp_seed]
                else:
                    cell = row.find("td",{"data-stat": t})
                    a = cell.text.strip().encode()
                    text=a.decode("utf-8")
                    if t in games_dict:
                        games_dict[t].append(text)
                    else: 
                        games_dict[t] = [text]
            
    games_df = pd.DataFrame.from_dict(games_dict)
    games_df_all=pd.concat([games_df_all,games_df])

#export to csv
#games_df_all.to_csv("games_2008_2019.csv", axis=False)     
    
    
########## get school locations ##########
url = "https://www.sports-reference.com/cbb/schools/"    
page = urlopen(url).read()          
soup = BeautifulSoup(page)
count  = 0
body = soup.find("tbody")
school_rows = body.find_all('tr')

school_loc_dict={}
school_loc_cols = {'school_name', 'location'}

for row in school_rows:
    if (row.find('th', {"scope":"row"}) != None):
        for t in school_loc_cols:
            if t == 'school_name':
                cell = row.find("td",{"data-stat": t})
                href = cell.find_all("a")[0]
                text1 = href.text
                href2 = href.attrs['href']
                text2 = re.findall(r'(?<=cbb/schools/)(.*)(?=\/)', href2)[0]
                if 'school' in school_loc_dict:
                    school_loc_dict['school'].append(text1)
                    school_loc_dict['url_school'].append(text2)
                else: 
                    school_loc_dict['school'] = [text1]
                    school_loc_dict['url_school'] = [text2]
            else:
                cell = row.find("td",{"data-stat": t})
                a = cell.text.strip().encode()
                text=a.decode("utf-8")
                if t in school_loc_dict:
                    school_loc_dict[t].append(text)
                else: 
                    school_loc_dict[t] = [text]
            

school_loc_df = pd.DataFrame.from_dict(school_loc_dict)


#export to csv
#school_loc_df.to_csv("school_loc.csv", index=False)



################Scrape Player Win Shares##############

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
    
 
import urllib.parse   
from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import pandas as pd
import re


url = "https://basketball.realgm.com/ncaa/tournaments/Post-Season/NCAA-Tournament/1/teams"
page = urlopen(url).read()
soup = BeautifulSoup(page)
table = soup.find("tbody")
school_names = []
school_ids = []
conference_names = []
conference_ids = []
tournaments = []
for row in table.findAll('tr'):
    school_name = row.findAll('a')[0].text
    school_id = str(row.findAll('a')[0]).split('/')[6]
    conference_name = str(row.findAll('a')[0]).split('/')[3]
    conference_id = str(row.findAll('a')[0]).split('/')[4]
    school_names.append(school_name)
    conference_names.append(conference_name)
    school_ids.append(school_id)
    conference_ids.append(conference_id)
    tourn_seasons = []
    for row in row.findAll('a')[1:]:
        tourn_seasons.append(row.text.split('-')[1])
    tournaments.append(tourn_seasons)    

#school_df = pd.DataFrame.from_dict(school_dict)


####get schools duplicated for each tournament season    
snames = []
sids = []
cnames = []  
cids = [] 
seasons = []
 
  
for (school_name, school_id, conference_name ,conference_id, tournament) in zip(school_names, school_ids, conference_names, conference_ids, tournaments):
    for year in tournament:
        snames.append(school_name)
        seasons.append(year)
        sids.append(school_id)
        cnames.append(conference_name) 
        cids.append(conference_id) 

school_tournaments = pd.DataFrame(list(zip(snames, sids, cnames, cids, seasons)), 
               columns =['school', 'school_id', 'conference', 'conference_id', 'Season'])  

###########full win share scrape
win_shares = {}
for (school_id, school_name, conference_id, conference_name, year) in zip(sids, snames, cids, cnames, seasons):
    if year in ['2013', '2014', '2015', '2016', '2017', '2018', '2019']:
        try:
            school = urllib.parse.quote(school_name)
            url = "https://basketball.realgm.com/ncaa/conferences/" + conference_name + "/" + conference_id + "/" + school + "/" + school_id +  "/stats/" + year + "/Misc_Stats/All/All/Season/All/per/desc/1/"   
            page = urlopen(url).read()
            soup = BeautifulSoup(page)
            try:
                table = soup.find("tbody")
            except(TypeError, KeyError) as e:
                table = soup.find("tbody")
            for row in table.findAll('tr'):
                player = row.find_all('td')[1].text
                player_id = str(row.find_all('a')).split('/')[4].split('">')[0]
                win_share = row.find_all('td')[-1].text
                if len(win_shares) >= 6:
                    win_shares['year'].append(year)
                    win_shares['player'].append(player)
                    win_shares['player_id'].append(player_id)
                    win_shares['school_id'].append(school_id)
                    win_shares['school_name'].append(school_name)
                    win_shares['win_shares'].append(win_share)
                else:
                    win_shares['year'] = [year]
                    win_shares['player'] = [player]
                    win_shares['player_id'] = [player_id]
                    win_shares['school_id'] = [school_id]
                    win_shares['school_name'] = [school_name]
                    win_shares['win_shares'] = [win_share]
        except ConnectionResetError:
            print('Handle Exception')
            
win_share_df = pd.DataFrame.from_dict(win_shares)
win_shares = win_share_df.drop_duplicates()
win_share_df['win_shares'] = win_share_df['win_shares'].astype(float)
    


#get tournament win shares
tourn_win_shares = {}
for (school_id, school_name, conference_id, conference_name, year) in zip(sids, snames, cids, cnames, seasons):
    if year in ['2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']:
        try:
            school = urllib.parse.quote(school_name)
            url = "https://basketball.realgm.com/ncaa/conferences/" + conference_name + "/" + conference_id + "/" + school + "/" + school_id +  "/stats/" + year + "/Misc_Stats/All/All/Post-Season_NCAA_Tournament/All/desc/1/"   
            page = urlopen(url).read()
            soup = BeautifulSoup(page)
            try:
                table = soup.find("tbody")
            except(TypeError, KeyError) as e:
                table = soup.find("tbody")
            for row in table.findAll('tr'):
                player = row.find_all('td')[1].text
                player_id = str(row.find_all('a')).split('/')[4].split('">')[0]
                win_share = row.find_all('td')[-1].text
                if len(tourn_win_shares) >= 6:
                    tourn_win_shares['year'].append(year)
                    tourn_win_shares['player'].append(player)
                    tourn_win_shares['player_id'].append(player_id)
                    tourn_win_shares['school_id'].append(school_id)
                    tourn_win_shares['school_name'].append(school_name)
                    tourn_win_shares['win_shares'].append(win_share)
                else:
                    tourn_win_shares['year'] = [year]
                    tourn_win_shares['player'] = [player]
                    tourn_win_shares['player_id'] = [player_id]
                    tourn_win_shares['school_id'] = [school_id]
                    tourn_win_shares['school_name'] = [school_name]
                    tourn_win_shares['win_shares'] = [win_share]
        except ConnectionResetError:
            print('Handle Exception')
            
tourn_win_share_df = pd.DataFrame.from_dict(tourn_win_shares)
tourn_win_share_df = tourn_win_share_df.drop_duplicates()
tourn_win_share_df['win_shares'] = tourn_win_share_df['win_shares'].astype(float)            

player_win_shares = pd.merge(win_share_df, tourn_win_share_df, how = "left", on=['player_id', 'school_id', 'year'], suffixes=['', '_tourn'])

player_win_shares = player_win_shares.drop(['player_tourn', 'school_name_tourn'], axis=1)

player_win_shares['win_shares_tourn'] = player_win_shares['win_shares_tourn'].fillna(0)

player_win_shares['win_shares'] = player_win_shares['win_shares'] - player_win_shares['win_shares_tourn']
player_win_shares = player_win_shares.drop(['win_shares_tourn'], axis=1)

player_win_shares['win_shares'] = player_win_shares['win_shares'].astype(float) 

#write to csv
player_win_shares.to_csv("player_win_shares.csv", index=False) 

########## Manipulate Data ##########

#read in data files

#rosters    
#roster_2020 = pd.read_csv("roster_2020.csv", na_values=['NA'])
roster_2019 = pd.read_csv("roster_2019.csv", na_values=['NA'])
roster_2018 = pd.read_csv("roster_2018.csv", na_values=['NA'])
roster_2017 = pd.read_csv("roster_2017.csv", na_values=['NA'])
roster_2016 = pd.read_csv("roster_2016.csv", na_values=['NA'])
roster_2015 = pd.read_csv("roster_2015.csv", na_values=['NA'])
roster_2014 = pd.read_csv("roster_2014.csv", na_values=['NA'])
roster_2013 = pd.read_csv("roster_2013.csv", na_values=['NA'])
roster_2012 = pd.read_csv("roster_2012.csv", na_values=['NA'])
roster_2011 = pd.read_csv("roster_2011.csv", na_values=['NA'])
roster_2010 = pd.read_csv("roster_2010.csv", na_values=['NA'])
roster_2009 = pd.read_csv("roster_2009.csv", na_values=['NA'])
roster_2008 = pd.read_csv("roster_2008.csv", na_values=['NA'])
roster_2007 = pd.read_csv("roster_2007.csv", na_values=['NA'])

#player totals
#totals_2020 = pd.read_csv("totals_2020.csv", na_values=['NA'])
totals_2019 = pd.read_csv("totals_2019.csv", na_values=['NA'])
totals_2018 = pd.read_csv("totals_2018.csv", na_values=['NA'])
totals_2017 = pd.read_csv("totals_2017.csv", na_values=['NA'])
totals_2016 = pd.read_csv("totals_2016.csv", na_values=['NA'])
totals_2015 = pd.read_csv("totals_2015.csv", na_values=['NA'])
totals_2014 = pd.read_csv("totals_2014.csv", na_values=['NA'])
totals_2013 = pd.read_csv("totals_2013.csv", na_values=['NA'])
totals_2012 = pd.read_csv("totals_2012.csv", na_values=['NA'])
totals_2011 = pd.read_csv("totals_2011.csv", na_values=['NA'])
totals_2010 = pd.read_csv("totals_2010.csv", na_values=['NA'])
totals_2009 = pd.read_csv("totals_2009.csv", na_values=['NA'])
totals_2008 = pd.read_csv("totals_2008.csv", na_values=['NA'])
totals_2007 = pd.read_csv("totals_2007.csv", na_values=['NA'])
#tourney player totals - rename year_id to season, school_name to school and pts/mp to tourn_pts, tourn_mp
tourney_player_totals = pd.read_csv("tourney_2008_2019.csv")
tourney_player_totals = tourney_player_totals.rename({'year_id': 'season', 'school_name': 'school', 'pts': 'tourn_pts', 'mp': 'tourn_mp'}, axis=1)

#coaches
coaches = pd.read_csv("coaches_1975_2019.csv")
coaches['since_cur_schl'] = coaches['since_cur_schl'].str.replace('-\d+', '')

#only get one coach per school per year
#remove mike hopkins as interim coach when Boeheim got suspended
coaches = coaches[~((coaches['coach_id'] == 'mike-hopkins-1') & (coaches['url_school'] == 'syracuse'))] 


coaches_subset = coaches[['season', 'url_school', 'since_cur_schl', 'coach_id']]
coaches_subset = coaches_subset.groupby(['season','url_school']).max().reset_index()

#confirm that each season/school only has one coach
coaches_subset.groupby(['season','url_school']).size().sort_index(ascending=True)

#join to coaches
coaches = pd.merge(coaches_subset, coaches, how='left',on=['url_school', 'season', 'coach_id'], suffixes=('', '_y'))

#drop extra column from merge
coaches = coaches.drop('since_cur_schl_y', axis=1)


#games - rename year_id to season
games = pd.read_csv("games_2008_2019.csv")
games = games.rename({'year_id': 'season'}, axis=1)

#states abbreviations file to convert game locations
states = pd.read_csv("states.csv")


#school locations
school_loc = pd.read_csv("school_loc.csv")
#some schools have the wrong city or spelled differently than cities table, so need to update them to be able to join to cities table
school_loc['location'] = school_loc['location'].replace({'Villanova, Pennsylvania': 'Philadelphia, Pennsylvania', 
                                 'Mississippi State, Mississippi': 'Starkville, Mississippi', 
                                 'University, Mississippi': 'Oxford, Mississippi', 
                                 'St. Bonaventure, New York': 'Allegany, New York',
                                 'Washington, D.C.': 'Washington, District of Columbia',
                                 'University Park, Pennsylvania': 'State College, Pennsylvania'
                                 })
    
#cities file with lat long coordninates
cities = pd.read_csv("worldcities.csv")

#kaggle school spellings - need to specify encoding as it had a decoding error
school_spellings = pd.read_csv("MTeamSpellings.csv", encoding = "ISO-8859-1")
#rename columns
school_spellings = school_spellings.rename({'TeamNameSpelling': 'school_spelling', 'TeamID': 'team_id'}, axis=1)
school_spellings['school_spelling'] = school_spellings['school_spelling'].str.replace('chicago-st', 'chicago-state')

#T-Rank Stats
trank_november = pd.read_csv("trank_november.csv")
trank_december = pd.read_csv("trank_december.csv")
trank_january = pd.read_csv("trank_january.csv")
trank_febmarch = pd.read_csv("trank_febmarch.csv")
trank_all = pd.read_csv("trank_fullseason.csv")




#combine all roster and totals data into 2 separate data frames (1 for all roster data & 1 for all totals data)
#create list of all rosters
roster_list = [roster_2019, roster_2018, roster_2017, 
           roster_2016, roster_2015, roster_2014, roster_2013, 
           roster_2012, roster_2011, roster_2010, roster_2009, 
           roster_2008, roster_2007]

#create list of all totals
totals_list = [totals_2019, totals_2018, totals_2017, 
           totals_2016, totals_2015, totals_2014, totals_2013, 
           totals_2012, totals_2011, totals_2010, totals_2009, 
           totals_2008, totals_2007]

#combine all
rosters = pd.concat(roster_list)
totals = pd.concat(totals_list)

#grab just the ranking from rsci rosters column and remove the (year)
#convert null values to 0
rosters['rsci'] = rosters['rsci'].fillna(0).astype(str)

#create function to split on comma, reverse string list, and return just the ranking
#this was because I wanted the second ranking for players with multiple rankings
def clean_ranking(x):
        return x.split(',')[::-1][0].split()[0]

rosters['rsci'] = rosters['rsci'].apply(clean_ranking)

#convert to int
rosters['rsci'] = rosters['rsci'].astype(int)

#check if duplicates
rosters.duplicated(['player', 'season', 'url_school']).sum()
totals.duplicated(['player', 'season', 'url_school']).sum()

#3 duplicates in each. Let's see what they are
rosters[rosters.duplicated(['player', 'season', 'url_school'])]
totals[totals.duplicated(['player', 'season', 'url_school'])]

#the duplicate rows have incorrectly formatted player_id's (lastname-firstname instead of firstname-lastname or 2 instead of 1)
#These can be removed from the rosters
rosters = rosters[rosters['player_id'] != 'funtarov-georgi-1']
rosters = rosters[rosters['player_id'] != 'battle-joseph-1']
rosters = rosters[rosters['player_id'] != 'anthony-horton-2']

#for totals, I will combine the rows into one by renaming each player_id and adding the totals
totals['player_id'] = totals['player_id'].replace('funtarov-georgi-1', 'georgi-funtarov-1').replace('battle-joseph-1', 'joseph-battle-1').replace('anthony-horton-2', 'anthony-horton-1')
totals = totals.groupby(['player_id','player', 'season', 'url_school', 'school']).sum().reset_index()
#totals = totals.drop_duplicates(['player', 'season', 'url_school'])

#join the two data frames together.
rosters_totals = pd.merge(rosters, totals, how='left', on=['player_id', 'player', 'url_school', 'school', 'season']) 

#need to rename a player who has a new id and is different from id in tournament data
rosters_totals['player_id'] = rosters_totals['player_id'].replace('anthony-oliverii-1', 'aj-oliverii-1')

#join to tourney data to get pre tourney totals
rosters_totals = pd.merge(rosters_totals, tourney_player_totals, how='left',on=['player_id', 'url_school', 'school', 'season'], suffixes=('', '_y'))

#drop additional player column that was created during the merge
rosters_totals = rosters_totals.drop('player_y', axis=1)

#fill null values with 0 in tourn_pts and tourn_mp 
rosters_totals['tourn_mp'] = rosters_totals['tourn_mp'].fillna(0)
rosters_totals['tourn_pts'] = rosters_totals['tourn_pts'].fillna(0)

#subtract tournament stats from season stats
rosters_totals['mp'] = rosters_totals['mp'] - rosters_totals['tourn_mp']
rosters_totals['pts'] = rosters_totals['pts'] - rosters_totals['tourn_pts']

#create new table to work with in calculating rating for team recruiting weighted by minutes
rsci_rosters_totals = rosters_totals

#calculate team recruiting ranking
#reverse numbers for rsci column so that 100 is best rating and 1 is worst
rsci_rosters_totals['rsci'] = (rsci_rosters_totals['rsci']-101).abs()
    
#replace all values of 101 with 0
rsci_rosters_totals.loc[rsci_rosters_totals['rsci']== 101, 'rsci'] = 0

#multiply rsci by mp
rsci_rosters_totals['rsci_mp'] = rsci_rosters_totals['rsci'] * rsci_rosters_totals['mp']

#group by school/season and sum the rsci_mp and mp columns
rsci_rosters_totals = rsci_rosters_totals.groupby(['season', 'url_school'])['rsci_mp', 'mp'].sum().reset_index()

#create rsci_rating by dividing rsci_mp by mp
rsci_rosters_totals['rsci_rating'] = rsci_rosters_totals['rsci_mp'] / rsci_rosters_totals['mp']

#convert season to int
rsci_rosters_totals['season'] = rsci_rosters_totals['season'].astype(int)

#calculate mp/scoring continuity
#ceate new mp table 
mp_cont = rosters_totals[['url_school', 'season', 'player_id', 'mp']]

#calculate if a player is a returning player from prior year
mp_cont['returning'] = mp_cont.groupby(['url_school','player_id'])['mp'].shift(-1)

#group by season and school and create new column with the total number of minutes of school for that season
mp_cont['total'] = mp_cont.groupby(['season', 'url_school'])['mp'].transform(sum)

#fill na vaues with 0
mp_cont['returning'] = mp_cont['returning'].fillna(0)

#filter out non returning players and low impact player by excluding players who played less than 150 minutes
mp_cont = mp_cont.loc[mp_cont['returning'] >= 150 , ['season', 'url_school', 'player_id', 'mp', 'total']]

#calculate the % of team minutes that each player accounter for
mp_cont['pct'] = mp_cont['mp'] / mp_cont['total']

#create continuity column by adding up the pct column
mp_cont['continuity'] = mp_cont.groupby(['season', 'url_school'])['pct'].transform(sum)

#remove everything but season, url_school and continuity columns
mp_cont = mp_cont[['season', 'url_school', 'continuity']]

#remove duplicate rows
mp_cont = mp_cont.drop_duplicates()

#convert season to int
mp_cont['season'] = mp_cont['season'].astype(int)

#calculate scoring continuity
#ceate new table 
pts_cont = rosters_totals[['url_school', 'season', 'player_id', 'pts']]

#calculate if a player is a returning player from prior year
pts_cont['returning'] = pts_cont.groupby(['url_school','player_id'])['pts'].shift(-1)

#group by season and school and create new column with the total number of minutes of school for that season
pts_cont['total'] = pts_cont.groupby(['season', 'url_school'])['pts'].transform(sum)

#filter out non returning players by excluding null values
pts_cont = pts_cont.loc[pts_cont['returning'].isnull() == False, ['season', 'url_school', 'player_id', 'pts', 'total']]

#calculate the % of team minutes that each player accounter for
pts_cont['pct'] = pts_cont['pts'] / pts_cont['total']

#create continuity column by adding up the pct column
pts_cont['continuity'] = pts_cont.groupby(['season', 'url_school'])['pct'].transform(sum)

#remove everything but season, url_school and continuity columns
pts_cont = pts_cont[['season', 'url_school', 'continuity']]

##get team id/location for each school from kaggle id's
#confirm number of rows for each year in games table is correct and that I have all the data
games.groupby(['season'])['season'].count()

##get all schools that have played in tournament
schools = games[['url_school', 'school']]

#get unique schools
school_ids = schools.drop_duplicates()

#get school id from kaggle spellings data
school_ids = pd.merge(school_ids, school_spellings, how='left', left_on='url_school', right_on='school_spelling')

#get location and coordinates for each school to calculate distance
#get location of each school
school_ids = pd.merge(school_ids, school_loc, on=['url_school'], suffixes=('', '_y'))

#remove extra school column created in the merge
school_ids = school_ids.drop('school_y', axis=1)

#create new column with underscore separting city/state so that can be joined to cities
school_ids['loc_id'] = school_ids['location'].str.replace(' ', '_').str.replace(',', '').str.replace('.', '').str.lower()


#prepare cities file to join to school_ids to get coordinates
#exclude all non-us cities
cities = cities[cities['country'] == 'United States']

#filter out unnecessary columns
cities = cities[['city_ascii', 'admin_name', 'lat', 'lng']]

#rename city_asci to city and admin_name to state
cities = cities.rename({'city_ascii': 'city', 'admin_name': 'state'}, axis=1)

#create new cities not found in table
new_cities = [pd.Series(['Boiling Springs', 'North Carolina', 35.2543, -81.6670], index=cities.columns),
              pd.Series(['Hamilton', 'New York', 42.8270, -75.5447], index=cities.columns),
              pd.Series(['South Orange', 'New Jersey',  40.7490, -74.2613], index=cities.columns),
              pd.Series(['Allegany', 'New York', 42.0901, -78.4942], index=cities.columns),
              pd.Series(['Moon Township','Pennsylvania',  40.5201, -80.2107], index=cities.columns),
              pd.Series(['Riverdale', 'New York', 40.9005, -73.9064], index=cities.columns),
              pd.Series(['Itta Bena', 'Mississippi',  33.4951, -90.3198], index=cities.columns),
              pd.Series(['Loudonville', 'New York',  42.7048, -73.7548], index=cities.columns),
              pd.Series(['Chestnut Hill', 'Massachusetts',  42.6362, -72.2009], index=cities.columns),
              pd.Series(['Northridge', 'California',  34.2283, -118.5368], index=cities.columns)]

#append new cities to cities table
cities = cities.append(new_cities , ignore_index=True)

#concatenate city and state column
cities['city_id'] = cities['city'] +'_' + cities['state']

#clean up city_id column to the same format in school_ids table
cities['city_id'] = cities['city_id'].str.replace(' ', '_').str.replace(',', '').str.replace('.', '').str.lower()

#get jiust the city_id, lat and lng columns
cities = cities[['city_id', 'lat', 'lng']]
#join cities to school_ids
school_ids = pd.merge(school_ids, cities, how='left', left_on = 'loc_id', right_on= 'city_id')


########## update coaches to only include pre tourney stats ########## 

#replace null values with 0  
coaches.loc[coaches['ncaa_apps_car'].isnull(), 'ncaa_apps_car'] = 0
coaches.loc[coaches['sweet16_apps_car'].isnull(), 'sweet16_apps_car'] = 0
coaches.loc[coaches['final4_apps_car'].isnull(), 'final4_apps_car'] = 0
coaches.loc[coaches['natl_champs_car'].isnull(), 'natl_champs_car'] = 0

def tourney_win(x):
    if x == 'Lost Second Round':
        return 1
    elif x == 'Lost Regional Semifinal':
        return 2
    elif x == 'Lost Regional Final':
        return 3
    elif x == 'Lost National Semifinal':
        return 4
    elif x == 'Lost National Final':
        return 5
    elif x == 'Won National Final':
        return 6
    else:
        return 0
    

def sweet16(x):
    if x >= 2:
        return 1
    else:
        return 0

def elite8(x):
    if x >= 3:
        return 1
    else:
        return 0

def final4(x):
    if x >= 4:
        return 1
    else:
        return 0
    
    
coaches['tourney_wins'] = coaches['tourney_note'].apply(tourney_win)
coaches['sweet16'] = coaches['tourney_wins'].apply(sweet16)
coaches['elite8'] = coaches['tourney_wins'].apply(elite8)
coaches['final4'] = coaches['tourney_wins'].apply(final4)


#Calculate elite 8's

#Get just coachid, season, and elite 8
coach_subset = coaches[['coach_id', 'season', 'elite8']]

#create cumsum of elite 8 wins
coach_subset['elite8_apps_car'] = coach_subset.groupby(['coach_id'])['elite8'].cumsum()

#remove negative numbers
coach_subset.loc[coach_subset['elite8_apps_car']== -1, 'elite8_apps_car'] = 0

#remove elite 8 column
coach_subset = coach_subset.drop('elite8', axis=1)

#join to coaches
coaches = pd.merge(coaches, coach_subset, on=['coach_id', 'season']) 


coaches['w_car'] = coaches['w_car'].astype(int) - coaches['tourney_wins'].astype(int)
coaches['sweet16_apps_car'] = coaches['sweet16_apps_car'].astype(int) - coaches['sweet16'].astype(int)
coaches['elite8_apps_car'] = coaches['elite8_apps_car'].astype(int) - coaches['elite8'].astype(int)
coaches['final4_apps_car'] = coaches['final4_apps_car'].astype(int) - coaches['final4'].astype(int)

#change sweet16_apps_car from negative 1 to 0
coaches['sweet16_apps_car'] = coaches['sweet16_apps_car'].replace(-1, 1)
  
#reduce to only the columns I need
coaches = coaches[['season', 'url_school', 'coach_id', 'ap_pre', 'w_car', 'l_car', 'sweet16_apps_car', 'elite8_apps_car']]       

#fill na values with 26

coaches['ap_pre'] = coaches['ap_pre'].fillna(26)


#manipulate t-rank data

#get only tounament teams(string includes seed number)
#pd.options.mode.chained_assignment = None

#create function to update tables
def update_trank(df):
        #get only tounament teams(string includes seed number)
        #strip on seed number and return 1st element and remove space at end and make lowercase
        df['school'] = df['school'].str.split('\d+').str[0].str.rstrip().str.lower()
        df['school'] = df['school'].astype(str)
        df['school'] = df['school'].str.replace('arkansas little rock' , 'ark little rock')
        df['school'] = df['school'].str.replace('louisiana lafayette' , 'ull')
        df['school'] = df['school'].str.replace('cal st. bakersfield' , 'cal-state-bakersfield')
        df['school'] = df['school'].str.replace('mississippi valley st.' , 'mississippi-valley-state')
        df['school'] = df['school'].str.replace('arkansas pine bluff' , 'ark pine bluff')
        df['adjoe'] = df['adjoe'].str.split('\s+').str[0]
        df['adjde'] = df['adjde'].str.split('\s+').str[0]
        df['barthag'] = df['barthag'].str.split('\s+').str[0]
        df['wab'] = df['wab'].str.split('\s+').str[0]
        return df
    


trank_november = update_trank(trank_november)
trank_december = update_trank(trank_december)
trank_january = update_trank(trank_january) 
trank_febmarch = update_trank(trank_febmarch) 
trank_all = update_trank(trank_all) 
   



trank_november_new = pd.merge(trank_november, school_spellings, how='left', left_on='school', right_on = ('school_spelling'))

trank_november_new = pd.merge(school_ids, trank_november_new, how='left', on=['team_id'])

trank_november_new = trank_november_new.rename({'adjoe': 'adjoe1', 'adjde': 'adjde1', 'wab': 'wab1'}, axis=1)



trank_december_new = pd.merge(trank_december, school_spellings, how='left', left_on='school', right_on = ('school_spelling'))

trank_december_new = pd.merge(school_ids, trank_december_new,  how='left', on=['team_id'])

trank_december_new = trank_december_new.rename({'adjoe': 'adjoe2', 'adjde': 'adjde2', 'wab': 'wab2'}, axis=1)


trank_january_new = pd.merge(trank_january, school_spellings, how='left', left_on='school', right_on = ('school_spelling'))

trank_january_new = pd.merge( school_ids, trank_january_new, how='left', on=['team_id'])

trank_january_new = trank_january_new.rename({'adjoe': 'adjoe3', 'adjde': 'adjde3', 'wab': 'wab3'}, axis=1)


trank_febmarch_new = pd.merge(trank_febmarch, school_spellings, how='left', left_on='school', right_on = ('school_spelling'))

trank_febmarch_new = pd.merge(school_ids, trank_febmarch_new, how='left', on=['team_id'])

trank_febmarch_new = trank_febmarch_new.rename({'adjoe': 'adjoe4', 'adjde': 'adjde4', 'wab': 'wab4'}, axis=1)


trank_all_new = pd.merge(trank_all, school_spellings, how='left', left_on='school', right_on = ('school_spelling'))

trank_all_new = pd.merge(school_ids, trank_all_new,  how='left', on=['team_id'])

trank_all_new = trank_all_new.rename({'adjoe': 'adjoe5', 'adjde': 'adjde5', 'wab': 'wab5'}, axis=1)

trank = pd.merge(trank_november_new, trank_december_new, on=['url_school', 'season'])
trank = pd.merge(trank, trank_january_new, on=['url_school', 'season'])
#drop extra season column (wouldn't let me sort)
trank = trank.drop('school_x', axis=1)

trank = pd.merge(trank, trank_febmarch_new, on=['url_school', 'season'])
#drop extra season column (wouldn't let me sort)
trank = trank.drop('school_x', axis=1)
trank = pd.merge(trank, trank_all_new, on=['url_school', 'season'])


#get games table ready to join with other tables              
#convert season to string
games['season'] = games['season'].astype(str)

#remove duplicate games
#create new column that has the same game combination string for both lines of games
games['dup_games'] = games.apply(lambda row: ''.join(sorted([row['season'], row['url_school'], row['opp_url_school']])), axis=1)

#remove duplicate games and drop the extra column
games = games.drop_duplicates('dup_games')     
games = games.drop('dup_games', axis=1)  

#remove unnecessary columns
games = games[['season', 'location', 'url_school', 'opp_url_school', 'pts_diff']]

##convert location column to same format in other tables
#convert The Pit, Al to Albuquerque, New Mexico
games['location'] = games['location'].str.replace('The Pit, Al', 'Albuquerque, NM')

 


#split location column on comma
games[['city', 'state']] = games['location'].str.split(', ', expand=True)

#get full state name
games = pd.merge(games, states, how='left', left_on = 'state', right_on = 'abbreviation', suffixes=('', '_y'))

#concatenate columns together
games['loc_id'] = games['city'] + ' ' + games['state_y']

#update formate
games['loc_id'] = games['loc_id'].str.replace(' ', '_').str.replace('.', '').str.lower()

#get lat long coordinates for tournament site
games = pd.merge(games, cities, how='left', left_on='loc_id', right_on = 'city_id')

#rename lat/lng
games = games.rename({'lat': 'tourn_lat', 'lng': 'tourn_lng'}, axis=1)

#get lat long coordinates for first school
games = pd.merge(games,school_ids[['url_school', 'lat', 'lng']],on=['url_school'], how='left')
#games = pd.merge(games, school_ids, how='left', on=['url_school'], suffixes=['url_school_', 'url_school_'])

#rename lat/lng
games = games.rename({'lat': 's1_lat', 'lng': 's1_lng'}, axis=1)

#get lat long coordinates for second school
games = pd.merge(games, school_ids, how='left', left_on = 'opp_url_school', right_on='url_school', suffixes=('', '_y'))

#rename lat/lng
games = games.rename({'lat': 's2_lat', 'lng': 's2_lng'}, axis=1)

#reduce columns
games = games[['season', 'url_school', 's1_lat', 's1_lng', 'opp_url_school', 's2_lat', 's2_lng',  'pts_diff', 'loc_id', 'tourn_lat', 'tourn_lng']]

##calculate distance
#pip install pyproj
from pyproj import Geod

#Distance will be measured on this ellipsoid - more accurate than a spherical method
wgs84_geod = Geod(ellps='WGS84') 

#Get distance between pairs of lat-lon points
def Distance(lat1,lon1,lat2,lon2):
  az12,az21,dist = wgs84_geod.inv(lon1,lat1,lon2,lat2)
  return dist



#Add/update a column to the data frame with the distances (in meters)
games['s1_dist'] = Distance(games['s1_lat'].tolist(),games['s1_lng'].tolist(),games['tourn_lat'].tolist(),games['tourn_lng'].tolist())
games['s2_dist'] = Distance(games['s2_lat'].tolist(),games['s2_lng'].tolist(),games['tourn_lat'].tolist(),games['tourn_lng'].tolist())



##add recruiting numbers

#convert season to int
games['season'] = games['season'].astype(int)

#join url_school to recruiting table
games = pd.merge(games, rsci_rosters_totals, how='left', on = ['url_school', 'season'])

#rename recruiting column for url_school
games = games.rename({'rsci_rating': 's1_rsci_rating'}, axis=1)

#join opp_url_school to recruiting table
games = pd.merge(games, rsci_rosters_totals, how='left', left_on = ['opp_url_school', 'season'], right_on = ['url_school', 'season'], suffixes=('', '_y'))

#rename recruiting column for opp_url_school
games = games.rename({'rsci_rating': 's2_rsci_rating'}, axis=1)

# add roster continuity numbers

#join url_school to continuity table
games = pd.merge(games, mp_cont, how='left', on = ['url_school', 'season'])

#rename continuity column for url_school
games = games.rename({'continuity': 's1_cont'}, axis=1)

#join opp_url_school to continuity table
games = pd.merge(games, mp_cont, how='left', left_on = ['opp_url_school', 'season'], right_on = ['url_school', 'season'], suffixes=('', '_y'))

#rename continuity column for opp_url_school
games = games.rename({'continuity': 's2_cont'}, axis=1)

#join to coaches

#join url_school to coaches table
games = pd.merge(games, coaches, how='left', on = ['url_school', 'season'])

#rename coaches column for url_school
games = games.rename({'coach_id': 's1_coach_id', 'w_car': 's1_coach_wins', 'l_car': 's1_coach_losses', 'ap_pre': 's1_ap_pre', 'sweet16_apps_car': 's1_coach_sweet16', 'elite8_apps_car': 's1_coach_elite8'}, axis=1)

#join opp_url_school to coaches table
games = pd.merge(games, coaches, how='left', left_on = ['opp_url_school', 'season'], right_on = ['url_school', 'season'], suffixes=('', '_y'))

#rename coaches column for opp_url_school
games = games.rename({'coach_id': 's2_coach_id', 'w_car': 's2_coach_wins', 'l_car': 's2_coach_losses', 'ap_pre': 's2_ap_pre', 'sweet16_apps_car': 's2_coach_sweet16', 'elite8_apps_car': 's2_coach_elite8'}, axis=1)


#rename url_school and opp_url_school
games = games.rename({'url_school': 's1', 'opp_url_school': 's2'}, axis=1)

#reduce columns
games = games[['season', 'loc_id', 's1', 's1_dist', 's1_cont', 's1_ap_pre', 's1_coach_id', 's1_coach_wins', 's1_coach_sweet16', 's1_coach_elite8',  's1_rsci_rating', 's2', 's2_dist', 's2_cont', 's2_rsci_rating', 's2_ap_pre', 's2_coach_id', 's2_coach_wins', 's2_coach_sweet16', 's2_coach_elite8', 'pts_diff']]



#join to t-rank
games = pd.merge(games, trank, how='left', left_on = ['s1', 'season'], right_on = ['url_school', 'season'], suffixes=('', '_y'))

games = games.rename({'wins': 's1_wins','adjoe1': 's1_adjoe1', 'adjoe2': 's1_adjoe2', 
                      'adjoe3': 's1_adjoe3','adjoe4': 's1_adjoe4', 'adjoe5': 's1_adjoe5', 
                      'adjde1': 's1_adjde1', 'adjde2': 's1_adjde2',
                      'adjde3': 's1_adjde3', 'adjde4': 's1_adjde4',
                      'adjde5': 's1_adjde5', 'wab1': 's1_wab1', 
                      'wab2': 's1_wab2', 'wab3': 's1_wab3', 'wab4': 's1_wab4', 
                      'wab5': 's1_wab5'
                      }, axis=1)
    
games = pd.merge(games, trank, how='left', left_on = ['s2', 'season'], right_on = ['url_school', 'season'], suffixes=('', '_y'))

games = games.rename({'wins': 's2_wins', 'adjoe1': 's2_adjoe1', 'adjoe2': 's2_adjoe2', 
                      'adjoe3': 's2_adjoe3','adjoe4': 's2_adjoe4', 'adjoe5': 's2_adjoe5', 
                      'adjde1': 's2_adjde1', 'adjde2': 's2_adjde2',
                      'adjde3': 's2_adjde3', 'adjde4': 's2_adjde4',
                      'adjde5': 's2_adjde5', 'wab1': 's2_wab1', 
                      'wab2': 's2_wab2', 'wab3': 's2_wab3', 'wab4': 's2_wab4', 
                      'wab5': 's2_wab5'
                      }, axis=1)
    
games = games[['season', 'loc_id', 's1', 's1_dist', 's1_cont', 's1_ap_pre', 's1_wins', 's1_coach_id', 's1_coach_wins', 's1_coach_sweet16', 's1_coach_elite8',  's1_rsci_rating', 
               's1_adjoe1', 's1_adjoe2', 's1_adjoe3', 's1_adjoe4', 's1_adjoe5',
               's1_adjde1', 's1_adjde2', 's1_adjde3', 's1_adjde4', 's1_adjde5',
               's1_wab1', 's1_wab2', 's1_wab3', 's1_wab4', 's1_wab5', 
               's2', 's2_dist', 's2_cont', 's2_rsci_rating', 's2_ap_pre', 's2_wins', 's2_coach_id', 's2_coach_wins', 's2_coach_sweet16', 's2_coach_elite8',
               's2_adjoe1', 's2_adjoe2', 's2_adjoe3', 's2_adjoe4', 's2_adjoe5',
               's2_adjde1', 's2_adjde2', 's2_adjde3', 's2_adjde4', 's2_adjde5',
               's2_wab1', 's2_wab2', 's2_wab3', 's2_wab4', 's2_wab5', 'pts_diff']]

#manually enter roster continuity for north-dakota-state who has a broken link for 2009
games.loc[(games['s1'] == 'north-dakota-state') & (games['season'] == 2009), 's1_cont'] = .8685

#check to make sure no null values
games.info()

















                

         
                
                
                

    



