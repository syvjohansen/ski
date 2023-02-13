#Need to add
#1. All for looking at last race
#2. Look into Tour/Stage races for points
#3. Update age scrape



from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
import pandas as pd
from scipy import stats
from datetime import datetime
from sklearn import linear_model
from sklearn import preprocessing
from sklearn.model_selection import KFold
from sklearn.linear_model import LinearRegression
#import statsmodels.api as sm
#import matplotlib.pyplot as plt
import math
import time
import json
from pandas.io.json import json_normalize
pd.options.mode.chained_assignment = None
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

import time
import traceback
start_time = time.time()












#This is for team sprint events
def fis_team_sprint():
	ids = []
	ids_men = []
	ids_ladies = []
	teams = []
	sex = []
	count = 0

	#start with the men
	#There will be 4 because of the semifinals
	startlist_list = ["https://www.fis-ski.com/DB/general/results.html?sectorcode=CC&raceid=43564",
	"https://www.fis-ski.com/DB/general/results.html?sectorcode=CC&raceid=43561"]
	for a in range(len(startlist_list)):
		startlist = BeautifulSoup(urlopen(startlist_list[a]), 'html.parser')
	#print(startlist)
		names = startlist.find_all('div', {'g-lg-14 g-md-14 g-sm-11 g-xs-10 justify-left bold'})
		body = startlist.find_all('div', {'g-lg-2 g-md-2 g-sm-3 hidden-xs justify-right gray pr-1'})
		print(startlist_list[a])

		for b in range(len(body)):
			#print(body[a].text.strip())
			if(b%3!=0):
				ids.append(int(body[b].text.strip()))
			else:
				team = names[b].text.strip()
				if(a<1):
					team = "m"+team
				else:
					team = "f"+team
				ids.append(team)
			#if(count==0):
			#	sex.append('M')
			#else:
			#	sex.append('L')
		
		

		#print(team)
		count+=1

	print(ids)

	

	#now for the ladies
	
	return ids

def fantasy_team_sprint(startlist):
	name = []
	team_name = []
	team_id = []
	team_price = []
	team_sex = []
	ski_id = []
	price =[]
	sex = []
	#sex = startlist['sex']
	#startlist = startlist['id']
	#print(sex)
	#print(startlist)
	fantasy = 'https://www.fantasyxc.se/api/athletes'
	#soup = BeautifulSoup(urlopen(fantasy), 'html5lib')
	#print(soup)
	with requests.Session() as s:
		r=s.get(fantasy)
		soup = BeautifulSoup(r.content, 'html5lib')
	API_json = json.loads(soup.get_text())
	API_df = pd.DataFrame.from_dict(pd.json_normalize(API_json), orient='columns')

	##Change to locate for increased speed
	for a in range(len(startlist)):
		if(a%3==0):
			
			if(startlist[a].startswith("m")):
				#print(startlist[a])
				country_name = startlist[a]
				country_name = country_name.split("m")
				country_name = country_name[1]
				if(country_name.endswith(" I") or country_name.endswith(" II")):
					pass
				else:
					country_name = country_name + " I"
				if(country_name == "ROC I"):
					country_name = "RUSSIA I"
				elif(country_name == "P.R. CHINA I"):
					country_name = "PEOPLES REPUBLIC OF CHINA I"
				nation= API_df.loc[API_df['name']==country_name]
				nation = nation.loc[nation['gender']=='m']
				
				sex.append('m')
				name.append("Male"+country_name)
				#print(nation)
			else:
				country_name = startlist[a]
				country_name = country_name.split("f")
				country_name = country_name[1]
				if(country_name.endswith(" I") or country_name.endswith(" II")):
					pass
				else:
					country_name = country_name + " I"
				if(country_name == "ROC I"):
					country_name = "RUSSIA I"
				elif(country_name == "P.R. CHINA I"):
					country_name = "PEOPLES REPUBLIC OF CHINA I"
				nation= API_df.loc[API_df['name']==country_name]
				nation = nation.loc[nation['gender']=='f']
				sex.append('f')
				name.append("Female" + country_name)
			try:
				ski_id.append(nation['athlete_id'].iloc[0])
				price.append(nation['price'].iloc[0])
				#sex.append(nation['gender'].iloc[0])
			except:
				print(country_name)
				ski_id.append(999999)
				price.append(23096)





		else:

			athlete = API_df.loc[API_df['athlete_id']==startlist[a]]
			
			first_name = []
			last_name = []
			try:
				test_name = (athlete['name'].iloc[0])
			except:
				test_name = "NAME Generic" 
			test_name = test_name.split(" ")
			for word in test_name:
				if word.isupper():
					last_name.append(word)
				else:
					first_name.append(word)
			first_name = ' '.join(first_name)
			last_name = ' '.join(last_name)
			test_name = first_name + " " + last_name


			name.append(test_name)
			try:
				ski_id.append(athlete['athlete_id'].iloc[0])
				price.append(athlete['price'].iloc[0])
				sex.append(athlete['gender'].iloc[0])
			except:
				ski_id.append(999999)
				price.append(999999)
				sex.append('mf')
				#pass
				print(test_name)
		
	d = {'name':name, 'id':ski_id, 'price':price, 'sex':sex}
	fantasy_df = pd.DataFrame(data=d)
	
	return fantasy_df

