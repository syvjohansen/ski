import pandas as pd
import numpy as np


mendf = pd.read_pickle("~/ski/elo/python/biathlon/mendf.pkl")

def EA (pelos, index):
    players = len(pelos)
    ra = pelos[index]
    QA = 10**(ra/400) 
    QA = np.repeat(QA, players - 1)
    rb = np.delete(np.array(pelos), index)
    QB = 10**(rb/400)
    EA = QA / (QA + QB)
    return EA

def SA(place_vector, place):
    place_vector = np.array(place_vector)
    losses = (place_vector < place).sum()
    draws = np.count_nonzero(place_vector == place) - 1
    wins = (place_vector > place).sum()
    return losses*[0] + draws*[0.5] + wins*[1]



def male_elo():
	#Step 1: Figure out the person's previous elo.  
	#If they aren't in the new dataframe, make them a new score (1300)
	menelodf = pd.DataFrame()
	#menelodf.columns = ['date', 'city', 'country', 'level', 'sex', 'distance', 
	#'discipline', 'place', 'name', 'nation','season','race', 'pelo', 'elo']
	
	id_pool = []
	max_races = max(mendf['race'])
	#Print the unique seasons
	seasons = (pd.unique(mendf['season']))
	for season in range(len(seasons)):
	#for season in range(10):
		print(seasons[season])

		seasondf = mendf.loc[mendf['season']==seasons[season]]
		races = pd.unique(seasondf['race'])
		K = float(38/len(races))
		for race in range(len(races)):
			pelo_list = []
			elo_list = []
			racedf = seasondf.loc[seasondf['race']==races[race]]
			racedf.reset_index(inplace=True, drop=True)
			for a in range(len(racedf['id'])):
				if (racedf['id'][a] not in id_pool):
					id_pool.append(racedf['id'][a])
					pelo_list.append(1300)
				else:
					#print("yo")
					#Get the vet skiers line
					vetskier = menelodf.loc[menelodf['id']==racedf['id'][a]]
					pelo_list.append(vetskier['elo'].iloc[-1])

				#else we have to find them and see if they are the same person
				#else we have to find their last elo in menelodf

			racedf['pelo'] = pelo_list
			PLACES = list(racedf['place'])
			for i,p in enumerate(PLACES):
				elo_list.append(pelo_list[i] + K*(sum(SA(PLACES, PLACES[i])) - sum(EA(pelo_list,i))))

			racedf['elo'] = elo_list
			menelodf = menelodf.append(racedf)
			#print(menelodf)

		endseasondate = int(str(seasons[season])+'0500')
		#print(endseasondate)
		for n in range(len(id_pool)):
			endskier = menelodf.loc[menelodf['id']==id_pool[n]]
			endname = endskier['name'].iloc[-1]
			endpelo = endskier['elo'].iloc[-1]
			endelo = endpelo*.85+1300*.15
			endnation = endskier['nation'].iloc[-1]
			endf = pd.DataFrame([[endseasondate, "Summer", "Break", "end", "M", 0, None, 0
				, endname, endnation, id_pool[n],seasons[season], 0, endpelo, endelo]], columns = menelodf.columns)
			menelodf = menelodf.append(endf)

	return menelodf	

menelodf = male_elo()
menelodf.to_pickle("~/ski/elo/python/biathlon/simmale.pkl") #changed
menelodf.to_excel("~/ski/elo/python/biathlon/simmale.xlsx") #changed


#def male_elo():