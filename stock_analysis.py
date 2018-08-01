# encoding: utf-8
import math
import requests
import re
import sys
import urllib.request
import chardet
import time
import os
import os.path
import platform
from bs4 import BeautifulSoup
from operator import attrgetter
import numpy as np

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36'}
rs = requests.session()

class StockInfo:
        def __init__(self, id, name, PredictEarningRatio, PredictLossRatio, RiskEarningRatio, clPrice, PredictHighestPrice, PredictLowestPrice, PEG):
                self.id = id
                self.name = name
                self.PredictEarningRatio = PredictEarningRatio
                self.PredictLossRatio = PredictLossRatio
                self.RiskEarningRatio = RiskEarningRatio
                self.clPrice = clPrice
                self.PredictHighestPrice = PredictHighestPrice
                self.PredictLowestPrice = PredictLowestPrice
                self.PEG = PEG
        def __repr__(self):
                return repr((self.id, self.name, self.PredictEarningRatio, self.PredictLossRatio, self.RiskEarningRatio, self.clPrice, self.PredictHighestPrice, self.PredictLowestPrice, self.PEG))


###+++6/28 show more info+++###

class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False
        
    def __repr__(self):
                return repr((self.id))
    
    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False

###global variable###


###---6/28 show more info---###

#Test for jsjustweb
def evaluate(stockID):
#+++
	#print ("show_moreInfo:" + stockID)
	#file.write("股票代號:" + stockID + "\n")
	meaningful = True
	# 抓本益比
	urlforPE = "http://jsjustweb.jihsun.com.tw/z/zc/zca/zca_" + stockID + ".djhtm"
	response = urllib.request.urlopen(urlforPE)
	webdata = response.read()
	sp = BeautifulSoup(webdata.decode('cp950'), "html.parser")
	response.close()

	if ("" !=  sp.find('td',{'class':'t10'})):
		name_tbl = sp.find('td',{'class':'t10'}).get_text(' ').split()[0]
		#print ('name_tbl:' + name_tbl.get_text(' ').split()[0])
		#if (sp.select('.t10').length() == 0)
	else :
		name_tbl = sp.find('option').get_text();
		#print ('name_tbl:' + name_tbl.get_text())
	

	###########################################################
	tbls_new = sp.select('.t01 td');
	for idx,tb in enumerate(tbls_new):
		#印出所以元素
		#print(str(idx)+" ["+tb.get_text()+"]")
		#switch case判斷
		for case in switch(tb.get_text()):
				if case('開盤價'):
					open_Price = tbls_new[idx+1].get_text()
					#print ('開盤價: '+tbls_new[idx+1].get_text())
					#print ('開盤價: '+open_Price)
					break
				if case('本益比'):
					now_PE = tbls_new[idx+1].get_text()
					#print ('目前本益比: '+now_PE)
					break
				if case('最高本益比'):
					highPE_List = []
					new_highPE_List = []
					for i,mtb in enumerate(tb.parent.find_all("td")):
						#第一個是string
						if (i != 0 and mtb.get_text() != "" and mtb.get_text() != "N/A"):
							#print(str(mtb.get_text()))
							#將資料一個個塞進List當中
							highPE_List.append(float(mtb.get_text().replace(",", "")))
					#print ('最高本益比:'+str(highPE_List))
					if (highPE_List != []):
						highPE_List.pop(0)
					#print ('最高本益比:'+str(highPE_List))
					break
				if case('最低本益比'):
					lowPE_List = []
					#new_lowPE_List = []
					for i,mtb in enumerate(tb.parent.find_all("td")):
						#第一個是string
						if (i != 0 and mtb.get_text() != "" and mtb.get_text() != "N/A"):
							#print(str(mtb.get_text()))
							#將資料一個個塞進List當中
							lowPE_List.append(float(mtb.get_text().replace(",", "")))
					#print ('最低本益比:'+str(lowPE_List))
					if (lowPE_List != []):
						lowPE_List.pop(0)
					break					
				if case('營收比重'):
					product_radio = tbls_new[idx+1].get_text()
					#print ('營收比重: '+tbls_new[idx+1].get_text())
					break
				if case('一年內最高價'):
					highest_Price_in_a_year = tbls_new[idx+1].get_text()
					break
				if case('一年內最低價'):
					lowerest_Price_in_a_year = tbls_new[idx+1].get_text()
					break


	#print ("股票代號2:" + stockID)
	urlforMProfitYoY = "http://jsjustweb.jihsun.com.tw/z/zc/zch/zch_" + stockID + ".djhtm"
	response = urllib.request.urlopen(urlforMProfitYoY)
	webdata = response.read()
	spYOY = BeautifulSoup(webdata.decode('cp950'), "html.parser")
	response.close()
	tbls = spYOY.select('.t01 td');
	#tbls = sp.find('年增率');
	#print (tbls)
	index_YOY = True
	counter_YOY=0
	YOY_List = []
	Latest_YOY = 0
	meaningfulYOY = True
	#meaningful = True
	for idx,tb in enumerate(tbls):
		#印出所以元素
		#print(str(idx)+" ["+tb.get_text()+"]")
		#switch case判斷
		for case in switch(tb.get_text()):
			if case('年增率'):
				if (index_YOY):
					#for i in tbls:
					for i in tbls:
						counter_YOY+=1
						if (len(tbls[idx+7*counter_YOY].get_text()) < 1):
							index_YOY = False
							break

						element_YOY = float(tbls[idx+7*counter_YOY].get_text().replace("%", "").replace(",",""))
						#element_YOY = tbls[idx+7*counter_YOY].get_text()
						#if (float(tbls[idx+7*counter_YOY].get_text().replace("%", "")) != "N/A" or float(tbls[idx+7*counter_YOY].get_text().replace("%", "")) != ""):
						if (str(element_YOY) != "N/A" or str(element_YOY) != ""):
							YOY_List.append(element_YOY)
							#print("YOY_List: " + str(YOY_List))
							#print ('年增率: '+tbls[idx+7*counter_YOY].get_text())
							'''if(element_YOY < 0):
								index_YOY = False
								meaningfulYOY = False
								print("YOY_List: " + str(YOY_List))
								#print("YOY 有負數!")
								break'''
							if (counter_YOY==6):
								index_YOY = False
								#print("年增率: " + str(YOY_List))
								#mean_YOY = float(format(np.mean(YOY_List), '.2f'))
								#new_amean = format(np.mean(new_lowPE_List)*0.9, '.2f')
								#print("年增率平均: " + str(mean_YOY))
								break
							elif (counter_YOY == 1):
								Latest_YOY = float(YOY_List[0])
								#print("Latest_YOY:" + str(Latest_YOY))

						else:
							index_YOY = False
							meaningfulYOY = False
							#print("YOY 為N/A or Null")

			break
