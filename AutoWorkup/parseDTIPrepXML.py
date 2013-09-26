import os
from glob import glob
from xml.etree import ElementTree as et
import math
from fillDB import FillDB
from makePlots import MakePlots

class ParseXML():

    def __init__(self):
        self.SQLiteCommandList = list()

    def main(self):
        xmlFileList = self.getXMLFileList()
        self.parseXMLFileList(xmlFileList)
        return self.SQLiteCommandList

    def getXMLFileList(self):
        base_dir = '/scratch/20130913_Parse_DTIPrep_XML'
        xml_file_pattern = '{0}/_SESSION_ID_*/dtiPrep/*.xml'.format(base_dir)
        xmlFileList = glob(xml_file_pattern)
        return xmlFileList

    def parseXMLFileList(self, xmlFileList):
        print xmlFileList
        for xmlFile in xmlFileList:
            print xmlFile
            pathElements = list(xmlFile.split(os.path.sep))
            fileName = pathElements.pop()
            container = pathElements.pop() # dtiPrep
            session = pathElements.pop().replace("_SESSION_ID_","")
            year = session.split("_")[-2][0:4]
            self.processingDict = dict()
            tree = et.parse(xmlFile)
            root = tree.getroot()
            for child in root[2][3:]:
                gradient = child.attrib['parameter']
                gradDirs = child[1][0].text.strip().split(' ')
                print child.attrib['parameter'], child[1][0].text, child[0].text
                xval = float(gradDirs[0])
                yval = float(gradDirs[1])
                zval = float(gradDirs[2])
                if zval < 0:
                    xval *= -1
                    yval *= -1
                    zval *= -1
                # print gradDirs
                (rho, theta, phi) = self.calculateSphericalCoordinates(
                    xval, yval, zval)
                print rho, theta, phi
                processing = child[0].text
                fieldDict = {'filepath' : xmlFile,
                             'project' : 'TEMP_PROJECT',
                             'session' : session,
                             'year' : year,
                             'gradient' : gradient,
                             'xval' : gradDirs[0],
                             'yval' : gradDirs[1],
                             'zval' : gradDirs[2],
                             'rho' : str(rho),
                             'theta' : str(theta),
                             'phi' : str(phi),
                             'processing' : processing}
                self.makeSQLiteCommand(fieldDict)

    def calculateSphericalCoordinates(self, x, y, z):
        rho = math.sqrt((x**2 + y**2 + z**2))
        if x != 0:
            phi = math.degrees(math.atan2(y, x))
        else:
            phi = 0.0
        if rho != 0:
            theta = math.degrees(math.acos(z/rho))
            # theta2 = math.degrees(math.atan2(math.sqrt(x**2+y**2),z))
        else:
            theta = 0.0
        return str(rho), str(theta), str(phi)

    def makeSQLiteCommand(self, image_info):
        keys = image_info.keys()
        vals = image_info.values()
        col_names = ",".join(keys)
        values = ', '.join(map(lambda x: "'" + x + "'", vals))
        SQLite_command = "INSERT INTO dtiprep ({0}) VALUES ({1});".format(col_names, values)
        self.SQLiteCommandList.append(SQLite_command)
        # print self.SQLiteCommandList
        print


if __name__ == "__main__":
    ParserObject = ParseXML()
    (sqlDBcommandList) = ParserObject.main()
    DBObject = FillDB(sqlDBcommandList)
    DBObject.main()
    PlotObject = MakePlots()
    PlotObject.main()
