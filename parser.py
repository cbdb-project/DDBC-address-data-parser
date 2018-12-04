import re

# If you want to add or remove globalFieldName, you must to redefine it in globalFieldNameOrder list
globalFieldName = {}
globalFieldName["ID"] = "規範碼"
globalFieldName["oldID"] = "舊規範碼"
globalFieldName["classification"] = "地名分類"
globalFieldName["coord"] = "經緯度"
globalFieldName["x"] = "經度"
globalFieldName["y"] = "緯度："
globalFieldName["belongs"] = "屬"
globalFieldName["currentBelongs"] = "行政區"
globalFieldName["notes"] = "備註"
globalFieldName["dynasty"] = "朝代"
# The content of "別名" was in next line, so we have to remove the \n after "別名："
globalFieldName["altname"] = "別名"
globalFieldName["anno"] = "註解"
# The content of "Occurs in：" was in next line, so we have to remove the \n after "Occurs in："
# The bad news is that there might be multiple lines which belong to a single "Occurs in：". This
# problem was solved by data = re.sub(r"\n([a-zA-Z]\d)", r";\1", data) in reFormCrosslineData
globalFieldName["OccursIn"] = "Occurs in"

# Define the output field order here
globalFieldNameOrder = [globalFieldName["ID"], globalFieldName["oldID"], globalFieldName["classification"], globalFieldName["x"], globalFieldName["y"], globalFieldName["belongs"], globalFieldName["currentBelongs"], globalFieldName["notes"], globalFieldName["dynasty"], globalFieldName["altname"], globalFieldName["anno"], globalFieldName["OccursIn"]]

globalRemoveList = [r"\(僅供參考請勿使用\)", r"\(精確值\)  download KML   Map", r"Feedback"]

# The regular expression for x and y
coordRE = r"緯度：(\d+\.\d+)經度：(\d+\.\d+)"

# If the line end by "引用網址", it means that this is the address name of this entry
addrNameSymbol = "引用網址"

def removeContentFromRemoveList(data):
    for i in globalRemoveList:
        data = re.sub(i, "", data)
    return data

def reFormCrosslineData(data):
# work on 别名
    data = re.sub(r"%s：\n"%(globalFieldName["altname"]), r"%s："%(globalFieldName["altname"]), data)
# work on occurs in
    data = re.sub(r"\n([a-zA-Z]\d)", r";\1", data)
    data = re.sub(r"%s：;"%(globalFieldName["OccursIn"]), r"%s："%(globalFieldName["OccursIn"]), data)
    return data
    
def readfile(fileName):
    with open(fileName, "r", encoding="utf8") as f:
        data = f.read()
# Remove the data from globalRemoveList
        cleanedData = removeContentFromRemoveList(data)
# Move the next line after "occur in" and "别名" to current line
        cleanedData = reFormCrosslineData(cleanedData)
    outputList = cleanedData.split("\n")
    return outputList

# Remove (zhēn dìng fǔ) from 真定府(zhēn dìng fǔ)
def removePinyinFromAddrName(data):
    return re.sub(r"\(.+\)", "", data)

def parseToDic(inputDataList):
    output = {}
    outputIndex = ""
    tempList =[""]*len(globalFieldName)
# The title seperated by ：
    currentTitle = ""
# The content seperated by ：
    currentContent = []
    for i in inputDataList:
# Find address name by using addrNameSymbol(引用網址)
        if addrNameSymbol in i:
            addrName = i[:(len(i)-len(addrNameSymbol)-1)]
            addrName = removePinyinFromAddrName(addrName)
# To read the first line
            if outputIndex== "":
                tempList[0] = addrName
# Find the next entry. It's a trigger to save current entry
# !!! Each entry should be ended here
            elif outputIndex!="":
                output[outputIndex] = tempList
                #print(output[outputIndex])
                outputIndex = ""
                tempList =[""]*len(globalFieldName)
                tempList[0] = addrName
# Use ：to seperate title and content
        currentInputDataListSplit = i.split("：")
# If there is at least one ：
        if len(currentInputDataListSplit)>1:
            currentTitle = currentInputDataListSplit[0]
            currentContent = i[len(currentTitle)+1:]
# Use "規範碼" as the unique index
            if currentTitle == globalFieldName["ID"]:
                outputIndex = currentContent.strip()
# Seperate x and y to differnt cells
            elif currentTitle == globalFieldName["coord"]:
                y, x = re.findall(coordRE, currentContent)[0]
                tempList[globalFieldNameOrder.index(globalFieldName["x"])] = x.strip()
                tempList[globalFieldNameOrder.index(globalFieldName["y"])] = y.strip()
            else:
                tempList[globalFieldNameOrder.index(currentTitle)] = currentContent.strip()
# Save the last reocrd
    if outputIndex!="":
        output[outputIndex] = tempList
        return output

def writeFile(dataDic, fileName):
    output = []
    for i, j in dataDic.items():
        line = "%s\t%s"%(i, "\t".join(j))
        output.append(line)
    with open(fileName, "w", encoding="utf8") as f:
        f.write("\n".join(output))



# Step 1, create input.txt:
# 1. Read DDBC html file by browser. 2. CtrlA to get all the data. 3. copy and paste that data to input.txt
#
# Step 2, please detele the paragraphs at the top of the page, Ex:
# *Z碼系統使用GRS67經緯度座標系統，與GPS或Google Earth使用WGS84經緯度座標系統略有不同，有需要可利用「Web版坐標轉換程式」進行座標轉換
#
# 檢索【 】(地名：257 筆，群組：0 筆) ：
# 。朝代過濾器(不含群組)：
# Step 3, run parser.py. My environment is python3.5

inputDataList = readfile("input.txt")

# Convert the raw data to a dictionary, use 規範碼 as the index
dataDic = parseToDic(inputDataList)

# Convert data to a list, and save it to csv
writeFile(dataDic, "output.txt")