#---
	name = name_tbl
	print ("股票代號:" + stockID + " " +name_tbl)
	file.write("股票代號:" + stockID + " " +name_tbl + "\n")
	print("營收比重: "+product_radio)
	file.write("營收比重: "+product_radio+ "\n")
	meaningful = True
	# 抓本益比
	'''urlforPE = "http://jsjustweb.jihsun.com.tw/z/zc/zca/zca_" + stockID + ".djhtm"
	response = urllib.request.urlopen(urlforPE)
	webdata = response.read()
	sp = BeautifulSoup(webdata.decode('cp950'), "html.parser")
	response.close()'''

	tbls = sp.find_all('table', attrs={'border' : '0'})
	trs = tbls[0].find_all('tr')
	tds = trs[6].find_all('td')
	PE = tds[1].get_text()
	PE = PE.replace(",", "")

	# 收盤價
	tds = trs[4].find_all('td')
	if (tds[7].get_text() != "" and tds[7].get_text() != "N/A"):
		closePrice = float(tds[7].get_text().replace(",", ""))
	print("開盤價:" + str(open_Price))
	file.write("開盤價:" + str(open_Price)+ "\n")
	print ("收盤價:" + str(closePrice))
	file.write("收盤價:" + str(closePrice) + "\n")
	print ("一年內最高價:" + str(highest_Price_in_a_year) + "\t"+"一年內最低價:" + str(lowerest_Price_in_a_year))
	file.write("一年內最高價:" + str(highest_Price_in_a_year) + "\t")
	#print ("一年內最低價:" + str(lowerest_Price_in_a_year))
	file.write("一年內最低價:" + str(lowerest_Price_in_a_year) + "\n")
	print("目前本益比: "+ now_PE)
	file.write("目前本益比: "+ now_PE+ "\n")

	PENoData = False
	SmallThreshold = 2
	LargeThreshold = 2
	SmallMaxPE = 0
	LargeMinPE = 0
	LatestMaxPE = 0
	LatestMinPE = 0
	MaxPEList = []
	MinPEList = []
	# 最高本益比
	SumMaxPE = 0
	if (len(trs) >= 27):
		trs = trs[27].find_all('tr')
		tds = trs[3].find_all('td')
		if (len(tds) >= 6):
			for i in range(1,6):
				if (tds[i].get_text() != "" and tds[i].get_text() != "N/A"):
					MaxPE = float(tds[i].get_text().replace(",", ""))

					if (i == 1):
						LatestMaxPE = MaxPE
						SmallMaxPE = MaxPE
						MaxPEList.append(MaxPE)
					else:
						if (SmallMaxPE < 10):
							Threshold = SmallThreshold
						else:
							Threshold = LargeThreshold

						if (MaxPE < SmallMaxPE*Threshold and MaxPE > SmallMaxPE/Threshold):
							MaxPEList.append(MaxPE)
							if (MaxPE < SmallMaxPE):
								SmallMaxPE = MaxPE
				else:
					PENoData = True
					break;
		else:
			PENoData = True
	else:
		PENoData = True

	if (PENoData == False):
		SumMaxPE = 0
		for MaxPE in MaxPEList:
			SumMaxPE = SumMaxPE + MaxPE 
		AvgMaxPE = SumMaxPE/len(MaxPEList)

		SumDiff = 0
		for MaxPE in MaxPEList:
			SumDiff = SumDiff + (MaxPE-AvgMaxPE)**2
		Delta = (SumDiff/len(MaxPEList))**0.5

		SumMaxPE = 0
		Num = 0
		for MaxPE in MaxPEList:
			if (MaxPE <= (AvgMaxPE + 2*Delta) and MaxPE >= (AvgMaxPE - 2*Delta)):
				SumMaxPE = SumMaxPE + MaxPE 
				Num = Num + 1
		AvgMaxPE = SumMaxPE/Num

	PENoData = False
	# 最低本益比
	SumMinPE = 0
	if (len(tds) >=4):
		tds = trs[4].find_all('td')
		if (len(tds) >= 6):
			for i in range(1,6):
				if (tds[i].get_text() != "" and tds[i].get_text() != "N/A"):
					MinPE = float(tds[i].get_text().replace(",", ""))

					if (i == 1):
						LatestMinPE = MinPE
						LargeMinPE = MinPE
						MinPEList.append(MinPE)
					else:
						if (LargeMinPE < 10):
							Threshold = SmallThreshold
						else:
							Threshold = LargeThreshold

						if (MinPE < LargeMinPE*Threshold and MinPE > LargeMinPE/Threshold):
							MinPEList.append(MinPE)
							if (MinPE > LargeMinPE):
								LargeMinPE = MinPE
				else:
					PENoData = True
					break;
		else:
			PENoData = True
	else:
		PENoData = True
	print("目前最高本益比表:" + str(highPE_List))
	print("目前最低本益比表:" + str(lowPE_List))
	file.write("目前最高本益比表:" + str(highPE_List)+ "\n")
	file.write("目前最低本益比表:" + str(lowPE_List)+ "\n")
	if (PENoData == False):
		SumMinPE = 0
		for MinPE in MinPEList:
			SumMinPE = SumMinPE + MinPE 
		AvgMinPE = SumMinPE/len(MinPEList)

		SumDiff = 0
		for MinPE in MinPEList:
			SumDiff = SumDiff + (MinPE-AvgMinPE)**2
		Delta = (SumDiff/len(MinPEList))**0.5

		SumMinPE = 0
		Num = 0
		for MinPE in MinPEList:
			if (MinPE <= (AvgMinPE + 2*Delta) and MinPE >= (AvgMinPE - 2*Delta)):
				SumMinPE = SumMinPE + MinPE 
				Num = Num + 1
		AvgMinPE = SumMinPE/Num

		if (LatestMaxPE < AvgMaxPE):
			PredictMaxPE = LatestMaxPE
		else:
			PredictMaxPE = AvgMaxPE

		if (LatestMinPE < AvgMinPE):
			PredictMinPE = LatestMinPE
		else:
			PredictMinPE = AvgMinPE

		LatestAvgPE = (LatestMaxPE + LatestMinPE)/2
		print ("預估本益比:" + format(PredictMaxPE, '.2f') + "~" + format(PredictMinPE, '.2f') )
		file.write("預估本益比:" + format(PredictMaxPE, '.2f') + "~" + format(PredictMinPE, '.2f') + "\n")
	else:
		meaningful = False
		print ("本益比無法預估")
		file.write("本益比無法預估" + "\n")

	# 預估營收年增率
	'''urlforMProfitYoY = "http://jsjustweb.jihsun.com.tw/z/zc/zch/zch_" + stockID + ".djhtm"
	response = urllib.request.urlopen(urlforMProfitYoY)
	webdata = response.read()
	sp = BeautifulSoup(webdata.decode('cp950'), "html.parser")
	response.close()'''
	
	tbls = spYOY.find_all('table', attrs={'border' : '0', 'width' : '600'})
	# 近六個月每月營收年增率 > 0, min(latest_YOY,Avg)
	print("最近年營收表:" + str(YOY_List))
	file.write("最近年營收表:" + str(YOY_List)+ "\n")
	trs = tbls[0].find_all('tr')
	match = True
	PredictedProfitMonth = 0
	if (len(trs) >= 13):
		ProfitMonthAcc = 0
		for i in range(7,13):
			tds = trs[i].find_all('td')
			if (len(tds) >= 4):
				ProfitMonth = tds[4].get_text().strip('%')
				if (ProfitMonth != "" and ProfitMonth != "N/A"):
					ProfitMonth = ProfitMonth.replace(",", "")
					if float(ProfitMonth) < 0:
						match = False
						print ("營收年增率有負值:" +str(ProfitMonth))
						file.write("營收年增率有負值:" +str(ProfitMonth) + "\n")
						break;
					else:
						ProfitMonthAcc = ProfitMonthAcc + float(ProfitMonth)
						if i == 7:
							latest_YOY = float(ProfitMonth)
				else:
					match = False
					break;
			else:
				match = False
				break;
	else:
		match = False

	if match:
		AvgYoY = ProfitMonthAcc/6
		if AvgYoY < latest_YOY:
			PredictedProfitMonth = AvgYoY
		else:
			PredictedProfitMonth = latest_YOY

		print ("預估營收年增率:" + format(PredictedProfitMonth, '.2f'))
		file.write("預估營收年增率:" + format(PredictedProfitMonth, '.2f') + "\n")
	else:
		meaningful = False
		print ("營收年增率無法正確預估")
		file.write("營收年增率無法正確預估" + "\n")

	# 預估營收
	urlforYearEarning = "http://jsjustweb.jihsun.com.tw/z/zc/zcdj_" + stockID + ".djhtm"
	response = urllib.request.urlopen(urlforYearEarning)
	webdata = response.read()
	sp = BeautifulSoup(webdata.decode('cp950'), "html.parser")
	response.close()

	tbls = sp.find_all('table', attrs={'border' : '0', 'width' : '600'})
	trs = tbls[0].find_all('tr')
	if (len(trs) >=3):
		tds = trs[3].find_all('td')

		if (len(tds) >=2):
			LastYearEarning = tds[2].get_text().replace(",", "")
			if (LastYearEarning != "" and LastYearEarning != "N/A"):
				LastYearEarning = LastYearEarning.replace(",", "")
				PredictedEarning = float(LastYearEarning)*(1+PredictedProfitMonth/100)
				print ("預估營收:" + format(PredictedEarning, '.2f'))
				file.write("預估營收:" + format(PredictedEarning, '.2f') + "\n")
			else:
				meaningful = False
				print ("營收無法正確預估")
				file.write("營收無法正確預估" + "\n")
		else:
			meaningful = False
			print ("營收無法正確預估")
			file.write("營收無法正確預估" + "\n")
	else:
		meaningful = False
		print ("營收無法正確預估")
		file.write("營收無法正確預估" + "\n")

	# 預估稅後淨利率
	urlforProfitRatio = "http://jsjustweb.jihsun.com.tw/z/zc/zcd_" + stockID + ".djhtm"
	response = urllib.request.urlopen(urlforProfitRatio)
	webdata = response.read()
	sp = BeautifulSoup(webdata.decode('cp950'), "html.parser")
	response.close()

	tbls = sp.find_all('table', attrs={'border' : '0', 'width' : '600'})
	trs = tbls[0].find_all('tr')
	match = True

	if (len(trs) >= 7):
		ProfitRatioAcc = 0
		highest = 0
		lowest = 0
		for i in range(3,7):
			tds = trs[i].find_all('td')
			if i == 3:
				capital =float(tds[1].get_text().replace(",", ""))

			Income = tds[2].get_text()
			if (Income != "" and Income != "N/A"):
				Income = float(tds[2].get_text().replace(",", ""))
			else:
				print ("營收無資料")
				file.write("營收無資料" + "\n")
				match = False
				break;

			NetProfit = tds[4].get_text()
			if (NetProfit != "" and NetProfit != "N/A"):
				NetProfit = float(tds[4].get_text().replace(",", ""))
			else:
				print ("稅後淨利無資料")
				file.write("稅後淨利無資料" + "\n")
				match = False
				break;

			if (Income != 0):
				ProfitRatio = NetProfit/Income
			else:
				print ("營收為0")
				file.write("營收為0" + "\n")
				match = False
				break;

			if ProfitRatio > 0:
				ProfitRatioAcc = ProfitRatioAcc + ProfitRatio

				if highest == 0:
					highest = ProfitRatio
					lowest = ProfitRatio

				if ProfitRatio > highest:
					highest = ProfitRatio
				if ProfitRatio < lowest:
					lowest = ProfitRatio

				#if (highest > lowest*1.25):
				#	print ("稅後淨利率高低變化超過25%")
				#	file.write ("稅後淨利率高低變化超過25%" + "\n")
				#	match = False
				#	break;
			else:
				print ("稅後淨利率有負數")
				file.write("稅後淨利率有負數" + "\n")
				match = False
				break;

		if match:
			PredictProfitRatio = ProfitRatioAcc/4
			print ("預估稅後淨利率:" + format(PredictProfitRatio, '.3f'))
			file.write("預估稅後淨利率:" + format(PredictProfitRatio, '.3f') + "\n")
		else:
			meaningful = False
			print ("稅後淨利率無法正確預估")
			file.write("稅後淨利率無法正確預估" + "\n")

	# 抓近兩年EPS
	EPSNoData = False
	EPSYoY = -1
	urlforEPS = "http://jsjustweb.jihsun.com.tw/z/zc/zcdj_" + stockID + ".djhtm" 
	response = urllib.request.urlopen(urlforEPS)
	webdata = response.read()
	sp = BeautifulSoup(webdata.decode('cp950'), "html.parser")
	response.close()

	tbls = sp.find_all('table', attrs={'border' : '0', 'width' : '600'})
	trs = tbls[0].find_all('tr')

	EPSYearList = []
	if (len(trs) >= 5):
		for i in range(3,5):
			tds = trs[i].find_all('td')
			EPSYear = tds[7].get_text()
			if (EPSYear != "" and EPSYear != "N/A" and float(EPSYear) != 0):
				EPSYearList.append(float(EPSYear))
			else:
				EPSNoData = True
				break;
	else:
		EPSNoData = True

	if (EPSNoData == False):
		EPSYoY = EPSYearList[0] / EPSYearList[1] -1

	if meaningful:
		PredictEPS = PredictedEarning * PredictProfitRatio *100 / capital *10
		print ("預估EPS:" + format(PredictEPS, '.3f'))
		file.write("預估EPS:" + format(PredictEPS, '.3f') + "\n")
		PredictHighestPrice = PredictEPS*PredictMaxPE
		PredictLowestPrice = PredictEPS*PredictMinPE
		print ("預估股價高低落點:" + format(PredictHighestPrice, '.2f') + "~" + format(PredictLowestPrice, '.2f'))
		file.write("預估股價高低落點:" + format(PredictHighestPrice, '.2f') + "~" + format(PredictLowestPrice, '.2f') + "\n")

		PredictEarningRatio = (PredictHighestPrice - closePrice) / closePrice
		print ("預估報酬率:" + format(PredictEarningRatio, '.2f'))
		file.write("預估報酬率:" + format(PredictEarningRatio, '.2f') + "\n")

		PredictLossRatio = (closePrice - PredictLowestPrice) / closePrice
		print ("預估風險:" + format(PredictLossRatio, '.2f'))
		file.write("預估風險:" + format(PredictLossRatio, '.2f') + "\n")

		if (PredictLossRatio < 0):
			RiskEarningRatio = abs(PredictEarningRatio / 0.01)
		else:
			RiskEarningRatio = abs(PredictEarningRatio / PredictLossRatio)
		print ("風險報酬倍數:" + format(RiskEarningRatio, '.2f'))
		file.write("風險報酬倍數:" + format(RiskEarningRatio, '.2f') + "\n")

		# 計算PEG
		if (EPSNoData == False and LatestAvgPE > 0 and EPSYoY > 0):
			PEG = closePrice / PredictEPS / EPSYoY /100
			print ("PEG:" + format(PEG, '.2f'))
			print ("============")
			file.write("PEG:" + format(PEG, '.2f') + "\n")
			file.write("============" + "\n")
		else:
			PEG = 0
			print ("PEG無法計算出")
			print ("============")
			file.write("PEG無法計算出" + "\n")
			file.write("============" + "\n")
		return StockInfo(stockID, name, PredictEarningRatio, PredictLossRatio, RiskEarningRatio, closePrice, PredictHighestPrice, PredictLowestPrice, PEG)

	if (int(option) == 2):
		print ("============")
		file.write("============" + "\n")

	# file.close()
	return 0

