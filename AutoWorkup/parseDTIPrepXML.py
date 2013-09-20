import os
from glob import glob
import re
from xml.etree import ElementTree as et
import datetime
import sqlite3 as lite
import csv
import math

class ParseXML():

    def __init__(self):
        self.SQLiteCommandList = list()

    def main(self):
        xmlFileList = self.getXMLFileList()
        self.parseXMLFileList(xmlFileList)
        return self.SQLiteCommandList

    def getXMLFileList(self):
        base_dir = '/scratch/20130913_Parse_DTIPrep_XML'
        xml_file_pattern = '{0}/*.xml'.format(base_dir)
        xmlFileList = glob(xml_file_pattern)
        return xmlFileList

    def parseXMLFileList(self, xmlFileList):
        for xmlFile in xmlFileList:
            print xmlFile
            tree = et.parse(xmlFile)
            root = tree.getroot()
            for child in root[2][3:]:
                gradient = child.attrib['parameter']
                gradDirs = child[1][0].text.strip().split(' ')
                print gradDirs
                (rho, theda, phi) = self.calculateSphericalCoordinates(float(gradDirs[0]),float(gradDirs[1]),float(gradDirs[2]))
                processing = child[0].text
                print child.attrib['parameter'], child[1][0].text, child[0].text
                fieldDict = {'filepath' : xmlFile,
                             'gradient' : gradient,
                             'xval' : gradDirs[0],
                             'yval' : gradDirs[1],
                             'zval' : gradDirs[2],
                             'rho' : rho,
                             'theda' : theda,
                             'phi' : phi,
                             'processing' : processing}
                print fieldDict
                self.makeSQLiteCommand(fieldDict)

    def calculateSphericalCoordinates(self, x, y, z):
        rho = math.sqrt((x**2 + y**2 + z**2))
        if x != 0:
            theda = math.degrees(math.atan2(y, x))
        else:
            theda = 0.0
        if rho != 0:
            phi = math.degrees(math.acos(z/rho))
            phi2 = math.degrees(math.atan2(math.sqrt(x**2+y**2),z))
        else:
            phi = 0.0
            phi2 = 0.0
        # print "rho = ", rho, " theda = ", theda, " phi = ", phi, " phi2 = ", phi2
        # print
        return str(rho), str(theda), str(phi)

    def makeSQLiteCommand(self, image_info):
        keys = image_info.keys()
        vals = image_info.values()
        col_names = ",".join(keys)
        values = ', '.join(map(lambda x: "'" + x + "'", vals))
        SQLite_command = "INSERT INTO dtiprep ({0}) VALUES ({1});".format(col_names, values)
        self.SQLiteCommandList.append(SQLite_command)
        # print self.SQLiteCommandList
        print

class FillDB():

    def __init__(self, sqlDBcommandList):
        self.dbFileName = "dtiprepxml.db"
        self.sqlDBcommandList = sqlDBcommandList
        #self.output_dir = os.path.join(args.basePath, args.superProject,'reports', datetime.date.today().isoformat())
        #if os.path.exists(self.output_dir):
        #    pass
        #else:
        #    os.mkdir(self.output_dir)

    def main(self):
        self.createDB()
        self.fillDB()

    def createDB(self):
        """
        Create the DTIPrep Output SQLite database that will contain all of
        the information parsed from the XML files.
        """
        ## column titles and types for the ImageEval SQLite database
        dbColTypes =  'filepath TEXT, gradient TEXT, xval REAL, yval REAL, zval REAL, ' \
                      'rho REAL, theda REAL, phi REAL, processing TEXT'
        if os.path.exists(self.dbFileName):
            os.remove(self.dbFileName)
        con = lite.connect(self.dbFileName)
        dbCur = con.cursor()
        dbCur.execute("CREATE TABLE dtiprep({0});".format(dbColTypes))
        dbCur.close()

    def fillDB(self):
        con = lite.connect(self.dbFileName)
        dbCur = con.cursor()
        for command in self.sqlDBcommandList:
            dbCur.execute(command)
            con.commit()
        dbCur.close()

class PrintReport():

    def __init__(self):
        self.dbFileName = "dtiprepxml.db"

    def main(self):
        self.printReport()
        # self.deleteDB()

    def getInfoFromDB(self, SQLiteCommand):
        con = lite.connect(self.dbFileName)
        dbCur = con.cursor()
        dbCur.execute(SQLiteCommand)
        DBinfo = dbCur.fetchall()
        dbCur.close()
        return DBinfo

    def printReport(self):
        outputDir = ''
        path = os.path.join(outputDir,"{0}_DTIPrep_Output_XML.csv".format(datetime.date.today().isoformat()))
        Handle = csv.writer(open(path, 'wb'), quoting=csv.QUOTE_ALL)
        col_name_list = ['filepath, gradient, xval, yval, zval, rho, theda, phi, processing']
        Handle.writerow(col_name_list)
        SQLiteCommand = "SELECT filepath, gradient, xval, yval, zval, rho, theda, phi, processing " \
                        "FROM dtiprep ORDER BY filepath, gradient;"
        DBinfo = self.getInfoFromDB(SQLiteCommand)
        for line in DBinfo:
            Handle.writerow(line)

    def deleteDB(self):
        os.remove(self.dbFileName)

if __name__ == "__main__":
    ParserObject = ParseXML()
    sqlDBcommandList = ParserObject.main()
    DBObject = FillDB(sqlDBcommandList)
    DBObject.main()
    ReportObject = PrintReport()
    ReportObject.main()