def elo_team_sprint(fantasydf, menpkls, ladiespkls, men_vars, ladies_vars, men_chrono, ladies_chrono):
	wc = [100, 80, 60, 50, 45, 40, 36, 32, 29, 26, 24, 22, 20, 18, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
	wc = [i*2 for i in wc]
	mendfs = []
	ladiesdfs = []
	skier_elo = []
	team_elos = []
	fantasydf.loc[:, 'points'] = 0
	menrelaypkls = ["~/ski/elo/python/ski/relay/radar/varmen_sprint_k.pkl"]
	ladiesrelaypkls = ["~/ski/elo/python/ski/relay/radar/varladies_sprint_k.pkl"]


	for a in range(len(menpkls)):
		skier_elo = []
		skier_distance_elo = []
		skier_distance_classic_elo = []
		skier_distance_freestyle_elo = []

		skier_sprint_elo = []
		skier_sprint_classic_elo = []
		skier_sprint_freestyle_elo = []
		skier_classic_elo = []
		skier_freestyle_elo = []

		skier_avg_points = []
		skier_exp = []
		skier_age = []
		skier_home = []
		df = pd.read_pickle(menpkls[a])
		df = df.loc[df['level']=="all"]
		menintslope = regress_relay(df, men_vars[a])
		
		
		ladiespkl = pd.read_pickle(ladiespkls[a])
		ladiespkl = ladiespkl.loc[ladiespkl['level']=="all"]
		ladiesintslope = regress_relay(ladiespkl, ladies_vars[a])

		df = men_chrono
		df = df.loc[df['level']=="all"]

		ladiespkl = ladies_chrono
		ladiespkl = ladiespkl.loc[ladiespkl['level']=="all"]


		df = df.append(ladiespkl, ignore_index = True)

		

		team_elos = []
		team_distance_elos = []
		team_distance_classic_elos = []
		team_distance_freestyle_elos = []

		team_sprint_elos = []
		team_sprint_classic_elos = []
		team_sprint_freestyle_elos = []

		team_classic_elos = []
		team_freestyle_elos = []
		team_avg_pointss = []
		team_exps = []
		team_ages = []

		team_homes = []
	
		
		df['name'] = df['name'].str.replace('ø', 'oe')
		df['name'] = df['name'].str.replace('ä', 'ae')
		df['name'] = df['name'].str.replace('æ', 'ae')
		df['name']= df['name'].str.replace('ö', 'oe')
		df['name']= df['name'].str.replace('ü', 'ue')
		df['name']= df['name'].str.replace('å', 'aa')
		df['name']= df['name'].str.replace('Ã¸', 'oe')
		df['name']= df['name'].str.replace('Ã¤', 'ae')
		df['name']= df['name'].str.replace('Ã¼', 'ue')
		df['name'] = df['name'].str.replace('Ã¶', 'oe')
		df['name'] = df['name'].str.replace('Ã', 'oe')
		df['name'] = df['name'].str.replace('Ã¦', 'ae')
		df['name']= df['name'].str.replace('Ã¥', 'aa')
		df['name'] = df['name'].str.replace('Aleksandr Terentev', 'alexander terentev')
		df['name'] = df['name'].str.replace('Irineu Esteve Altimiras', 'ireneu esteve altimiras')
		df['name'] = df['name'].str.replace('Thomas Hjalmar Westgaard', 'thomas maloney westgaard')
		df['name'] = df['name'].str.replace('Aleksandr Terentev', 'alexander terentev')
		df['name'] = df['name'].str.replace('Lauri Lepistoe', 'lauri lepisto')
		df['name'] = df['name'].str.replace('Philip Bellingham', 'phillip bellingham')
		df['name'] = df['name'].str.replace('Snorri Einarsson', 'snorri eythor einarsson')
		df['name'] = df['name'].str.replace('Krista Paermaekoski', 'krista parmakoski')
		df['name'] = df['name'].str.replace('Jessica Diggins', 'jessie diggins')
		df['name'] = df['name'].str.replace('Patricijia Eiduka', 'patricija eiduka')
		df['name'] = df['name'].str.replace('Katri Lylynperae', 'katri lylynpera')
		df['name'] = df['name'].str.replace('Julia Belger', 'julia preussger')
		df['name'] = df['name'].str.replace('Perttu Hyvaerinen', 'perttu hyvarinen')
		df['name'] = df['name'].str.replace('Kathrine Stewart-Jones', 'katherine stewart-jones')
		df['name'] = df['name'].str.replace('Ailja Iksanova', 'alija iksanova')
		df['name'] = df['name'].str.replace('Eric Silfver', 'erik silfver')
		df['name'] = df['name'].str.replace('Joni Maeki', 'joni maki')

		teamsdf = fantasydf.iloc[::3, :]
		print(teamsdf)
		fantasydf = fantasydf[fantasydf.index % 3 !=0]

		#print(fantasydf)

		fantasy_names = fantasydf['name']
		print(fantasy_names)
		fantasy_names = fantasy_names.str.lower()
		fantasy_names  = fantasy_names.tolist()
		count = 0
		team_elo = 0
		team_distance_elo = 0
		team_distance_classic_elo = 0
		team_distance_freestyle_elo = 0

		team_sprint_elo = 0
		team_sprint_classic_elo = 0
		team_sprint_freestyle_elo = 0

		team_classic_elo = 0
		team_freestyle_elo = 0

		team_avg_points = 0

		team_exp = 0
		team_age = 0
		team_home=0
	



		for b in range(len(fantasy_names)):

			skier = df.loc[df['name'].str.lower() == fantasy_names[b]]
			if(len(skier['name'])==0):
				print("Name not registered", fantasy_names[b])
			#print(skier)
			try:
				#Make tries and excepts for each of these
				elo = skier['elo'].iloc[-1]
				distance_elo = skier['distance_elo'].iloc[-1]
				distance_classic_elo = skier['distance_classic_elo'].iloc[-1]
				distance_freestyle_elo = skier['distance_freestyle_elo'].iloc[-1]

				sprint_elo = skier['sprint_elo'].iloc[-1]
				sprint_classic_elo = skier['sprint_classic_elo'].iloc[-1]
				sprint_freestyle_elo = skier['sprint_freestyle_elo'].iloc[-1]


				classic_elo = skier['classic_elo'].iloc[-1]
				freestyle_elo = skier['freestyle_elo'].iloc[-1]

				
				
				#avg_points = skier['avg_points'].iloc[-1]*.682250876756-.006352194332*skier['avg_points'].iloc[-1]**2+0.000027600716*skier['avg_points'].iloc[-1]**3-0.000000045133*skier['avg_points'].iloc[-1]**4-.958832685276
				exp = skier['exp'].iloc[-1]
				age = skier['age'].iloc[-1]

				if(skier['nation'].iloc[-1]=="Italy"):
					home = 1
				else:
					home = 0

				print(fantasy_names[b], elo)
				team_elo+=elo/2

				team_distance_elo+=distance_elo/2
				team_distance_classic_elo+=distance_classic_elo/2
				team_distance_freestyle_elo+=distance_freestyle_elo/2

				team_sprint_elo+=sprint_elo/2
				team_sprint_classic_elo+=sprint_classic_elo/2
				team_sprint_freestyle_elo+=sprint_freestyle_elo/2

				team_classic_elo+=classic_elo/2
				team_freestyle_elo+=freestyle_elo/2
				#team_avg_points+=avg_points

				team_exp+=exp
				team_age+=age

				team_home = home





			except Exception:
				#print(fantasy_names[b], traceback.print_exc())
				#print(fantasy_names[b])
				team_elo+=0

				team_distance_elo+=0
				team_distance_classic_elo+=0
				team_distance_freestyle_elo+=0

				team_sprint_elo+=0
				team_sprint_classic_elo+=0
				team_sprint_freestyle_elo+=0

				team_classic_elo+=0
				team_freestyle_elo+=0

				team_exp+=0
				team_age+=0
				team_avg_points+=0

				team_home+=0

			if(b%2==1):
				team_elos.append(team_elo)
				team_distance_elos.append(team_distance_elo)
				team_distance_classic_elos.append(team_distance_classic_elo)
				team_distance_freestyle_elos.append(team_distance_freestyle_elo)

				team_sprint_elos.append(team_sprint_elo)
				team_sprint_classic_elos.append(team_sprint_classic_elo)
				team_sprint_freestyle_elos.append(team_sprint_freestyle_elo)

				team_classic_elos.append(team_classic_elo)
				team_freestyle_elos.append(team_freestyle_elo)
				team_avg_pointss.append(team_avg_points)

				team_exps.append(team_exp)
				team_ages.append(team_age)

				team_homes.append(team_home)

				team_elo = 0
				team_distance_elo = 0
				team_distance_classic_elo = 0
				team_distance_freestyle_elo = 0

				team_sprint_elo = 0
				team_sprint_classic_elo = 0
				team_sprint_freestyle_elo = 0

				team_classic_elo = 0
				team_freestyle_elo = 0

				team_avg_points = 0

				team_exp = 0
				team_age = 0
				team_home=0
				#skier_elo.append(1300)
		
		teamsdf['elo'] = team_elos
		

		teamsdf['distance_elo'] = team_distance_elos
		teamsdf['distance_classic_elo'] = team_distance_classic_elos
		teamsdf['distance_freestyle_elo'] = team_distance_freestyle_elos

		teamsdf['sprint_elo'] = team_sprint_elos
		teamsdf['sprint_classic_elo'] = team_sprint_classic_elos
		teamsdf['sprint_freestyle_elo'] = team_sprint_freestyle_elos

		teamsdf['classic_elo'] = team_classic_elos
		teamsdf['freestyle_elo'] = team_freestyle_elos

		teamsdf['avg_points'] = team_avg_pointss
		teamsdf['exp'] = team_exps
		teamsdf['age'] = team_ages
		teamsdf['home'] = team_homes
		print("teamsdf", teamsdf)


		fantasydf = teamsdf
		#print(fantasydf)
		
		
		mendf = fantasydf.loc[fantasydf['sex']=='m']
		mendf = dezero(mendf)
		
		mendf = mendf.sort_values(by='elo', ascending = False)
		mendf = mendf.reset_index(drop=True)
		mendf['points'] = menintslope[0]
		men_vars[a] = [m.replace('pelo', 'elo') for m in men_vars[a]]
		men_vars[a] = [m.replace('pavg', 'avg') for m in men_vars[a]]


		ladies_vars[a] = [l.replace('pelo', 'elo') for l in ladies_vars[a]]
		ladies_vars[a] = [l.replace('pavg', 'avg') for l in ladies_vars[a]]
		

		for b in range(len(men_vars[a])):
			print(menintslope[b])
			mendf['points'] = mendf['points']+menintslope[b+1]*mendf[men_vars[a][b]]

			
		mendf['points'] = mendf['points'].fillna(0)
		
		
		mendf['points'].loc[mendf['points']<0] = 0

		#For normal WCP
		#mendf['points'] = .030964*mendf['points']**2+.263557*mendf['points']+3.196429

		#for TDS
		#mendf['points'] = 0.093193*mendf['points']**2+0.787371*mendf['points']+9.215816 

		#For Relay
		mendf['points'] = 0.0015396*mendf['points']**4-0.0737648*mendf['points']**3+1.1908351*mendf['points']**2-4.9454726*mendf['points']+10.2055212

			
		mendfs.append(mendf)
		
		ladiesdf = fantasydf.loc[fantasydf['sex']=='f']

		ladiesdf = dezero(ladiesdf)
		

		ladiesdf = ladiesdf.sort_values(by='elo', ascending=False)
		ladiesdf = ladiesdf.reset_index(drop=True)

		ladiesdf['points'] = ladiesintslope[0]
		for b in range(len(ladies_vars[a])):
			ladiesdf['points'] = ladiesdf['points']+ladiesintslope[b+1]*ladiesdf[ladies_vars[a][b]]
		#Next block is for regression
		
		
		ladiesdf['points'] = ladiesdf['points'].fillna(0)
		ladiesdf['points'].loc[ladiesdf['points']<0] = 0

		

		#Relay
		ladiesdf['points'] = 0.0015396*ladiesdf['points']**4-0.0737648*ladiesdf['points']**3+1.1908351*ladiesdf['points']**2-4.9454726*ladiesdf['points']+10.2055212

		#Next block is ladies non-regression
		'''
		ladies_wc_scores = ladiesdf['points'].tolist()
		ladies_wc_scores = ladies_wc_scores[:30]
		ladies_wc_scores = np.add(ladies_wc_scores, wc)
		ladies_wc_scores = pd.Series(ladies_wc_scores)
		ladiesdf.loc[:30, 'points'] = ladies_wc_scores
		'''
		ladiesdfs.append(ladiesdf)

		mendf = fantasydf.loc[fantasydf['sex']=='m']
		mendf = mendf.sort_values(by='id')
		mendf = mendf.reset_index(drop=True)
		ladiesdf = fantasydf.loc[fantasydf['sex']=='f']
		ladiesdf = ladiesdf.sort_values(by='id')
		ladiesdf = ladiesdf.reset_index(drop=True)


	for a in range(len(mendfs)):
		mendfs[a] = mendfs[a].sort_values(by='id')
		mendfs[a] = mendfs[a].reset_index(drop=True)
		elo_name = "elo"+str(a+1)
		race_name = "race"+str(a+1)
		mendf[elo_name] = mendfs[a]['elo']
		mendf[race_name] = mendfs[a]['points']
		mendf['points'] = mendf['points'] + mendf[race_name]
		ladiesdfs[a] = ladiesdfs[a].sort_values(by='id')
		ladiesdfs[a] = ladiesdfs[a].reset_index(drop=True)
		ladiesdf[elo_name] = ladiesdfs[a]['elo']
		ladiesdf[race_name] = ladiesdfs[a]['points']
		ladiesdf['points'] = ladiesdf['points'] + ladiesdf[race_name]







	
	#ladiesdf = ladiesdf[:30]
	#ladiesdf[:30, 'points'] += wc
	mendf=mendf.sort_values(by='points', ascending=False)
	ladiesdf =ladiesdf.sort_values(by='points', ascending=False)
	mendf = mendf[mendf['points']>0]
	ladiesdf = ladiesdf[ladiesdf['points']>0]
	mendf['place'] = np.arange(1, len(mendf['name'])+1, 1)
	ladiesdf['place'] = np.arange(1,len(ladiesdf['name'])+1,1)
	print(list(ladiesdf['name']).sort())
	fantasydf = mendf
	fantasydf = fantasydf.append(ladiesdf)

	fantasydf = fantasydf[['name', 'id', 'price', 'sex','points', 'race1', 'place']]
	return fantasydf
def fis_mixed_ts():
	'''men_ids = [3420909, 3420605, 3420586, 3422819, 34819883, 3482119, 3482280, 3482277, 3180535, 3180861,
	3180557, 3180508, 3530882, 3530532, 3530902, 3530911, 3200802, 3200205, 3200356, 3200676,
	3501741, 3501223, 3500664, 3501010, 3510342, 3510023, 3510361, 3510351, 3150570, 3150519, 
	3150664, 3150637, 3100406, 3100409, 3100412, 1111111, 3190529, 3190111, 3190302, 3190345,
	3290379, 3290326, 3290407, 3290504, 1111111, 1111111, 3300494, 3300373, 3430249, 3430233,
	3430276, 3430103, 3390167, 3390240, 3390169, 3390207, 1111111, 1111111, 1111111, 1111111,
	3040101, 3040125, 1111111, 1111111, 1111111, 3560145, 3560101, 3560121]'''
	

	men_ids = [3500664, 3421154, 3501255, 3510588, 3190323, 3426456, 3200676, 3180865, 3200356, 3180861,
	3050267, 9999999999999, 3560145, 3290326, 3550147, 3100412, 3100409, 99999999999]
	ladies_ids = [3505809, 3426201, 3506105, 3510619, 3195263, 3426200, 3205305, 3185579, 3205407, 3185551, 
	3050155, 3195205, 3560121, 999999999, 3555052, 3105146, 3105179, 999999999]

	ids = []
	'''men_teams = ["mNORWAY I", "mRUSSIA I", "mFINLAND I", "mUNITED STATES OF AMERICA I", "mGERMANY I", "mSWEDEN I", "mSWITZERLAND I", "mCZECH REPUBLIC I", "mCANADA I", "mFRANCE I",
	"mITALY I", "mJAPAN I", "mPOLAND I", "mESTONIA I", "mPEOPLES REPUBLIC OF CHINA I", "mAUSTRALIA I", "mSLOVENIA I"]'''
	#ladies_teams = []
	teams = []
	sex = []
	count = 0
	#start with the men
	startlist_list = ['https://www.fis-ski.com/DB/general/results.html?sectorcode=CC&raceid=40882']
	for a in range(len(startlist_list)):

		startlist = BeautifulSoup(urlopen(startlist_list[a]), 'html.parser')
		

	#print(startlist)
		names = startlist.find_all('div', {'g-lg-18 g-md-18 g-sm-16 g-xs-16 justify-left bold'})
		body = startlist.find_all('div', {'pr-1 g-lg-2 g-md-2 g-sm-2 hidden-xs justify-right gray'})
		
		count = 0
	
		for b in range(len(body)):
			#print(body[a].text.strip())
			#if(b%3!=0):
				#ids.append(int(body[b].text.strip()))
			team = names[b].text.strip()
				
			ids.append(team)
			ids.append(ladies_ids[b])
			ids.append(men_ids[b])
				

			#else:
			
			#if(count==0):
			#	sex.append('M')
			#else:
			#	sex.append('L')
		
		

		#print(team)
		#count+=1

	print(ids)

	

	#now for the ladies
	
	return ids

def fantasy_mixed_ts(startlist):
	name = []
	team_name = []
	team_id = []
	team_price = []
	team_sex = []
	ski_id = []
	price =[]
	sex = []
	#sex = startlist['sex']
	#startlist = startlist['id']
	#print(sex)
	#print(startlist)
	fantasy = 'https://www.fantasyxc.se/api/athletes'
	#soup = BeautifulSoup(urlopen(fantasy), 'html5lib')
	#print(soup)
	with requests.Session() as s:
		r=s.get(fantasy)
		soup = BeautifulSoup(r.content, 'html5lib')
	API_json = json.loads(soup.get_text())
	API_df = pd.DataFrame.from_dict(pd.json_normalize(API_json), orient='columns')

	##Change to locate for increased speed
	for a in range(len(startlist)):
		if(a%3==0):
			
			
				#print(startlist[a])
			country_name = startlist[a]
			
			
			if(country_name.endswith(" I") or country_name.endswith(" II")):
				pass
			else:
				country_name = country_name + " I"

			nation= API_df.loc[API_df['name']==country_name]
			nation = nation.loc[nation['gender']=='mixed']
			sex.append('mixed')
			name.append(country_name)
				#print(nation)
			
			try:
				ski_id.append(nation['athlete_id'].iloc[0])
				price.append(nation['price'].iloc[0])
				#sex.append(nation['gender'].iloc[0])
			except:
				print(country_name)
				ski_id.append(999999)
				price.append(23096)





		else:

			athlete = API_df.loc[API_df['athlete_id']==startlist[a]]
			
			first_name = []
			last_name = []
			try:
				test_name = (athlete['name'].iloc[0])
			except:
				test_name = "NAME Generic" 
			test_name = test_name.split(" ")
			for word in test_name:
				if word.isupper():
					last_name.append(word)
				else:
					first_name.append(word)
			first_name = ' '.join(first_name)
			last_name = ' '.join(last_name)
			test_name = first_name + " " + last_name


			name.append(test_name)
			try:
				ski_id.append(athlete['athlete_id'].iloc[0])
				price.append(athlete['price'].iloc[0])
				sex.append(athlete['gender'].iloc[0])
			except:
				ski_id.append(999999)
				price.append(999999)
				sex.append('mf')
				#pass
				print(test_name)
		
	d = {'name':name, 'id':ski_id, 'price':price, 'sex':sex}
	fantasy_df = pd.DataFrame(data=d)
	
	return fantasy_df

def elo_mixed_ts(fantasydf, menpkls, ladiespkls, relaypkls):
	wc = [100, 80, 60, 50, 45, 40, 36, 32, 29, 26, 24, 22, 20, 18, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
	wc = [i*2 for i in wc]
	
	team_elos = []
	fantasydf.loc[:,'points'] =0

	for a in range(len(menpkls)):
		
		df = pd.read_pickle(menpkls[a])
		df = df.loc[df['level']=="all"]
		ladiespkl = pd.read_pickle(ladiespkls[a])
		ladiespkl = ladiespkl.loc[ladiespkl['level']=="all"]
		df = df.append(ladiespkl, ignore_index = True)


		df['name'] = df['name'].str.replace('ø', 'oe')
		df['name'] = df['name'].str.replace('ä', 'ae')
		df['name'] = df['name'].str.replace('æ', 'ae')
		df['name']= df['name'].str.replace('ö', 'oe')
		df['name']= df['name'].str.replace('ü', 'ue')
		df['name']= df['name'].str.replace('å', 'aa')
		df['name']= df['name'].str.replace('Ã¸', 'oe')
		df['name']= df['name'].str.replace('Ã¤', 'ae')
		df['name']= df['name'].str.replace('Ã¼', 'ue')
		df['name'] = df['name'].str.replace('Ã¶', 'oe')
		df['name'] = df['name'].str.replace('Ã', 'oe')
		df['name'] = df['name'].str.replace('Ã¦', 'ae')
		df['name']= df['name'].str.replace('Ã¥', 'aa')
		
		df['name'] = df['name'].str.replace('Aleksandr Terentev', 'alexander terentev')
		df['name'] = df['name'].str.replace('Irineu Esteve Altimiras', 'ireneu esteve altimiras')
		df['name'] = df['name'].str.replace('Thomas Hjalmar Westgaard', 'thomas maloney westgaard')
		df['name'] = df['name'].str.replace('Aleksandr Terentev', 'alexander terentev')
		df['name'] = df['name'].str.replace('Lauri Lepistoe', 'lauri lepisto')
		df['name'] = df['name'].str.replace('Philip Bellingham', 'phillip bellingham')
		df['name'] = df['name'].str.replace('Snorri Einarsson', 'snorri eythor einarsson')
		df['name'] = df['name'].str.replace('Krista Paermaekoski', 'krista parmakoski')
		df['name'] = df['name'].str.replace('Jessica Diggins', 'jessie diggins')
		df['name'] = df['name'].str.replace('Patricijia Eiduka', 'patricija eiduka')
		df['name'] = df['name'].str.replace('Katri Lylynperae', 'katri lylynpera')
		df['name'] = df['name'].str.replace('Julia Belger', 'julia preussger')
		df['name'] = df['name'].str.replace('Perttu Hyvaerinen', 'perttu hyvarinen')
		df['name'] = df['name'].str.replace('Kathrine Stewart-Jones', 'katherine stewart-jones')
		df['name'] = df['name'].str.replace('Ailja Iksanova', 'alija iksanova')
		df['name'] = df['name'].str.replace('Joni Maeki', 'joni maki')
		df['name'] = df['name'].str.replace('Paal Golberg', 'pal golberg')

		teamsdf = fantasydf.iloc[::3, :]

		fantasydf = fantasydf[fantasydf.index % 3 !=0]

		#print(fantasydf)
		

		fantasy_names = fantasydf['name']
		fantasy_names = fantasy_names.str.lower()
		fantasy_names  = fantasy_names.tolist()
		count = 0
		team_elo = 0
		for b in range(len(fantasy_names)):

			skier = df.loc[df['name'].str.lower() == fantasy_names[b]]
			if(len(skier['name'])==0):
				print(fantasy_names[b])
			#print(skier)
			try:
				elo = skier['elo'].iloc[-1]
				team_elo+=elo
				#print(team_elo)
				#skier_elo.append(elo)
			#elo = (skier.loc[skier['date']==20210500]['elo'])
			except:
				print("Name not registered", fantasy_names[b])
				team_elo+=1300

			if(b%2==1):
				team_elos.append(team_elo)
				team_elo = 0
				#skier_elo.append(1300)
		
		teamsdf['team_elo'] = team_elos
		fantasydf = teamsdf
		
		relaypkl = pd.read_pickle(relaypkls[a])
		
		relaypkl = relaypkl.loc[relaypkl['level']=="all"]
		
		intslope = regress_relay(relaypkl)

		mixeddf = fantasydf.loc[fantasydf['sex']=='mixed']
		max_elo = max(mixeddf['team_elo'])
		mixeddf['elopct'] = mixeddf['team_elo'].apply(lambda x: 100*(x/max_elo))
		mixeddf = mixeddf.sort_values(by='team_elo', ascending = False)
		mixeddf = mixeddf.reset_index(drop=True)
		#Edit out these next three and the ladies three for pursuit.  One for actual
		
		#mendf = mendf.sort_values(by='elo', ascending=False)
		
		#mendf = mendf[:len(mendf)]
		mixeddf['points'] = mixeddf['elopct'].apply(lambda x: (intslope[0]+intslope[1]*x)**np.exp(1))
		mixeddf['points'] = mixeddf['points'].fillna(0)


		#ladiesdf = ladiesdf.sort_values(by='elo', ascending=False)
		#ladiesdf = ladiesdf[:len(team_elos)]
		
		mixeddf['place'] = np.arange(1, len(mixeddf['name'])+1, 1)
		
		fantasydf = mixeddf
	

	return fantasydf

def fis_relay():
	'''men_ids = [3420909, 3420605, 3420586, 3422819, 34819883, 3482119, 3482280, 3482277, 3180535, 3180861,
	3180557, 3180508, 3530882, 3530532, 3530902, 3530911, 3200802, 3200205, 3200356, 3200676,
	3501741, 3501223, 3500664, 3501010, 3510342, 3510023, 3510361, 3510351, 3150570, 3150519, 
	3150664, 3150637, 3100406, 3100409, 3100412, 1111111, 3190529, 3190111, 3190302, 3190345,
	3290379, 3290326, 3290407, 3290504, 1111111, 1111111, 3300494, 3300373, 3430249, 3430233,
	3430276, 3430103, 3390167, 3390240, 3390169, 3390207, 1111111, 1111111, 1111111, 1111111,
	3040101, 3040125, 1111111, 1111111, 1111111, 3560145, 3560101, 3560121]'''
	men_ids = []
	ids = []
	'''men_teams = ["mNORWAY I", "mRUSSIA I", "mFINLAND I", "mUNITED STATES OF AMERICA I", "mGERMANY I", "mSWEDEN I", "mSWITZERLAND I", "mCZECH REPUBLIC I", "mCANADA I", "mFRANCE I",
	"mITALY I", "mJAPAN I", "mPOLAND I", "mESTONIA I", "mPEOPLES REPUBLIC OF CHINA I", "mAUSTRALIA I", "mSLOVENIA I"]'''
	men_teams = []
	ladies_teams = []
	teams = []
	sex = []
	count = 0
	#start with the men
	startlist_list = ['https://www.fis-ski.com/DB/general/results.html?sectorcode=CC&raceid=41609',
'https://www.fis-ski.com/DB/general/results.html?sectorcode=CC&raceid=41608']
	for a in range(len(startlist_list)):

		startlist = BeautifulSoup(urlopen(startlist_list[a]), 'html.parser')
		'''if(a==0):
			count = 0
			for b in range(len(men_teams)):
				ids.append(men_teams[b])
				for c in range(4):
					ids.append(men_ids[count])
					count+=1
		else:
'''
	#print(startlist)
		names = startlist.find_all('div', {'g-lg-14 g-md-14 g-sm-11 g-xs-10 justify-left bold'})
		body = startlist.find_all('div', {'g-lg-2 g-md-2 g-sm-3 hidden-xs justify-right gray pr-1'})
		print(startlist_list[a])

		for b in range(len(body)):
			#print(body[a].text.strip())
			if(b%5!=0):
				ids.append(int(body[b].text.strip()))
			else:
				team = names[b].text.strip()
				if(a==0):
					team = "m"+team
				else:
					team = "f"+team
				ids.append(team)
			#if(count==0):
			#	sex.append('M')
			#else:
			#	sex.append('L')
		
		

		#print(team)
		#count+=1

	print(ids)

	

	#now for the ladies
	
	return ids

def fantasy_relay(startlist):
	name = []
	team_name = []
	team_id = []
	team_price = []
	team_sex = []
	ski_id = []
	price =[]
	sex = []
	#sex = startlist['sex']
	#startlist = startlist['id']
	#print(sex)
	#print(startlist)
	fantasy = 'https://www.fantasyxc.se/api/athletes'
	#soup = BeautifulSoup(urlopen(fantasy), 'html5lib')
	#print(soup)
	with requests.Session() as s:
		r=s.get(fantasy)
		soup = BeautifulSoup(r.content, 'html5lib')
	API_json = json.loads(soup.get_text())
	API_df = pd.DataFrame.from_dict(pd.json_normalize(API_json), orient='columns')

	##Change to locate for increased speed
	for a in range(len(startlist)):
		if(a%5==0):
			
			if(startlist[a].startswith("m")):
				#print(startlist[a])
				country_name = startlist[a]
				country_name = country_name.split("m")
				country_name = country_name[1]
				if(country_name.endswith(" I") or country_name.endswith(" II")):
					pass
				else:
					country_name = country_name + " I"

				nation= API_df.loc[API_df['name']==country_name]
				nation = nation.loc[nation['gender']=='m']
				sex.append('m')
				name.append("Male"+country_name)
				#print(nation)
			else:
				country_name = startlist[a]
				country_name = country_name.split("f")
				country_name = country_name[1]
				if(country_name.endswith(" I") or country_name.endswith(" II")):
					pass
				else:
					country_name = country_name + " I"
				nation= API_df.loc[API_df['name']==country_name]
				nation = nation.loc[nation['gender']=='f']
				sex.append('f')
				name.append("Female" + country_name)
			try:
				ski_id.append(nation['athlete_id'].iloc[0])
				price.append(nation['price'].iloc[0])
				#sex.append(nation['gender'].iloc[0])
			except:
				print(country_name)
				ski_id.append(999999)
				price.append(23096)





		else:

			athlete = API_df.loc[API_df['athlete_id']==startlist[a]]
			
			first_name = []
			last_name = []
			try:
				test_name = (athlete['name'].iloc[0])
			except:
				test_name = "NAME Generic" 
			test_name = test_name.split(" ")
			for word in test_name:
				if word.isupper():
					last_name.append(word)
				else:
					first_name.append(word)
			first_name = ' '.join(first_name)
			last_name = ' '.join(last_name)
			test_name = first_name + " " + last_name


			name.append(test_name)
			try:
				ski_id.append(athlete['athlete_id'].iloc[0])
				price.append(athlete['price'].iloc[0])
				sex.append(athlete['gender'].iloc[0])
			except:
				ski_id.append(999999)
				price.append(999999)
				sex.append('mf')
				#pass
				print(test_name)
		
	d = {'name':name, 'id':ski_id, 'price':price, 'sex':sex}
	fantasy_df = pd.DataFrame(data=d)
	return fantasy_df







def elo_relay(fantasydf, menpkls, ladiespkls, men_vars, ladies_vars, men_chrono, ladies_chrono):
	wc = [100, 80, 60, 50, 45, 40, 36, 32, 29, 26, 24, 22, 20, 18, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
	wc = [i*2 for i in wc]
	mendfs = []
	ladiesdfs = []
	skier_elo = []
	team_elos = []
	fantasydf.loc[:, 'points'] = 0
	menrelaypkls = ["~/ski/elo/python/ski/relay/radar/varmen_sprint_k.pkl"]
	ladiesrelaypkls = ["~/ski/elo/python/ski/relay/radar/varladies_sprint_k.pkl"]


	for a in range(len(menpkls)):
		skier_elo = []
		skier_distance_elo = []
		skier_distance_classic_elo = []
		skier_distance_freestyle_elo = []

		skier_sprint_elo = []
		skier_sprint_classic_elo = []
		skier_sprint_freestyle_elo = []
		skier_classic_elo = []
		skier_freestyle_elo = []

		skier_avg_points = []
		skier_exp = []
		skier_age = []
		skier_home = []
		df = pd.read_pickle(menpkls[a])
		df = df.loc[df['level']=="all"]
		menintslope = regress_relay(df, men_vars[a])
		
		
		ladiespkl = pd.read_pickle(ladiespkls[a])
		ladiespkl = ladiespkl.loc[ladiespkl['level']=="all"]
		ladiesintslope = regress_relay(ladiespkl, ladies_vars[a])

		df = men_chrono
		df = df.loc[df['level']=="all"]

		ladiespkl = ladies_chrono
		ladiespkl = ladiespkl.loc[ladiespkl['level']=="all"]


		df = df.append(ladiespkl, ignore_index = True)

		

		team_elos = []
		team_distance_elos = []
		team_distance_classic_elos = []
		team_distance_freestyle_elos = []

		team_sprint_elos = []
		team_sprint_classic_elos = []
		team_sprint_freestyle_elos = []

		team_classic_elos = []
		team_freestyle_elos = []
		team_avg_pointss = []
		team_exps = []
		team_ages = []

		team_homes = []
	
		
		df['name'] = df['name'].str.replace('ø', 'oe')
		df['name'] = df['name'].str.replace('ä', 'ae')
		df['name'] = df['name'].str.replace('æ', 'ae')
		df['name']= df['name'].str.replace('ö', 'oe')
		df['name']= df['name'].str.replace('ü', 'ue')
		df['name']= df['name'].str.replace('å', 'aa')
		df['name']= df['name'].str.replace('Ã¸', 'oe')
		df['name']= df['name'].str.replace('Ã¤', 'ae')
		df['name']= df['name'].str.replace('Ã¼', 'ue')
		df['name'] = df['name'].str.replace('Ã¶', 'oe')
		df['name'] = df['name'].str.replace('Ã', 'oe')
		df['name'] = df['name'].str.replace('Ã¦', 'ae')
		df['name']= df['name'].str.replace('Ã¥', 'aa')
		df['name'] = df['name'].str.replace('Aleksandr Terentev', 'alexander terentev')
		df['name'] = df['name'].str.replace('Irineu Esteve Altimiras', 'ireneu esteve altimiras')
		df['name'] = df['name'].str.replace('Thomas Hjalmar Westgaard', 'thomas maloney westgaard')
		df['name'] = df['name'].str.replace('Aleksandr Terentev', 'alexander terentev')
		df['name'] = df['name'].str.replace('Lauri Lepistoe', 'lauri lepisto')
		df['name'] = df['name'].str.replace('Philip Bellingham', 'phillip bellingham')
		df['name'] = df['name'].str.replace('Snorri Einarsson', 'snorri eythor einarsson')
		df['name'] = df['name'].str.replace('Krista Paermaekoski', 'krista parmakoski')
		df['name'] = df['name'].str.replace('Jessica Diggins', 'jessie diggins')
		df['name'] = df['name'].str.replace('Patricijia Eiduka', 'patricija eiduka')
		df['name'] = df['name'].str.replace('Katri Lylynperae', 'katri lylynpera')
		df['name'] = df['name'].str.replace('Julia Belger', 'julia preussger')
		df['name'] = df['name'].str.replace('Perttu Hyvaerinen', 'perttu hyvarinen')
		df['name'] = df['name'].str.replace('Kathrine Stewart-Jones', 'katherine stewart-jones')
		df['name'] = df['name'].str.replace('Ailja Iksanova', 'alija iksanova')
		df['name'] = df['name'].str.replace('Eric Silfver', 'erik silfver')
		df['name'] = df['name'].str.replace('Joni Maeki', 'joni maki')
		df['name'] = df['name'].str.replace('Emmi Laemsae', 'emmi lamsa')
		df['name'] = df['name'].str.replace('Anne Kylloenen', 'anne kyllonen')
		df['name'] = df['name'].str.replace('Finn O\'Connell', 'finn o connell')
		df['name'] = df['name'].str.replace('Viktoriya Olekh', 'viktoriia olekh')

		teamsdf = fantasydf.iloc[::5, :]
		print(teamsdf)
		fantasydf = fantasydf[fantasydf.index % 5 !=0]

		#print(fantasydf)

		fantasy_names = fantasydf['name']
		print(fantasy_names)
		fantasy_names = fantasy_names.str.lower()
		fantasy_names  = fantasy_names.tolist()
		count = 0
		team_elo = 0
		team_distance_elo = 0
		team_distance_classic_elo = 0
		team_distance_freestyle_elo = 0

		team_sprint_elo = 0
		team_sprint_classic_elo = 0
		team_sprint_freestyle_elo = 0

		team_classic_elo = 0
		team_freestyle_elo = 0

		team_avg_points = 0

		team_exp = 0
		team_age = 0
		team_home=0
	



		for b in range(len(fantasy_names)):

			skier = df.loc[df['name'].str.lower() == fantasy_names[b]]
			if(len(skier['name'])==0):
				print("Name not registered", fantasy_names[b])
			#print(skier)
			try:
				#Make tries and excepts for each of these
				elo = skier['elo'].iloc[-1]
				distance_elo = skier['distance_elo'].iloc[-1]
				distance_classic_elo = skier['distance_classic_elo'].iloc[-1]
				distance_freestyle_elo = skier['distance_freestyle_elo'].iloc[-1]

				sprint_elo = skier['sprint_elo'].iloc[-1]
				sprint_classic_elo = skier['sprint_classic_elo'].iloc[-1]
				sprint_freestyle_elo = skier['sprint_freestyle_elo'].iloc[-1]


				classic_elo = skier['classic_elo'].iloc[-1]
				freestyle_elo = skier['freestyle_elo'].iloc[-1]

				
				
				#avg_points = skier['avg_points'].iloc[-1]*.682250876756-.006352194332*skier['avg_points'].iloc[-1]**2+0.000027600716*skier['avg_points'].iloc[-1]**3-0.000000045133*skier['avg_points'].iloc[-1]**4-.958832685276
				exp = skier['exp'].iloc[-1]
				age = skier['age'].iloc[-1]

				if(skier['nation'].iloc[-1]=="Italy"):
					home = 1
				else:
					home = 0

				print(fantasy_names[b], elo)
				team_elo+=elo/4

				team_distance_elo+=distance_elo/4
				team_distance_classic_elo+=distance_classic_elo/4
				team_distance_freestyle_elo+=distance_freestyle_elo/4

				team_sprint_elo+=sprint_elo/4
				team_sprint_classic_elo+=sprint_classic_elo/4
				team_sprint_freestyle_elo+=sprint_freestyle_elo/4

				team_classic_elo+=classic_elo/4
				team_freestyle_elo+=freestyle_elo/4
				#team_avg_points+=avg_points

				team_exp+=exp
				team_age+=age

				team_home = home





			except Exception:
				#print(fantasy_names[b], traceback.print_exc())
				#print(fantasy_names[b])
				team_elo+=0

				team_distance_elo+=0
				team_distance_classic_elo+=0
				team_distance_freestyle_elo+=0

				team_sprint_elo+=0
				team_sprint_classic_elo+=0
				team_sprint_freestyle_elo+=0

				team_classic_elo+=0
				team_freestyle_elo+=0

				team_exp+=0
				team_age+=0
				team_avg_points+=0

				team_home+=0

			if(b%4==3):
				team_elos.append(team_elo)
				team_distance_elos.append(team_distance_elo)
				team_distance_classic_elos.append(team_distance_classic_elo)
				team_distance_freestyle_elos.append(team_distance_freestyle_elo)

				team_sprint_elos.append(team_sprint_elo)
				team_sprint_classic_elos.append(team_sprint_classic_elo)
				team_sprint_freestyle_elos.append(team_sprint_freestyle_elo)

				team_classic_elos.append(team_classic_elo)
				team_freestyle_elos.append(team_freestyle_elo)
				team_avg_pointss.append(team_avg_points)

				team_exps.append(team_exp)
				team_ages.append(team_age)

				team_homes.append(team_home)

				team_elo = 0
				team_distance_elo = 0
				team_distance_classic_elo = 0
				team_distance_freestyle_elo = 0

				team_sprint_elo = 0
				team_sprint_classic_elo = 0
				team_sprint_freestyle_elo = 0

				team_classic_elo = 0
				team_freestyle_elo = 0

				team_avg_points = 0

				team_exp = 0
				team_age = 0
				team_home=0
				#skier_elo.append(1300)
		
		teamsdf['elo'] = team_elos
		

		teamsdf['distance_elo'] = team_distance_elos
		teamsdf['distance_classic_elo'] = team_distance_classic_elos
		teamsdf['distance_freestyle_elo'] = team_distance_freestyle_elos

		teamsdf['sprint_elo'] = team_sprint_elos
		teamsdf['sprint_classic_elo'] = team_sprint_classic_elos
		teamsdf['sprint_freestyle_elo'] = team_sprint_freestyle_elos

		teamsdf['classic_elo'] = team_classic_elos
		teamsdf['freestyle_elo'] = team_freestyle_elos

		teamsdf['avg_points'] = team_avg_pointss
		teamsdf['exp'] = team_exps
		teamsdf['age'] = team_ages
		teamsdf['home'] = team_homes
		print("teamsdf", teamsdf)


		fantasydf = teamsdf
		#print(fantasydf)
		
		
		mendf = fantasydf.loc[fantasydf['sex']=='m']
		mendf = dezero(mendf)
		
		mendf = mendf.sort_values(by='elo', ascending = False)
		mendf = mendf.reset_index(drop=True)
		mendf['points'] = menintslope[0]
		men_vars[a] = [m.replace('pelo', 'elo') for m in men_vars[a]]
		men_vars[a] = [m.replace('pavg', 'avg') for m in men_vars[a]]


		ladies_vars[a] = [l.replace('pelo', 'elo') for l in ladies_vars[a]]
		ladies_vars[a] = [l.replace('pavg', 'avg') for l in ladies_vars[a]]
		

		for b in range(len(men_vars[a])):
			print(menintslope[b])
			mendf['points'] = mendf['points']+menintslope[b+1]*mendf[men_vars[a][b]]

			
		mendf['points'] = mendf['points'].fillna(0)
		
		
		mendf['points'].loc[mendf['points']<0] = 0

		#For normal WCP
		#mendf['points'] = .030964*mendf['points']**2+.263557*mendf['points']+3.196429

		#for TDS
		#mendf['points'] = 0.093193*mendf['points']**2+0.787371*mendf['points']+9.215816 

		#For Relay
		mendf['points'] = 0.0015396*mendf['points']**4-0.0737648*mendf['points']**3+1.1908351*mendf['points']**2-4.9454726*mendf['points']+10.2055212

			
		mendfs.append(mendf)
		
		ladiesdf = fantasydf.loc[fantasydf['sex']=='f']

		ladiesdf = dezero(ladiesdf)
		

		ladiesdf = ladiesdf.sort_values(by='elo', ascending=False)
		ladiesdf = ladiesdf.reset_index(drop=True)

		ladiesdf['points'] = ladiesintslope[0]
		for b in range(len(ladies_vars[a])):
			ladiesdf['points'] = ladiesdf['points']+ladiesintslope[b+1]*ladiesdf[ladies_vars[a][b]]
		#Next block is for regression
		
		
		ladiesdf['points'] = ladiesdf['points'].fillna(0)
		ladiesdf['points'].loc[ladiesdf['points']<0] = 0

		

		#Relay
		ladiesdf['points'] = 0.0015396*ladiesdf['points']**4-0.0737648*ladiesdf['points']**3+1.1908351*ladiesdf['points']**2-4.9454726*ladiesdf['points']+10.2055212

		#Next block is ladies non-regression
		'''
		ladies_wc_scores = ladiesdf['points'].tolist()
		ladies_wc_scores = ladies_wc_scores[:30]
		ladies_wc_scores = np.add(ladies_wc_scores, wc)
		ladies_wc_scores = pd.Series(ladies_wc_scores)
		ladiesdf.loc[:30, 'points'] = ladies_wc_scores
		'''
		ladiesdfs.append(ladiesdf)

		mendf = fantasydf.loc[fantasydf['sex']=='m']
		mendf = mendf.sort_values(by='id')
		mendf = mendf.reset_index(drop=True)
		ladiesdf = fantasydf.loc[fantasydf['sex']=='f']
		ladiesdf = ladiesdf.sort_values(by='id')
		ladiesdf = ladiesdf.reset_index(drop=True)


	for a in range(len(mendfs)):
		mendfs[a] = mendfs[a].sort_values(by='id')
		mendfs[a] = mendfs[a].reset_index(drop=True)
		elo_name = "elo"+str(a+1)
		race_name = "race"+str(a+1)
		mendf[elo_name] = mendfs[a]['elo']
		mendf[race_name] = mendfs[a]['points']
		mendf['points'] = mendf['points'] + mendf[race_name]
		ladiesdfs[a] = ladiesdfs[a].sort_values(by='id')
		ladiesdfs[a] = ladiesdfs[a].reset_index(drop=True)
		ladiesdf[elo_name] = ladiesdfs[a]['elo']
		ladiesdf[race_name] = ladiesdfs[a]['points']
		ladiesdf['points'] = ladiesdf['points'] + ladiesdf[race_name]







	
	#ladiesdf = ladiesdf[:30]
	#ladiesdf[:30, 'points'] += wc
	mendf=mendf.sort_values(by='points', ascending=False)
	ladiesdf =ladiesdf.sort_values(by='points', ascending=False)
	mendf = mendf[mendf['points']>0]
	ladiesdf = ladiesdf[ladiesdf['points']>0]
	mendf['place'] = np.arange(1, len(mendf['name'])+1, 1)
	ladiesdf['place'] = np.arange(1,len(ladiesdf['name'])+1,1)
	print(list(ladiesdf['name']).sort())
	fantasydf = mendf
	fantasydf = fantasydf.append(ladiesdf)

	fantasydf = fantasydf[['name', 'id', 'price', 'sex','points', 'race1', 'place']]
	return fantasydf

	
def fis_mixed_relay():
	'''men_ids = [3420909, 3420605, 3420586, 3422819, 34819883, 3482119, 3482280, 3482277, 3180535, 3180861,
	3180557, 3180508, 3530882, 3530532, 3530902, 3530911, 3200802, 3200205, 3200356, 3200676,
	3501741, 3501223, 3500664, 3501010, 3510342, 3510023, 3510361, 3510351, 3150570, 3150519, 
	3150664, 3150637, 3100406, 3100409, 3100412, 1111111, 3190529, 3190111, 3190302, 3190345,
	3290379, 3290326, 3290407, 3290504, 1111111, 1111111, 3300494, 3300373, 3430249, 3430233,
	3430276, 3430103, 3390167, 3390240, 3390169, 3390207, 1111111, 1111111, 1111111, 1111111,
	3040101, 3040125, 1111111, 1111111, 1111111, 3560145, 3560101, 3560121]'''
	
	ids = []
	'''men_teams = ["mNORWAY I", "mRUSSIA I", "mFINLAND I", "mUNITED STATES OF AMERICA I", "mGERMANY I", "mSWEDEN I", "mSWITZERLAND I", "mCZECH REPUBLIC I", "mCANADA I", "mFRANCE I",
	"mITALY I", "mJAPAN I", "mPOLAND I", "mESTONIA I", "mPEOPLES REPUBLIC OF CHINA I", "mAUSTRALIA I", "mSLOVENIA I"]'''
	#ladies_teams = []
	teams = []
	sex = []
	count = 0
	#start with the men
	startlist_list = ['https://www.fis-ski.com/DB/general/results.html?sectorcode=CC&raceid=39241']
	for a in range(len(startlist_list)):

		startlist = BeautifulSoup(urlopen(startlist_list[a]), 'html.parser')
		

	#print(startlist)
		names = startlist.find_all('div', {'g-lg-14 g-md-14 g-sm-11 g-xs-10 justify-left bold'})
		body = startlist.find_all('div', {'g-lg-2 g-md-2 g-sm-3 hidden-xs justify-right gray pr-1'})
		print(startlist_list[a])

		for b in range(len(body)):
			#print(body[a].text.strip())
			if(b%5!=0):
				ids.append(int(body[b].text.strip()))
			else:
				team = names[b].text.strip()
				
				ids.append(team)
			#if(count==0):
			#	sex.append('M')
			#else:
			#	sex.append('L')
		
		

		#print(team)
		#count+=1

	print(ids)

	

	#now for the ladies
	
	return ids

def fantasy_mixed_relay(startlist):
	name = []
	team_name = []
	team_id = []
	team_price = []
	team_sex = []
	ski_id = []
	price =[]
	sex = []
	#sex = startlist['sex']
	#startlist = startlist['id']
	#print(sex)
	#print(startlist)
	fantasy = 'https://www.fantasyxc.se/api/athletes'
	#soup = BeautifulSoup(urlopen(fantasy), 'html5lib')
	#print(soup)
	with requests.Session() as s:
		r=s.get(fantasy)
		soup = BeautifulSoup(r.content, 'html5lib')
	API_json = json.loads(soup.get_text())
	API_df = pd.DataFrame.from_dict(pd.json_normalize(API_json), orient='columns')

	##Change to locate for increased speed
	for a in range(len(startlist)):
		if(a%5==0):
			
			
				#print(startlist[a])
			country_name = startlist[a]
			
			
			if(country_name.endswith(" I") or country_name.endswith(" II")):
				pass
			else:
				country_name = country_name + " I"

			nation= API_df.loc[API_df['name']==country_name]
			nation = nation.loc[nation['gender']=='mixed']
			sex.append('mixed')
			name.append(country_name)
				#print(nation)
			
			try:
				ski_id.append(nation['athlete_id'].iloc[0])
				price.append(nation['price'].iloc[0])
				#sex.append(nation['gender'].iloc[0])
			except:
				print(country_name)
				ski_id.append(999999)
				price.append(23096)





		else:

			athlete = API_df.loc[API_df['athlete_id']==startlist[a]]
			
			first_name = []
			last_name = []
			try:
				test_name = (athlete['name'].iloc[0])
			except:
				test_name = "NAME Generic" 
			test_name = test_name.split(" ")
			for word in test_name:
				if word.isupper():
					last_name.append(word)
				else:
					first_name.append(word)
			first_name = ' '.join(first_name)
			last_name = ' '.join(last_name)
			test_name = first_name + " " + last_name


			name.append(test_name)
			try:
				ski_id.append(athlete['athlete_id'].iloc[0])
				price.append(athlete['price'].iloc[0])
				sex.append(athlete['gender'].iloc[0])
			except:
				ski_id.append(999999)
				price.append(999999)
				sex.append('mf')
				#pass
				print(test_name)
		
	d = {'name':name, 'id':ski_id, 'price':price, 'sex':sex}
	fantasy_df = pd.DataFrame(data=d)
	
	return fantasy_df

def elo_mixed_relay(fantasydf, menpkls, ladiespkls, relaypkls):
	wc = [100, 80, 60, 50, 45, 40, 36, 32, 29, 26, 24, 22, 20, 18, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
	wc = [i*2 for i in wc]
	
	team_elos = []
	fantasydf.loc[:,'points'] =0

	for a in range(len(menpkls)):
		print(menpkls[a])
		df = pd.read_pickle(menpkls[a])
		df = df.loc[df['level']=="all"]
		ladiespkl = pd.read_pickle(ladiespkls[a])
		ladiespkl = ladiespkl.loc[ladiespkl['level']=="all"]
		df = df.append(ladiespkl, ignore_index = True)


		df['name'] = df['name'].str.replace('ø', 'oe')
		df['name'] = df['name'].str.replace('ä', 'ae')
		df['name'] = df['name'].str.replace('æ', 'ae')
		df['name']= df['name'].str.replace('ö', 'oe')
		df['name']= df['name'].str.replace('ü', 'ue')
		df['name']= df['name'].str.replace('å', 'aa')
		df['name']= df['name'].str.replace('Ã¸', 'oe')
		df['name']= df['name'].str.replace('Ã¤', 'ae')
		df['name']= df['name'].str.replace('Ã¼', 'ue')
		df['name'] = df['name'].str.replace('Ã¶', 'oe')
		df['name'] = df['name'].str.replace('Ã', 'oe')
		
		
		df['name'] = df['name'].str.replace('Aleksandr Terentev', 'alexander terentev')
		df['name'] = df['name'].str.replace('Irineu Esteve Altimiras', 'ireneu esteve altimiras')
		df['name'] = df['name'].str.replace('Thomas Hjalmar Westgaard', 'thomas maloney westgaard')
		df['name'] = df['name'].str.replace('Aleksandr Terentev', 'alexander terentev')
		df['name'] = df['name'].str.replace('Lauri Lepistoe', 'lauri lepisto')
		df['name'] = df['name'].str.replace('Philip Bellingham', 'phillip bellingham')
		df['name'] = df['name'].str.replace('Snorri Einarsson', 'snorri eythor einarsson')
		df['name'] = df['name'].str.replace('Krista Paermaekoski', 'krista parmakoski')
		df['name'] = df['name'].str.replace('Jessica Diggins', 'jessie diggins')
		df['name'] = df['name'].str.replace('Patricijia Eiduka', 'patricija eiduka')
		df['name'] = df['name'].str.replace('Katri Lylynperae', 'katri lylynpera')
		df['name'] = df['name'].str.replace('Julia Belger', 'julia preussger')
		df['name'] = df['name'].str.replace('Perttu Hyvaerinen', 'perttu hyvarinen')
		df['name'] = df['name'].str.replace('Kathrine Stewart-Jones', 'katherine stewart-jones')
		df['name'] = df['name'].str.replace('Ailja Iksanova', 'alija iksanova')
		df['name'] = df['name'].str.replace('Joni Maeki', 'joni maki')
		

		teamsdf = fantasydf.iloc[::5, :]

		fantasydf = fantasydf[fantasydf.index % 5 !=0]

		#print(fantasydf)
		

		fantasy_names = fantasydf['name']
		fantasy_names = fantasy_names.str.lower()
		fantasy_names  = fantasy_names.tolist()
		count = 0
		team_elo = 0
		for b in range(len(fantasy_names)):

			skier = df.loc[df['name'].str.lower() == fantasy_names[b]]
			if(len(skier['name'])==0):
				print(fantasy_names[b])
			#print(skier)
			try:
				elo = skier['elo'].iloc[-1]
				team_elo+=elo
				#print(team_elo)
				#skier_elo.append(elo)
			#elo = (skier.loc[skier['date']==20210500]['elo'])
			except:
				print("Name not registered", fantasy_names[b])
				team_elo+=1300

			if(b%4==3):
				team_elos.append(team_elo)
				team_elo = 0
				#skier_elo.append(1300)
		
		teamsdf['team_elo'] = team_elos
		fantasydf = teamsdf
		
		relaypkl = pd.read_pickle(relaypkls[a])
		relaypkl = relaypkl.loc[relaypkl['level']=="all"]
		
		intslope = regress_relay(relaypkl)

		mixeddf = fantasydf.loc[fantasydf['sex']=='mixed']
		max_elo = max(mixeddf['team_elo'])
		mixeddf['elopct'] = mixeddf['team_elo'].apply(lambda x: 100*(x/max_elo))
		mixeddf = mixeddf.sort_values(by='team_elo', ascending = False)
		mixeddf = mixeddf.reset_index(drop=True)
		#Edit out these next three and the ladies three for pursuit.  One for actual
		
		#mendf = mendf.sort_values(by='elo', ascending=False)
		
		#mendf = mendf[:len(mendf)]
		mixeddf['points'] = mixeddf['elopct'].apply(lambda x: (intslope[0]+intslope[1]*x)**np.exp(1))
		mixeddf['points'] = mixeddf['points'].fillna(0)


		#ladiesdf = ladiesdf.sort_values(by='elo', ascending=False)
		#ladiesdf = ladiesdf[:len(team_elos)]
		
		mixeddf['place'] = np.arange(1, len(mixeddf['name'])+1, 1)
		
		fantasydf = mixeddf
	

	return fantasydf

def fis():
	ids = []
	sex = []
	'''ids_men = [3422819, 3420586, 3420605, 3420909, 3422619, 3421320, 3482277, 3482280, 3482105, 3482119,
	3481988, 3050342, 3020003, 3100406, 3100409, 3150570, 3150519, 3180535, 3180508, 3180557,
	3181180, 3190529, 3190111, 3190302, 3190268, 3190345, 3200802, 3200205, 3200356, 3200676,
	3220002, 3220016, 3270010, 3290379, 3290407, 3290326, 3290383, 3300494, 3300373, 3670115,
	3430249, 3490145, 3500664, 3501223, 3501741, 3501010, 3501255, 3510479, 3510342, 3510351,
	3510361, 3510023, 3530882, 3530532]'''

	fuzz = pd.read_excel("~/ski/elo/knapsack/excel365/fuzzy_match.xlsx")
	men = fuzz.loc[fuzz['gender']=='m']
	ids_men = list((men['athlete_id']))
	ladies = fuzz.loc[fuzz['gender']=='f']
	ids_ladies = list(ladies['athlete_id'])
	#print(ids_men)
	#ids_men = []
	#ids_ladies = []

	count = 0
	#start with the men
	startlist_list = ['https://www.fis-ski.com/DB/general/results.html?sectorcode=CC&raceid=41603',
	'https://www.fis-ski.com/DB/general/results.html?sectorcode=CC&raceid=41602']
	for a in startlist_list:
		startlist = BeautifulSoup(urlopen(a), 'html.parser')
	#print(startlist)
		body = startlist.find_all('div', {'class':'pr-1 g-lg-2 g-md-2 g-sm-2 hidden-xs justify-right gray'})
		#print(a)
		if(count==0):
			for a in range(len(ids_men)):
				ids.append(int(ids_men[a]))
		else:
			for a in range(len(ids_ladies)):
				ids.append(int(ids_ladies[a]))
		for b in range(len(body)):
			#print(body[a].text.strip())
			id_check = int(body[b].text.strip())
			if(id_check in ids):
				continue
			else:
				ids.append(int(body[b].text.strip()))
			#if(count==0):
			#	sex.append('M')
			#else:
			#	sex.append('L')
		ids.append
		count+=1

	#now for the ladies
	
	return ids

def fantasy(startlist):
	name = []
	ski_id = []
	price =[]
	sex = []
	#sex = startlist['sex']
	#startlist = startlist['id']
	#print(sex)
	#print(startlist)
	fantasy = 'https://www.fantasyxc.se/api/athletes'
	#soup = BeautifulSoup(urlopen(fantasy), 'html5lib')
	#print(soup)
	with requests.Session() as s:
		r=s.get(fantasy)
		soup = BeautifulSoup(r.content, 'html5lib')
	API_json = json.loads(soup.get_text())
	API_df = pd.DataFrame.from_dict(pd.json_normalize(API_json), orient='columns')

	##Change to locate for increased speed
	for a in range(len(startlist)):
		athlete = API_df.loc[API_df['athlete_id']==startlist[a]]
		
		first_name = []
		last_name = []
		try:
			test_name = (athlete['name'].iloc[0])
		except:
			#print(startlist[a])
			continue
		test_name = test_name.split(" ")
		for word in test_name:
			if word.isupper():
				last_name.append(word)
			else:
				first_name.append(word)
		first_name = ' '.join(first_name)
		last_name = ' '.join(last_name)
		test_name = first_name + " " + last_name
		#print(test_name)


		name.append(test_name)
		try:
			ski_id.append(athlete['athlete_id'].iloc[0])
			price.append(athlete['price'].iloc[0])
			sex.append(athlete['gender'].iloc[0])
		except:
			print(test_name)
		
	d = {'name':name, 'id':ski_id, 'price':price, 'sex':sex}
	fantasy_df = pd.DataFrame(data=d)
	#print(fantasy_df)
	return fantasy_df

def pursuit(fantasydf):
	stage = [50, 46, 43, 40, 37, 34, 32, 30, 28, 26, 24, 22, 20, 18, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
	wc = [100, 80, 60, 50, 45, 40, 36, 32, 29, 26, 24, 22, 20, 18, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
	tour = [400, 320, 240, 200, 180, 160, 144, 128, 116, 104, 96, 88, 80, 72, 64, 60, 56, 52, 48, 44, 40, 36, 32, 28, 24, 20,20, 20, 20, 20]

	mendf = fantasydf.loc[fantasydf['sex']=='m']
	mendf = mendf.sort_values(by='elo', ascending=False)
	mendf['pursuit'] = np.arange(1, len(mendf['name'])+1, 1)
	mendf['pursuit'] = .3*mendf['pursuit'] + .7*mendf['place']
	mendf = mendf.sort_values(by='pursuit', ascending=True)
	mendf['pursuit'] = np.arange(1, len(mendf['name'])+1, 1)
	mendf = mendf[:30]
	mendf['points'] = tour

	ladiesdf = fantasydf.loc[fantasydf['sex']=='f']
	ladiesdf = ladiesdf.sort_values(by='elo', ascending=False)
	ladiesdf['pursuit'] = np.arange(1,len(ladiesdf['name'])+1,1)
	ladiesdf['pursuit'] = .3*ladiesdf['pursuit'] + .7*ladiesdf['place']
	ladiesdf = ladiesdf.sort_values(by='pursuit', ascending=True)
	ladiesdf['pursuit'] = np.arange(1,len(ladiesdf['name'])+1,1)
	ladiesdf = ladiesdf[:30]
	ladiesdf['points'] = tour

	fantasydf = mendf
	fantasydf = fantasydf.append(ladiesdf)
	return fantasydf


def elo(fantasydf, menpkls, ladiespkls, men_vars, ladies_vars, men_chrono, ladies_chrono):
	stage = [50, 47, 44, 41, 38, 35, 32, 30, 28, 26, 24, 22, 20, 18, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
	wc = [100,95,90,85,80,75,72,69,66,63,60,58,56,54,52,50,48,46,44,42,40, 38, 36, 34, 32, 30, 28, 26, 24, 22, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
	tour = [300, 285, 270, 255, 240, 216, 207, 198, 189, 180, 174, 168, 162, 156, 150, 144, 138, 132, 126, 120, 114, 108, 102, 96, 90, 84, 78, 72, 66, 60, 57, 54, 51, 48, 45, 42, 39, 36, 33, 30, 27, 24, 21, 18, 15, 12, 9, 6, 3]
	mendfs = []
	ladiesdfs = []
	fantasydf.loc[:,'points'] =0
	
	#"~/ski/elo/python/ski/ladies/varladies_10_classic.pkl",
	#"~/ski/elo/python/ski/ladies/varladies_sprint_classic.pkl"]

	for a in range(len(menpkls)):
		skier_elo = []
		skier_distance_elo = []
		skier_distance_classic_elo = []
		skier_distance_freestyle_elo = []

		skier_sprint_elo = []
		skier_sprint_classic_elo = []
		skier_sprint_freestyle_elo = []
		skier_classic_elo = []
		skier_freestyle_elo = []

		skier_avg_points = []
		skier_exp = []
		skier_age = []
		skier_home = []

		df = pd.read_pickle(menpkls[a])
		#df = men_chrono

		#It's all unless it's the first race of the years
		df = df.loc[df['level']=="all"]

		menintslope = regress(df, men_vars[a])
		
		ladiespkl = pd.read_pickle(ladiespkls[a])
		#ladiespkl = ladies_chrono
		ladiespkl = ladiespkl.loc[ladiespkl['level']=="all"]
		ladiesintslope = regress(ladiespkl, ladies_vars[a])

		df_pkl = df
		df = men_chrono

		#It's all unless it's the first race of the years
		df = df.loc[df['level']=="all"]
		ladies_short_pkl = ladiespkl
		ladiespkl = ladies_chrono
		ladiespkl = ladiespkl.loc[ladiespkl['level']=="all"]
		df = df.append(ladiespkl, ignore_index = True)
		df_pkl = df_pkl.append(ladies_short_pkl, ignore_index=True)
		
		df['name'] = df['name'].str.replace('ø', 'oe')
		df['name'] = df['name'].str.replace('ä', 'ae')
		df['name'] = df['name'].str.replace('æ', 'ae')
		df['name']= df['name'].str.replace('ö', 'oe')
		df['name']= df['name'].str.replace('ü', 'ue')
		df['name']= df['name'].str.replace('å', 'aa')
		df['name']= df['name'].str.replace('Ã¸', 'oe')
		df['name']= df['name'].str.replace('Ã¤', 'ae')
		df['name']= df['name'].str.replace('Ã¼', 'ue')
		df['name']= df['name'].str.replace('Ø', 'Oe')
		df['name'] = df['name'].str.replace('Ã¶', 'oe')
		df['name'] = df['name'].str.replace('Ã', 'oe')
		

		df['name'] = df['name'].str.replace('Aleksandr Terentev', 'alexander terentev')
		df['name'] = df['name'].str.replace('Irineu Esteve Altimiras', 'ireneu esteve altimiras')
		df['name'] = df['name'].str.replace('Thomas Hjalmar Westgaard', 'thomas maloney westgaard')
		df['name'] = df['name'].str.replace('Aleksandr Terentev', 'alexander terentev')
		df['name'] = df['name'].str.replace('Lauri Lepistoe', 'lauri lepisto')
		df['name'] = df['name'].str.replace('Philip Bellingham', 'phillip bellingham')
		df['name'] = df['name'].str.replace('Snorri Einarsson', 'snorri eythor einarsson')
		df['name'] = df['name'].str.replace('Krista Paermaekoski', 'krista parmakoski')
		df['name'] = df['name'].str.replace('Jessica Diggins', 'jessie diggins')
		df['name'] = df['name'].str.replace('Patricijia Eiduka', 'patricija eiduka')
		df['name'] = df['name'].str.replace('Katri Lylynperae', 'katri lylynpera')
		df['name'] = df['name'].str.replace('Julia Belger', 'julia preussger')
		df['name'] = df['name'].str.replace('Perttu Hyvaerinen', 'perttu hyvarinen')
		df['name'] = df['name'].str.replace('Kathrine Stewart-Jones', 'katherine stewart-jones')
		df['name'] = df['name'].str.replace('Ailja Iksanova', 'alija iksanova')
		df['name'] = df['name'].str.replace('Eric Silfver', 'erik silfver')
		df['name'] = df['name'].str.replace('Joni Maeki', 'joni maki')
		df['name'] = df['name'].str.replace('Emmi Laemsae', 'emmi lamsa')
		df['name'] = df['name'].str.replace('Anne Kylloenen', 'anne kyllonen')
		df['name'] = df['name'].str.replace('Finn O\'Connell', 'finn o connell')
		df['name'] = df['name'].str.replace('Viktoriya Olekh', 'viktoriia olekh')
		

		df_pkl['name'] = df_pkl['name'].str.replace('ø', 'oe')
		df_pkl['name'] = df_pkl['name'].str.replace('ä', 'ae')
		df_pkl['name'] = df_pkl['name'].str.replace('æ', 'ae')
		df_pkl['name']= df_pkl['name'].str.replace('ö', 'oe')
		df_pkl['name']= df_pkl['name'].str.replace('ü', 'ue')
		df_pkl['name']= df_pkl['name'].str.replace('å', 'aa')
		df_pkl['name']= df_pkl['name'].str.replace('Ã¸', 'oe')
		df_pkl['name']= df_pkl['name'].str.replace('Ã¤', 'ae')
		df_pkl['name']= df_pkl['name'].str.replace('Ã¼', 'ue')
		df_pkl['name']= df_pkl['name'].str.replace('Ø', 'Oe')
		df_pkl['name'] = df_pkl['name'].str.replace('Ã¶', 'oe')
		df_pkl['name'] = df_pkl['name'].str.replace('Ã', 'oe')
		df_pkl['name'] = df_pkl['name'].str.replace('Aleksandr Terentev', 'alexander terentev')
		df_pkl['name'] = df_pkl['name'].str.replace('Irineu Esteve Altimiras', 'ireneu esteve altimiras')
		df_pkl['name'] = df_pkl['name'].str.replace('Thomas Hjalmar Westgaard', 'thomas maloney westgaard')
		df_pkl['name'] = df_pkl['name'].str.replace('Aleksandr Terentev', 'alexander terentev')
		df_pkl['name'] = df_pkl['name'].str.replace('Lauri Lepistoe', 'lauri lepisto')
		df_pkl['name'] = df_pkl['name'].str.replace('Philip Bellingham', 'phillip bellingham')
		df_pkl['name'] = df_pkl['name'].str.replace('Snorri Einarsson', 'snorri eythor einarsson')
		df_pkl['name'] = df_pkl['name'].str.replace('Krista Paermaekoski', 'krista parmakoski')
		df_pkl['name'] = df_pkl['name'].str.replace('Jessica Diggins', 'jessie diggins')
		df_pkl['name'] = df_pkl['name'].str.replace('Patricijia Eiduka', 'patricija eiduka')
		df_pkl['name'] = df_pkl['name'].str.replace('Katri Lylynperae', 'katri lylynpera')
		df_pkl['name'] = df_pkl['name'].str.replace('Julia Belger', 'julia preussger')
		df_pkl['name'] = df_pkl['name'].str.replace('Perttu Hyvaerinen', 'perttu hyvarinen')
		df_pkl['name'] = df_pkl['name'].str.replace('Kathrine Stewart-Jones', 'katherine stewart-jones')
		df_pkl['name'] = df_pkl['name'].str.replace('Ailja Iksanova', 'alija iksanova')
		df_pkl['name'] = df_pkl['name'].str.replace('Eric Silfver', 'erik silfver')
		df_pkl['name'] = df_pkl['name'].str.replace('Joni Maeki', 'joni maki')
		df_pkl['name'] = df_pkl['name'].str.replace('Emmi Laemsae', 'emmi lamsa')
		df_pkl['name'] = df_pkl['name'].str.replace('Anne Kylloenen', 'anne kyllonen')
		df_pkl['name'] = df_pkl['name'].str.replace('Finn O\'Connell', 'finn o connell')
		df_pkl['name'] = df_pkl['name'].str.replace('Viktoriya Olekh', 'viktoriia olekh')
		#df['name'] = df['name'].str.replace('H', 'ailja iksanova')



		fantasy_names = fantasydf['name']
		fantasy_names = fantasy_names.str.lower()
		fantasy_names  = fantasy_names.tolist()
		
		
		#print(df.loc[df['name'].str.lower()=='kristine stavaas skistad'])


		for b in range(len(fantasy_names)):
			skier = df.loc[df['name'].str.lower() == fantasy_names[b]]
			skier_pkl = df_pkl.loc[df_pkl['name'].str.lower() == fantasy_names[b]]
			
			if(len(skier['name'])==0):
				print(a, fantasy_names[b])
			
			try:
				#Make tries and excepts for each of these
				elo = skier['elo'].iloc[-1]
				skier_elo.append(elo)
			except:
				skier_elo.append(0)
			try:
				distance_elo = skier['distance_elo'].iloc[-1]
				skier_distance_elo.append(distance_elo)
			except:
				skier_distance_elo.append(0)
			try:
				distance_classic_elo = skier['distance_classic_elo'].iloc[-1]
				skier_distance_classic_elo.append(distance_classic_elo)
			except:
				skier_distance_classic_elo.append(0)
			try:
				distance_freestyle_elo = skier['distance_freestyle_elo'].iloc[-1]
				skier_distance_freestyle_elo.append(distance_freestyle_elo)
			except:
				skier_distance_freestyle_elo.append(0)
			try:
				sprint_elo = skier['sprint_elo'].iloc[-1]
				skier_sprint_elo.append(sprint_elo)
			except:
				skier_sprint_elo.append(0)
			try:
				sprint_classic_elo = skier['sprint_classic_elo'].iloc[-1]
				skier_sprint_classic_elo.append(sprint_classic_elo)
			except:
				skier_sprint_classic_elo.append(0)
			try:
				sprint_freestyle_elo = skier['sprint_freestyle_elo'].iloc[-1]
				skier_sprint_freestyle_elo.append(sprint_freestyle_elo)
			except:
				skier_sprint_freestyle_elo.append(0)
			try:
				classic_elo = skier['classic_elo'].iloc[-1]
				skier_classic_elo.append(classic_elo)
			except:
				skier_classic_elo.append(0)
			try:
				freestyle_elo = skier['freestyle_elo'].iloc[-1]
				skier_freestyle_elo.append(freestyle_elo)
			except:
				skier_freestyle_elo.append(0)
			try:
				#NEED TO CHANGE AVERAGE POINTS AS IT LOOKS AT ALL

				#Individual
				avg_points = skier_pkl['avg_points'].iloc[-1]*.896294-0.0042397*skier_pkl['avg_points'].iloc[-1]**2+1.5865602

				#Stage
				#avg_points = skier_pkl['avg_points'].iloc[-1]*1.0801595-0.0100871*skier_pkl['avg_points'].iloc[-1]**2+0.1584908
				
				#Tour de Ski
				#avg_points = skier['avg_points'].iloc[-1]*0.29674200-0.00046598*skier['avg_points'].iloc[-1]**2+1.76564661
				skier_avg_points.append(avg_points)
			except Exception:
				#print(fantasy_names[b])
				#traceback.print_exc()
				skier_avg_points.append(0)
			try:
				exp = skier['exp'].iloc[-1]
				skier_exp.append(exp)
			except:
				skier_exp.append(0)
			try:
				age = skier['age'].iloc[-1]
				skier_age.append(age)
			except:
				skier_age.append(0)
			try:
				if(skier['nation'].iloc[-1]=="Italy"):
					#home = "TRUE"
					home = 1
				else:
					home= "FALSE"
					home = 0
				skier_home.append(home)
			except:
				skier_home.append(0)
				

			
		fantasydf['elo'] = skier_elo

		fantasydf['distance_elo'] = skier_distance_elo
		fantasydf['distance_classic_elo'] = skier_distance_classic_elo
		fantasydf['distance_freestyle_elo'] = skier_distance_freestyle_elo

		fantasydf['sprint_elo'] = skier_sprint_elo
		fantasydf['sprint_classic_elo'] = skier_sprint_classic_elo
		fantasydf['sprint_freestyle_elo'] = skier_sprint_freestyle_elo

		fantasydf['classic_elo'] = skier_classic_elo
		fantasydf['freestyle_elo'] = skier_freestyle_elo

		fantasydf['avg_points'] = skier_avg_points
		fantasydf['exp'] = skier_exp
		fantasydf['age'] = skier_age
		fantasydf['home'] = skier_home

		mendf = fantasydf.loc[fantasydf['sex']=='m']

		mendf = dezero(mendf)

		#Edit out these next three and the ladies three for pursuit.  One for actual
		
		mendf = mendf.sort_values(by='elo', ascending=False)
		mendf = mendf.reset_index(drop=True)

		#comment out next block for regression		
		'''
		mendf = mendf[:30]
		men_wc_scores = mendf['points'].tolist()
		men_wc_scores = men_wc_scores[:30]		
		men_wc_scores = np.add(men_wc_scores, wc)		
		men_wc_scores = pd.Series(men_wc_scores)
		mendf.loc[:30, 'points'] = men_wc_scores
		'''


		#Comment out next block for non-regression
		mendf['points'] = menintslope[0]
		men_vars[a] = [m.replace('pelo', 'elo') for m in men_vars[a]]
		men_vars[a] = [m.replace('pavg', 'avg') for m in men_vars[a]]
		ladies_vars[a] = [l.replace('pelo', 'elo') for l in ladies_vars[a]]
		ladies_vars[a] = [l.replace('pavg', 'avg') for l in ladies_vars[a]]

		
		for b in range(len(men_vars[a])):
			print(menintslope[b])
			mendf['points'] = mendf['points']+menintslope[b+1]*mendf[men_vars[a][b]]
		
		mendf['points'] = mendf['points'].fillna(0)
		
		
		mendf['points'].loc[mendf['points']<0] = 0

		#For normal WCP
		mendf['points'] = .030964*mendf['points']**2+.263557*mendf['points']+3.196429

		#for TDS
		#mendf['points'] = 0.093193*mendf['points']**2+0.787371*mendf['points']+9.215816 

		#For Stages
		#mendf['points'] = 0.045676*mendf['points']**2+0.178935*mendf['points']+2.531034

		
		mendfs.append(mendf)
		
		ladiesdf = fantasydf.loc[fantasydf['sex']=='f']

		ladiesdf = dezero(ladiesdf)
		

		ladiesdf = ladiesdf.sort_values(by='elo', ascending=False)
		ladiesdf = ladiesdf.reset_index(drop=True)

		ladiesdf['points'] = ladiesintslope[0]
		for b in range(len(ladies_vars[a])):
			ladiesdf['points'] = ladiesdf['points']+ladiesintslope[b+1]*ladiesdf[ladies_vars[a][b]]
		#Next block is for regression
		
		
		ladiesdf['points'] = ladiesdf['points'].fillna(0)
		ladiesdf['points'].loc[ladiesdf['points']<0] = 0

		#Individual
		ladiesdf['points'] = .263557*ladiesdf['points']+.030964*ladiesdf['points']**2+3.196429
		
		#TDS
		#ladiesdf['points'] = 0.787371 *ladiesdf['points']+0.093193*ladiesdf['points']**2+9.215816

		#Stages
		#ladiesdf['points'] = 0.045676*ladiesdf['points']**2+0.178935*ladiesdf['points']+2.531034

		#Next block is ladies non-regression
		'''
		ladies_wc_scores = ladiesdf['points'].tolist()
		ladies_wc_scores = ladies_wc_scores[:30]
		ladies_wc_scores = np.add(ladies_wc_scores, wc)
		ladies_wc_scores = pd.Series(ladies_wc_scores)
		ladiesdf.loc[:30, 'points'] = ladies_wc_scores
		'''
		ladiesdfs.append(ladiesdf)

	mendf = fantasydf.loc[fantasydf['sex']=='m']
	mendf = mendf.sort_values(by='id')
	mendf = mendf.reset_index(drop=True)
	ladiesdf = fantasydf.loc[fantasydf['sex']=='f']
	ladiesdf = ladiesdf.sort_values(by='id')
	ladiesdf = ladiesdf.reset_index(drop=True)
	

	for a in range(len(mendfs)):
		mendfs[a] = mendfs[a].sort_values(by='id')
		mendfs[a] = mendfs[a].reset_index(drop=True)
		elo_name = "elo"+str(a+1)
		race_name = "race"+str(a+1)
		mendf[elo_name] = mendfs[a]['elo']
		mendf[race_name] = mendfs[a]['points']
		mendf['points'] = mendf['points'] + mendf[race_name]
		ladiesdfs[a] = ladiesdfs[a].sort_values(by='id')
		ladiesdfs[a] = ladiesdfs[a].reset_index(drop=True)
		ladiesdf[elo_name] = ladiesdfs[a]['elo']
		ladiesdf[race_name] = ladiesdfs[a]['points']
		ladiesdf['points'] = ladiesdf['points'] + ladiesdf[race_name]







	
	#ladiesdf = ladiesdf[:30]
	#ladiesdf[:30, 'points'] += wc
	mendf=mendf.sort_values(by='points', ascending=False)
	ladiesdf =ladiesdf.sort_values(by='points', ascending=False)
	mendf = mendf[mendf['points']>0]
	ladiesdf = ladiesdf[ladiesdf['points']>0]
	mendf['place'] = np.arange(1, len(mendf['name'])+1, 1)
	ladiesdf['place'] = np.arange(1,len(ladiesdf['name'])+1,1)
	print(list(ladiesdf['name']).sort())
	fantasydf = mendf
	fantasydf = fantasydf.append(ladiesdf)

	fantasydf = fantasydf[['name', 'id', 'price', 'sex','points', 'race1', 'race2',  'place']]
	return fantasydf
			

#The point of pkl_setup is to add points and pct to the pkl
def pkl_setup(pkl):
	stage = [50, 46, 43, 40, 37, 34, 32, 30, 28, 26, 24, 22, 20, 18, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
	wc = [100, 80, 60, 50, 45, 40, 36, 32, 29, 26, 24, 22, 20, 18, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
	tour = [400, 320, 240, 200, 180, 160, 144, 128, 116, 104, 96, 88, 80, 72, 64, 60, 56, 52, 48, 44, 40, 36, 32, 28, 24, 20,20, 20, 20, 20]
	df = pd.read_pickle(pkl)



def regress_relay(df, vars_list):#, pkl):
	

	stage = [50, 46, 43, 40, 37, 34, 32, 30, 28, 26, 24, 22, 20, 18, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
	wc = [100, 80, 60, 50, 45, 40, 36, 32, 29, 26, 24, 22, 20, 18, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
	wc = [i*2 for i in wc]
	#tour = [400, 320, 240, 200, 180, 160, 144, 128, 116, 104, 96, 88, 80, 72, 64, 60, 56, 52, 48, 44, 40, 36, 32, 28, 24, 20,20, 20, 20, 20]
	#points = [100, 80, 60, 50, 45, 40, 36, 32, 29, 26, 24, 22, 20, 18, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
	
	#Set what type of race it is
	points = wc
	df = df.loc[df['level']=="all"]
	print(df)
	#max_elo = max(df['team_elo'])
	df = df.loc[df['season']>=2010]
	#df = df.loc[df['team_elo']!=5200]
	#df = df.loc[df['team_elo']!=2600]
	df2 = pd.DataFrame()
	seasons = pd.unique(df['season'])
	print(len(df['race']))
	df.loc[df['home']=="TRUE"] = 1
	df.loc[df['home']=="FALSE"] = 0

	#Relay
	df['points'] = df['points'].apply(lambda x: -.958832685276+.682250876756*x-.006352194332*x**2+0.000027600716*x**3-0.000000045133*x**4)
	

	df[vars_list] = df[vars_list]
	df = df.fillna(0)
	if('pavg_points' in vars_list):
		#Stage races
		df['pavg_points'] = df['pavg_points'].apply(lambda x: -.958832685276+.682250876756*x-.006352194332*x**2+0.000027600716*x**3-0.000000045133*x**4)
		
		#Tour de Ski
		#df['points'] = df['points'].apply(lambda x: 1.76564661+.296742*x-0.0046598*x**2)

		#df['pavg_points'] = df['pavg_points'].apply(lambda x: 0.1584908+0.29674200*x-0.00046598*x**2)
	
	
	y = df['points']
	x = df[vars_list]
	lm = LinearRegression()
	
	lm = LinearRegression().fit(x,y)
	coefs = [lm.intercept_]
	for a in range(len(vars_list)):
		coefs.append(lm.coef_[a])
	#print(coefs)
	print(coefs)
	return coefs

#The point of regress is to take the pkl from pkl_setup, add a regression to it to get expected points for the current race
#So it should return an intercept and a coefficient
def regress(df, vars_list):#, pkl):
	
	print(vars_list)

	stage = [50, 47, 44, 41, 38, 35, 32, 30, 28, 26, 24, 22, 20, 18, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
	wc = [100,95,90,85,80,75,72,69,66,63,60,58,56,54,52,50,48,46,44,42,40, 38, 36, 34, 32, 30, 28, 26, 24, 22, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
	tour = [300, 285, 270, 255, 240, 216, 207, 198, 189, 180, 174, 168, 162, 156, 150, 144, 138, 132, 126, 120, 114, 108, 102, 96, 90, 84, 78, 72, 66, 60, 57, 54, 51, 48, 45, 42, 39, 36, 33, 30, 27, 24, 21, 18, 15, 12, 9, 6, 3]
	#points = [100, 80, 60, 50, 45, 40, 36, 32, 29, 26, 24, 22, 20, 18, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
	
	#Set what type of race it is
	points = wc
	df = df.loc[df['level']=="all"]
	max_elo = max(df['elo'])
	df = df.loc[df['season']>=2018]
	#print(df['name'])
	#df = df.loc[df['total_pelo']!=1300]
	df2 = pd.DataFrame()
	seasons = pd.unique(df['season'])
	#print(len(df['race']))
	
	
	df.loc[df['home']=="TRUE"] = 1
	df.loc[df['home']=="FALSE"] = 0
	
	#Individual
	df['points'] = df['points'].apply(lambda x: 1.5865602+.896294*x-0.0042397*x**2)

	#Tour de Ski
	#df['points'] = df['points'].apply(lambda x: 1.76564661+.296742*x-0.0046598*x**2)

	#Stage races
	#df['points'] = df['points'].apply(lambda x: 0.1584908+1.0801595*x-0.0100871*x**2)
	

	
	
	df[vars_list] = df[vars_list]
	df = df.fillna(0)
	if('pavg_points' in vars_list):
		#Stage races
		df['pavg_points'] = df['pavg_points'].apply(lambda x: 1.5865602+.896294*x-0.0042397*x**2)
		
		#Tour de Ski
		#df['points'] = df['points'].apply(lambda x: 1.76564661+.296742*x-0.0046598*x**2)

		#df['pavg_points'] = df['pavg_points'].apply(lambda x: 0.1584908+0.29674200*x-0.00046598*x**2)
	
	
	y = df['points']
	x = df[vars_list]
	lm = LinearRegression()
	
	lm = LinearRegression().fit(x,y)
	coefs = [lm.intercept_]
	for a in range(len(vars_list)):
		coefs.append(lm.coef_[a])
	print(coefs)
	return coefs

def mixed_combo(relaydf, tsdf):
	
	relaydf['ts_elo'] = tsdf['team_elo']
	relaydf['relay_points'] = relaydf['points']
	relaydf['ts_points'] = tsdf['points']
	relaydf['points'] = relaydf['relay_points'] + relaydf['ts_points']

	return relaydf

	
	#lm = 

def dezero(df):
	print(df)
	df['elo'] = df['elo'].fillna(0)
	elo_list = list(df['elo'])
	#df['team_elo'] = df['team_elo'].fillna(0)
	#elo_list = list(df['team_elo'])
	elo_list = list(filter((0).__ne__,elo_list))
	elo_quant = np.quantile(elo_list,[.25])[0]
	#print(elo_quant)
	df['elo'] = df['elo'].replace([0], elo_quant)
	#df['team_elo'] = df['team_elo'].replace([0], elo_quant)
	
	#print('elo', list(df['elo']))

	df['distance_elo'] = df['distance_elo'].fillna(0)
	distance_elo_list = list(df['distance_elo'])
	distance_elo_list = list(filter((0).__ne__,distance_elo_list))
	distance_elo_quant = np.quantile(distance_elo_list,[.25])[0]
	df['distance_elo'] = df['distance_elo'].replace([0], distance_elo_quant)
	
	#print('distance_elo', list(df['distance_elo']))

	df['distance_classic_elo'] = df['distance_classic_elo'].fillna(0)
	distance_classic_elo_list = list(df['distance_classic_elo'])
	distance_classic_elo_list = list(filter((0).__ne__,distance_classic_elo_list))
	distance_classic_elo_quant = np.quantile(distance_classic_elo_list,[.25])[0]
	df['distance_classic_elo'] = df['distance_classic_elo'].replace([0], distance_classic_elo_quant)
	
	#print('distance_classic_elo', list(df['distance_classic_elo']))

	df['distance_freestyle_elo'] = df['distance_freestyle_elo'].fillna(0)
	distance_freestyle_elo_list = list(df['distance_freestyle_elo'])
	distance_freestyle_elo_list = list(filter((0).__ne__,distance_freestyle_elo_list))
	distance_freestyle_elo_quant = np.quantile(distance_freestyle_elo_list,[.25])[0]
	df['distance_freestyle_elo'] = df['distance_freestyle_elo'].replace([0], distance_freestyle_elo_quant)
	

	df['sprint_elo'] = df['sprint_elo'].fillna(0)
	sprint_elo_list = list(df['sprint_elo'])
	sprint_elo_list = list(filter((0).__ne__,sprint_elo_list))
	sprint_elo_quant = np.quantile(sprint_elo_list,[.25])[0]
	df['sprint_elo'] = df['sprint_elo'].replace([0], sprint_elo_quant)
	

	df['sprint_classic_elo'] = df['sprint_classic_elo'].fillna(0)
	sprint_classic_elo_list = list(df['sprint_classic_elo'])
	sprint_classic_elo_list = list(filter((0).__ne__,sprint_classic_elo_list))
	sprint_classic_elo_quant = np.quantile(sprint_classic_elo_list,[.25])[0]
	df['sprint_classic_elo'] = df['sprint_classic_elo'].replace([0], sprint_classic_elo_quant)
	print('sprint_classic_elo', sprint_classic_elo_quant, list(df['sprint_classic_elo']))

	df['sprint_freestyle_elo'] = df['sprint_freestyle_elo'].fillna(0)
	sprint_freestyle_elo_list = list(df['sprint_freestyle_elo'])
	sprint_freestyle_elo_list = list(filter((0).__ne__,sprint_freestyle_elo_list))
	sprint_freestyle_elo_quant = np.quantile(sprint_freestyle_elo_list,[.25])[0]
	df['sprint_freestyle_elo'] = df['sprint_freestyle_elo'].replace([0], sprint_freestyle_elo_quant)

	df['classic_elo'] = df['classic_elo'].fillna(0)
	classic_elo_list = list(df['classic_elo'])
	classic_elo_list = list(filter((0).__ne__,classic_elo_list))
	classic_elo_quant = np.quantile(classic_elo_list,[.25])[0]
	df['classic_elo'] = df['classic_elo'].replace([0], classic_elo_quant)

	
	df['freestyle_elo'] = df['freestyle_elo'].fillna(0)
	freestyle_elo_list = list(df['freestyle_elo'])
	freestyle_elo_list = list(filter((0).__ne__,freestyle_elo_list))
	freestyle_elo_quant = np.quantile(freestyle_elo_list,[.25])[0]
	df['freestyle_elo'] = df['freestyle_elo'].replace([0], freestyle_elo_quant)
	

	return df

	#WebDriverWait(driver, 30).until(EC.invisibility_of_element_located((By.XPATH,
	#	"//div[@class='js-off-canvas-overlay is-overlay-fixed']")))


#menpkls = ["~/ski/elo/python/ski/excel365/varmen_sprint_classic_k.pkl",
#"~/ski/elo/python/ski/excel365/varmen_distance_freestyle_k.pkl"]
'''menpkls = ["/Users/syverjohansen/ski/elo/python/ski/age/excel365/men_chrono_regress_sprint_freestyle.pkl",
"/Users/syverjohansen/ski/elo/python/ski/age/excel365/men_chrono_regress_distance_freestyle.pkl"] '''
menpkls = ["/Users/syverjohansen/ski/elo/python/ski/age/relay/excel365/men_chrono_regress_relay.pkl"]



men_AIC = [['age', 'pelo', 'distance_pelo', 'distance_classic_pelo', 'distance_freestyle_pelo', 'sprint_classic_pelo', 'sprint_freestyle_pelo', 'classic_pelo', 'freestyle_pelo', 'home']]


men_BIC = [['pelo', 'distance_pelo', 'distance_classic_pelo', 'distance_freestyle_pelo', 'classic_pelo', 'freestyle_pelo', 'home']]



men_R2 = [['age', 'pelo', 'distance_pelo', 'distance_classic_pelo', 'distance_freestyle_pelo', 'sprint_classic_pelo', 'sprint_freestyle_pelo', 'classic_pelo', 'freestyle_pelo', 'home']]


men_sprint = [['age', 'exp', 'pelo', 'distance_freestyle_pelo', 'sprint_classic_pelo', 'sprint_freestyle_pelo', 'classic_pelo', 'freestyle_pelo', 'home', 'pavg_points']]

men_distance = [['exp', 'pelo',  'distance_classic_pelo', 'distance_freestyle_pelo', 'sprint_classic_pelo',  'classic_pelo', 'freestyle_pelo',  'pavg_points']]


men_vars = men_AIC

#,
	#"~/ski/elo/python/ski/excel365/varmen_distance_freestyle_k.pkl"]
	#"~/ski/elo/python/ski/men/varmen_sprint_classic.pkl"]


'''ladiespkls = ["/Users/syverjohansen/ski/elo/python/ski/age/excel365/ladies_chrono_regress_sprint_freestyle.pkl",
"/Users/syverjohansen/ski/elo/python/ski/age/excel365/ladies_chrono_regress_distance_freestyle.pkl"]'''
ladiespkls = ["/Users/syverjohansen/ski/elo/python/ski/age/relay/excel365/ladies_chrono_regress_relay.pkl"]


ladies_AIC = [['age', 'exp', 'pelo', 'distance_pelo', 'distance_classic_pelo', 'distance_freestyle_pelo', 'sprint_freestyle_pelo', 'classic_pelo', 'freestyle_pelo']]

ladies_BIC = [['age', 'pelo', 'distance_classic_pelo', 'sprint_freestyle_pelo', 'classic_pelo', 'freestyle_pelo']]


ladies_R2 = [['exp', 'pelo', 'distance_pelo', 'distance_classic_pelo', 'distance_freestyle_pelo', 'sprint_pelo', 'sprint_classic_pelo', 'sprint_freestyle_pelo', 'classic_pelo', 'freestyle_pelo', 'home']]


ladies_sprint = [['age', 'pelo', 'distance_pelo', 'distance_freestyle_pelo', 'sprint_pelo', 'sprint_classic_pelo', 'classic_pelo', 'pavg_points']]

ladies_distance = [['age', 'distance_pelo', 'distance_classic_pelo', 'sprint_pelo', 'freestyle_pelo', 'pavg_points']]

ladies_vars = ladies_AIC


	#"~/ski/elo/python/ski/excel365/varladies_distance_freestyle_k.pkl"]
#relaypkls = ["~/ski/elo/python/ski/relay/radar/varmen_distance_k.pkl"]
#tspkls = ["~/ski/elo/python/ski/relay/radar/varmen_sprint_k.pkl"]

#men_chrono = pd.read_pickle("/Users/syverjohansen/ski/elo/python/ski/age/excel365/men_chrono_regress.pkl")
#ladies_chrono = pd.read_pickle("/Users/syverjohansen/ski/elo/python/ski/age/excel365/ladies_chrono_regress.pkl")

men_chrono = pd.read_pickle("/Users/syverjohansen/ski/elo/python/ski/age/relay/excel365/men_chrono_regress.pkl")
ladies_chrono = pd.read_pickle("/Users/syverjohansen/ski/elo/python/ski/age/relay/excel365/ladies_chrono_regress.pkl")


#df = pd.read_pickle(ladiespkls[0])
#regress(df)

#startlist = fis()
startlist = fis_relay()
#startlist = fis_mixed_relay()
#startlist = fis_team_sprint()

#fantasydf = (fantasy(startlist))
fantasydf = fantasy_relay(startlist)
#fantasydf = fantasy_mixed_relay(startlist)
#fantasydf = fantasy_team_sprint(startlist)
#with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
 #   print(fantasydf)
#print(fantasydf)
#print(fantasydf)



#fantasydf = elo(fantasydf, menpkls, ladiespkls, men_vars, ladies_vars, men_chrono, ladies_chrono)
#fantasydf = pursuit(fantasydf)
fantasydf = elo_relay(fantasydf, menpkls, ladiespkls, men_vars, ladies_vars, men_chrono, ladies_chrono)
#fantasydf = elo_mixed_relay(fantasydf, menpkls, ladiespkls, relaypkls)
#print(fantasydf)
#fantasydf = elo_team_sprint(fantasydf, menpkls, ladiespkls, men_vars, ladies_vars, men_chrono, ladies_chrono)
#print(fantasydf)
'''men_relay_skier_pkls = ["~/ski/elo/python/ski/relay/excel365/varmen_distance_k.pkl"]#,
ladies_relay_skier_pkls = ["~/ski/elo/python/ski/relay/excel365/varladies_distance_k.pkl"]#,
relaypkls = ["~/ski/elo/python/ski/relay/radar/varmen_distance_k.pkl"]
men_ts_skier_pkls = ["~/ski/elo/python/ski/relay/excel365/varmen_distance_k.pkl"]#,
ladies_ts_skier_pkls = ["~/ski/elo/python/ski/relay/excel365/varladies_distance_k.pkl"]#,
tspkls = ["~/ski/elo/python/ski/relay/radar/varmen_distance_k.pkl"]

mixed_relay_startlist = fis_mixed_relay()
mixed_relay_fantasydf = fantasy_mixed_relay(mixed_relay_startlist)
mixed_relay_fantasydf = elo_mixed_relay(mixed_relay_fantasydf, men_relay_skier_pkls, ladies_relay_skier_pkls, relaypkls)
mixed_ts_startlist = fis_mixed_ts()
mixed_ts_fantasydf = fantasy_mixed_ts(mixed_ts_startlist)
mixed_ts_fantasydf = elo_mixed_ts(mixed_ts_fantasydf, men_ts_skier_pkls, ladies_ts_skier_pkls, tspkls)
fantasydf = mixed_combo(mixed_relay_fantasydf, mixed_ts_fantasydf)
print(fantasydf)'''

fantasydf.to_pickle("~/ski/elo/knapsack/excel365/fantasydf_toblach_relay_BIC.pkl")
fantasydf.to_excel("~/ski/elo/knapsack/excel365/fantasydf_toblach_relay_BIC.xlsx")


print(time.time() - start_time)