def calculateAll():
	res = rs.get('http://www.emega.com.tw/js/StockTable.htm', headers = headers)
	url = "http://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
	url2 = "http://isin.twse.com.tw/isin/C_public.jsp?strMode=4"

	try:
		response = urllib.request.urlopen(url)
		webdata = response.read()
		sp = BeautifulSoup(webdata.decode('cp950'), "html.parser")
		response.close()

		tbls = sp.find_all('table', attrs={'border' : '0'})
		trs = tbls[0].find_all('tr')

		Results = []
		i = 1
		while i > 0 :
			tds = trs[i].find_all('td')
			text = tds[0].get_text().split()[0]
			if ( text == "上市認購(售)權證"):
				break;
			else:
				if (text != "股票"):
					#print ("stockID:" + text)
					if text != "2597" and text != "8081" and text != "3711" :
						result = evaluate(text)
						if (result != 0):
							Results.append(result)
				#else:
					#print ("Not invalid ID")
			i = i + 1
		
		response = urllib.request.urlopen(url2)
		webdata = response.read()
		sp = BeautifulSoup(webdata.decode('cp950'), "html.parser")
		response.close()

		tbls = sp.find_all('table', attrs={'border' : '0'})
		trs = tbls[0].find_all('tr')
		i = 1
		mstock_tag = False
		while i > 0 :
			tds = trs[i].find_all('td')
			text = tds[0].get_text().split()[0]
			if ( text == "臺灣存託憑證"):
				print ("111:" + text)
				mstock_tag = False
				break;
			else:
				if ( text == "00744B" ):
					print ("sttt:" + text)
					mstock_tag = True
				elif (text != "股票") and (mstock_tag):
					print ("stockID:" + text)
					if text != "2597" and text != "8081" and text != "3711" :
						result = evaluate(text)
						if (result != 0):
							Results.append(result)
			i = i + 1




		"""for result in Results:
			print ("StockID:"  + result.id)
			print ("EarningRatio:"  + format(result.PredictEarningRatio, '.2f'))
			print ("LossRatio:"  + format(result.PredictLossRatio, '.2f'))
			print ("RiskEarningRatio:"  + format(result.RiskEarningRatio, '.2f'))
			print ("ClosePrice:"  + format(result.clPrice, '.2f'))
			print ("HighestPrice:"  + format(result.PredictHighestPrice, '.2f'))
			print ("LowestPrice:"  + format(result.PredictLowestPrice, '.2f'))
			print ("PEG:"  + format(result.PEG, '.2f'))
			print ("============")"""

		SortResult = sorted(Results, reverse=True, key=attrgetter('PredictEarningRatio'))

		for i in range(0,75):
			print ("StockID:"  + SortResult[i].id)
			print ("StockName:" + SortResult[i].name)
			print ("EarningRatio:"  + format(SortResult[i].PredictEarningRatio, '.2f'))
			print ("PEG:" + format(SortResult[i].PEG, '.2f'))#add peg
			print ("============")
			file.write ("StockID:"  + SortResult[i].id + "\n")
			file.write ("StockName:" + SortResult[i].name + "\n")
			file.write ("EarningRatio:"  + format(SortResult[i].PredictEarningRatio, '.2f') + "\n")
			file.write("PEG:" + format(SortResult[i].PEG, '.2f') + "\n")
			file.write ("============" + "\n")

	except urllib.error.HTTPError:
		print ('There was an error with the request')
		file.write ("There was an error with the request")

	return 0

	
