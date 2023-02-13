from urllib.error import HTTPError
from urllib.error import URLError
import logging
from socket import timeout
import ssl
import re
ssl._create_default_https_context = ssl._create_unverified_context
from urllib.request import urlopen
from bs4 import BeautifulSoup
import xlsxwriter
import requests
import time
start_time = time.time()
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}

def convert_month(month):
	if(month=='Jan'):
		return '01'
	elif(month=='Feb'):
		return '02'
	elif(month=='Mar'):
		return '03'
	elif(month=='Apr'):
		return '04'
	elif(month=='May'):
		return '05'
	elif(month=='Jun'):
		return '06'
	elif(month=='Jul'):
		return '07'
	elif(month=='Aug'):
		return '08'
	elif(month=='Sep'):
		return '09'
	elif(month=='Oct'):
		return '10'
	elif(month=='Nov'):
		return '11'
	elif(month=='Dec'):
		return '12'

def get_date(worldcup_page):
	worldcup_soup = BeautifulSoup(urlopen(worldcup_page), 'html.parser')
	body = worldcup_soup.body.find_all('table', {'class':'tablesorter'})
	body = body[1]
	body = body.find_all('td')
	date = (body[-3].text)
	date = str(date)
	date = date.split(" ")
	year = date[2]
	date = "".join(date[1])
	
	date = date.split(".")
	month = convert_month(date[1])
	#print(month)
	day = date[0]
	day = day.zfill(2)
	date = (year+month+day)
	return date


def get_table(worldcup_page):
	w0 = 0
	to_worldcup_page = []
	to_worldcup_page.append(worldcup_page)
	while(len(to_worldcup_page)>0):
		if(w0>=len(to_worldcup_page)):
			w0 = 0
		try:
			worldcup_page = urlopen(to_worldcup_page[w0], timeout=10)
			to_worldcup_page.remove(to_worldcup_page[w0])
		except:
			w0+=1
			pass

	worldcup_soup = BeautifulSoup(worldcup_page, 'html.parser')
	body = worldcup_soup.body.find_all('table', {'class':'tablesorter'})

	body = body[1]
	body = body.find_all('td')
	try:
		date = (body[-3].text)

		date = str(date)
		date = date.split(" ")
		
		year = date[2]
		date = "".join(date[1])
		date = date.split(".")
		month = date[1]
		month = month.split(",")[0]
		
		month = convert_month(month)
		
		day = date[0]
		day = day.zfill(2)
		date = (year+month+day)
	except:
		date = (body[-1].text)
		date = str(date).split("/")
		year = date[1]
		date = year+"0101"
		

	city = body[5].text

	country = body[7].text.strip()

	distance = body[3].text#.split(" ")
	if(distance=="Nordic Combined"):
		return -1
	elif(distance=="Team"):
		return -1
	elif(distance=="Individual"):
		distance = "Gundersen K90/15km"
	elif(distance=="Sprint"):
		distance = "Sprint K90/7.5km"
	distance = distance.split(" ")
	

	if(distance[0]=="Team" or distance[0]=="\tTeam"):
		return -1
	elif(distance[0]=="Mass" or distance[0]=="Hurricane" or distance[0]=="Compact" or distance[0]=="Penalty"):

		distance = distance[1:]

	distance = distance[1]
	distance = distance.split("/")
	hill = distance[0]

	distance = distance[1]


	hill = hill.split("HS")
	
	if(len(hill)==1):
		hill = hill[0]
		hill = hill.split("K")[1]
		
	else:
		hill = hill[1]

	hill = int(hill[1])
	

	distance = distance.split("km")
	if(len(distance)<2):
		distance = distance[0]
		distance = distance.split("Km")



	distance = float(distance[0])
	#distance = distance[0]

	

	#distance = distance[0]

	if(hill >= 110):
		hill = "Large"
	else:
		hill = "Small"


		
	table = [date, city, country, hill, distance]
	return table
	
		
	#return worldcup_date
