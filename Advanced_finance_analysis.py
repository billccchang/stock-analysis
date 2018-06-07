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

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36'}
rs = requests.session()

class StockInfo:
        def __init__(self, id, PredictEarningRatio, PredictLossRatio, RiskEarningRatio, clPrice, PredictHighestPrice, PredictLowestPrice, PEG):
                self.id = id
                self.PredictEarningRatio = PredictEarningRatio
                self.PredictLossRatio = PredictLossRatio
                self.RiskEarningRatio = RiskEarningRatio
                self.clPrice = clPrice
                self.PredictHighestPrice = PredictHighestPrice
                self.PredictLowestPrice = PredictLowestPrice
                self.PEG = PEG
        def __repr__(self):
                return repr((self.id, self.PredictEarningRatio, self.PredictLossRatio, self.RiskEarningRatio, self.clPrice, self.PredictHighestPrice, self.PredictLowestPrice, self.PEG))

#Test for jsjustweb
def evaluate(stockID):
	
	print ("股票代號:" + stockID)
	file.write("股票代號:" + stockID + "\n")
	meaningful = True
	# 抓本益比
	urlforPE = "http://jsjustweb.jihsun.com.tw/z/zc/zca/zca_" + stockID + ".djhtm"
	response = urllib.request.urlopen(urlforPE)
	webdata = response.read()
	sp = BeautifulSoup(webdata.decode('cp950'), "html.parser")
	response.close()

	tbls = sp.find_all('table', attrs={'border' : '0'})
	trs = tbls[0].find_all('tr')
	tds = trs[6].find_all('td')
	PE = tds[1].get_text()
	PE = PE.replace(",", "")

	# 收盤價
	tds = trs[4].find_all('td')
	if (tds[7].get_text() != "" and tds[7].get_text() != "N/A"):
		closePrice = float(tds[7].get_text().replace(",", ""))
	print ("收盤價:" + str(closePrice))
	file.write("收盤價:" + str(closePrice) + "\n")

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
	urlforMProfitYoY = "http://jsjustweb.jihsun.com.tw/z/zc/zch/zch_" + stockID + ".djhtm"
	response = urllib.request.urlopen(urlforMProfitYoY)
	webdata = response.read()
	sp = BeautifulSoup(webdata.decode('cp950'), "html.parser")
	response.close()
	
	tbls = sp.find_all('table', attrs={'border' : '0', 'width' : '600'})
	# 近六個月每月營收年增率 > 0, min(latest_YOY,Avg)
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

		PredictLossRatio = (PredictLowestPrice - closePrice) / closePrice
		print ("預估風險:" + format(PredictLossRatio, '.2f'))
		file.write("預估風險:" + format(PredictLossRatio, '.2f') + "\n")

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
		return StockInfo(stockID, PredictEarningRatio, PredictLossRatio, RiskEarningRatio, closePrice, PredictHighestPrice, PredictLowestPrice, PEG)

	if (int(option) == 2):
		print ("============")
		file.write("============" + "\n")

	# file.close()
	return 0

def calculateAll():
	res = rs.get('http://www.emega.com.tw/js/StockTable.htm', headers = headers)
	url = "http://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
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
			print ("EarningRatio:"  + format(SortResult[i].PredictEarningRatio, '.2f'))
			print ("============")
			file.write ("StockID:"  + SortResult[i].id + "\n")
			file.write ("EarningRatio:"  + format(SortResult[i].PredictEarningRatio, '.2f') + "\n")
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