def openFiles(stockID):
	if (platform.system() == "Windows"):
		desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
	elif (platform.system() == "Linux"):
		desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
	save_path = desktop + "/stock_analysis"
	if not os.path.exists(save_path):
		os.makedirs(save_path)
	name_of_file = time.strftime("%Y-%m-%d") + stockID
	completeName = os.path.join(save_path, name_of_file+".txt")
	global file
	file = open(completeName, 'w')

def closeFiles():
	if not file.closed:
		file.close()

if __name__ == "__main__":
	while (True):
		print ("=========請選擇功能==========")
		print ("1.計算單一股票的財務分析(輸入股票代碼)")
		print ("2.找出財務分析優良的股票(default:10)")
		print ("輸入Q/q以離開")
		option = input (">>>")

		if (option.upper() == 'Q'):
			exit();

		if (int(option) == 1):
			print ("請輸入股票代碼")
			id  = input (">>>")
		
			if id != "2597" and id != "8081" and id != "3711":
				openFiles("_" + id)
				evaluate(id)
				closeFiles()
			else:
				print ("不支援該ID")
		elif (int(option) == 2):
			openFiles("")
			Result = calculateAll()
			closeFiles()
#def processInput():
 #   x = raw_input(">>> Input: ")
  #  print x

#while (True):
#   processInput()