def get_skier(worldcup_page, distance):
	w0 = 0
	to_worldcup_page = []
	to_worldcup_page.append(worldcup_page)
	while(len(to_worldcup_page)>0):
		if(w0>=len(to_worldcup_page)):
			w0 = 0
		try:
			worldcup_page = urlopen(to_worldcup_page[w0], timeout=10)
			to_worldcup_page.remove(to_worldcup_page[w0])
		except:
			w0+=1
			pass
	worldcup_soup = BeautifulSoup(worldcup_page, 'html.parser')
	body = worldcup_soup.body.find_all('table', {'class':'tablesorter sortTabell'})
	body = body[0]
	body = body.find_all('td')
	places = []
	skier = []
	nation = []
	ski_ids = []
	people = 1
	for a in range(len(body)):
		
		if(a%8==0):

			if(str(body[a].text)!="DNS"
				and str(body[a].text)!="DNQ" and str(body[a].text)!="DSQ" and str(body[a].text)!="OOT" and ("DNF" not in str(body[a].text))):
				places.append(body[a].text)
				
				ski_id = str(body[a+3])
				
				ski_id = ski_id.split("td>")[1]
				ski_id = ski_id.split("</td")[0]

				ski_id = ski_id.split("ID=")#[1]
				ski_id = ski_id[1]
				
				ski_id = str(ski_id.split("\"")[0])
				ski_ids.append(ski_id)
				skier.append(body[a+3].text.strip('\n'))
				nation.append(body[a+5].text)
			else:
				break

		if(distance=="Rel" and people>12):
			break
		elif(distance!="Rel" and people>10):
			break
	
	
	return [places, skier, nation, ski_ids]


def get_team(worldcup_page, distance):
	worldcup_soup = BeautifulSoup(urlopen(worldcup_page), 'html.parser')
	body = worldcup_soup.body.find_all('table', {'class':'tablesorter sortTabell'})
	body = body[0]
	body = body.find_all('td')
	places = []
	skier = []
	nation = []
	people = 1
	for a in range(len(body)):
		
		if(a%7==0):
			people+=1
			places.append(body[a].text)
			skier.append(body[a+2].text.strip('\n'))
			nation.append(body[a+4].text)

		
	return [places, skier, nation]


def get_worldcup():
	men_worldcup_page1 = []
	ladies_worldcup_page1 = []
	
	
	for a in range(1924, 2023):
		print(a)
		men_worldcup_page0 = "https://skisport365.com/kombinert/rennkalender.php?aar="+str(a)
		ladies_worldcup_page0 = "https://skisport365.com/kombinert/rennkalender.php?aar="+str(a)+"&k=F"
		

		try:
			men_worldcup_page0 = urlopen(men_worldcup_page0, timeout=10)	
		except:
			m0 = 0
			to_men_worldcup_page0 = []
			to_men_worldcup_page0.append(men_worldcup_page0)
			while(len(to_men_worldcup_page0)>0):
				if(m0>=len(to_men_worldcup_page0)):
					m0=0
				try:
					men_worldcup_page0 = urlopen(to_men_worldcup_page0[m0], timeout=10)	
					to_men_worldcup_page0.remove(to_men_worldcup_page0[m0])
				except:
					m0+=1
					pass
		
		try:
			ladies_worldcup_page0 = urlopen(ladies_worldcup_page0, timeout=10)	
		except:
			l0 = 0
			to_ladies_worldcup_page0 = []
			to_ladies_worldcup_page0.append(ladies_worldcup_page0)
			while(len(to_ladies_worldcup_page0)>0):
				if(l0>=len(to_ladies_worldcup_page0)):
					l0=0
				try:
					ladies_worldcup_page0=urlopen(to_ladies_worldcup_page0[l0], timeout=19)
					to_ladies_worldcup_page0.remove(to_ladies_worldcup_page0[l0])
				except:
					l0+=1
					pass



		#ladies_worldcup_page0 = urlopen(ladies_worldcup_page0)
		men_worldcup_soup0 = BeautifulSoup(men_worldcup_page0, 'html.parser')
		ladies_worldcup_soup0 = BeautifulSoup(ladies_worldcup_page0, 'html.parser')
		

		for b in men_worldcup_soup0.find_all('a', {'class':'ablue'}, href = True):
			men_worldcup_page1.append('https://skisport365.com/kombinert/'+b['href'])
		

		for b in ladies_worldcup_soup0.find_all('a', {'class':'ablue'}, href=True):
			ladies_worldcup_page1.append('https://skisport365.com/kombinert/'+b['href'])
	

	


	men_worldcup_page3 = []
	ladies_worldcup_page3 = []
	men_worldcup = []
	ladies_worldcup = []
	worldcup = []
	for a in range(len(men_worldcup_page1)):
	

		table = get_table(men_worldcup_page1[a])
		
		if(table==-1):
			continue
		date = table[0]
		print(date)
		city = table[1]
		country = table[2]
		category = "all"
		sex = "M"
		hill = table[3]
		distance = table[4]
		
		
		
		
		skiers = get_skier(men_worldcup_page1[a], distance)
		places = skiers[0]
		ski = skiers[1]
		nation = skiers[2]
		ski_ids = skiers[3]
		menwc = [date, city, country, category, sex, hill, distance, places, ski, nation, ski_ids]
		if(distance!="Rel" and distance!="Ts"):
			men_worldcup.append(menwc)

	for a in range(len(ladies_worldcup_page1)):
		
		table = get_table(ladies_worldcup_page1[a])
		if(table==-1):
			continue
		date = table[0]
		print(date)
		city = table[1]
		country = table[2]
		category = "all"
		sex = "L"
		hill = table[3]
		distance = table[4]
		
		
		skiers = get_skier(ladies_worldcup_page1[a], distance)
		places = skiers[0]
		ski = skiers[1]
		nation = skiers[2]
		ski_ids = skiers[3]
		ladieswc = [date, city, country, category, sex, hill, distance,  places, ski, nation, ski_ids]
		if(distance!="Rel" and distance!="Ts"):
			ladies_worldcup.append(ladieswc)

	#worldcup = ladies_worldcup
	#worldcup.extend(men_worldcup)
	return [ladies_worldcup, men_worldcup]
		
			

		#print(table)
	

#date, city, country, category, sex, distance, discipline, places, name
worldcup = get_worldcup()

workbook = xlsxwriter.Workbook("/Users/syverjohansen/ski/elo/python/nc/excel365/all.xlsx")
ladies = workbook.add_worksheet("Ladies")
men = workbook.add_worksheet("Men")




for g in range(len(worldcup)):
	#print(worldcup[g])
	if(g==0):
		row = 0
		col = 0
		for a in range(len(worldcup[g])):
			for b in range(len(worldcup[g][a][8])):
				ladies.write(row, col, worldcup[g][a][0])
				ladies.write(row, col+1, worldcup[g][a][1])
				ladies.write(row, col+2, worldcup[g][a][2])
				ladies.write(row, col+3, worldcup[g][a][3])
				ladies.write(row, col+4, worldcup[g][a][4])
				ladies.write(row, col+5, worldcup[g][a][5])
				ladies.write(row, col+6, worldcup[g][a][6])
				
		
				ladies.write(row, col+7, worldcup[g][a][7][b])
				#print(worldcup[g][a][0])
				#print(worldcup[g][a][7][b])
				ladies.write(row, col+8, worldcup[g][a][8][b])
				#print(worldcup[g][a][8][b])
				ladies.write(row, col+9, worldcup[g][a][9][b])
				ladies.write(row, col+10, worldcup[g][a][10][b])
				#print(worldcup[g][a][9][b])
				row+=1
	else:
		row = 0
		col = 0
		for a in range(len(worldcup[g])):
			for b in range(len(worldcup[g][a][8])):
				men.write(row, col, worldcup[g][a][0])
				men.write(row, col+1, worldcup[g][a][1])
				men.write(row, col+2, worldcup[g][a][2])
				men.write(row, col+3, worldcup[g][a][3])
				men.write(row, col+4, worldcup[g][a][4])
				men.write(row, col+5, worldcup[g][a][5])
				men.write(row, col+6, worldcup[g][a][6])
			
				men.write(row, col+7, worldcup[g][a][7][b])
				men.write(row, col+8, worldcup[g][a][8][b])
				men.write(row, col+9, worldcup[g][a][9][b])
				men.write(row, col+10, worldcup[g][a][10][b])
				row+=1


workbook.close()
print(time.time() - start_time)







