import os
from glob import glob
from xml.etree import ElementTree as et
import datetime
import sqlite3 as lite
import csv
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages as pdfpages
from coordtransform import cartesian_to_spherical

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
                [rho1, theta1, phi1] = cartesian_to_spherical([
                    float(gradDirs[0]), float(gradDirs[1]), float(gradDirs[2])])
                print rho1, math.degrees(theta1), math.degrees(phi1)
                processing = child[0].text
                fieldDict = {'filepath' : xmlFile,
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
                self.appendEntryProcessingDict(processing, phi, theta)
                # print fieldDict
                self.makeSQLiteCommand(fieldDict)
            self.plotThetaVsPhi(self.processingDict, session)
            self.processingDict = dict()

    def plotThetaVsPhi(self, procDict, session):
        pointColors = {'EXCLUDE_SLICECHECK':'rs', 'BASELINE_AVERAGED':'ys', 'EDDY_MOTION_CORRECTED':'bo',
                       3:'y', 4:'c', 5:'m', 6:'k'}
        for key in procDict.keys():
            if key == 'BASELINE_AVERAGED':
                continue
            plt.plot(procDict[key][0], procDict[key][1], pointColors[key],label=key)
            plt.title('Processing Type at Point Theta Vs. Phi \nfor Session {0}\n'.format(session), fontsize = 'large')
            plt.xlabel("\nPhi (degrees)", fontsize = 'large')
            plt.ylabel("Theta (degrees) \n", fontsize = 'large')
            plt.axis([-180, 180, 0, 90])
            plt.subplots_adjust(bottom = 0.2, top = 0.86, right = .88, left = 0.15)
            plt.legend(fontsize = 'small', bbox_to_anchor=(0., -.27, 1., .02), loc=3,
                  ncol=2, mode="expand", borderaxespad=0.,shadow=True)
            print key, len(procDict[key][0])
            print procDict[key]
        pp = pdfpages('{}_ProcessingInfoPerGradient.pdf'.format(session))
        pp.savefig()
        pp.close()
        plt.close()

    def appendEntryProcessingDict(self, processing, theta, phi):
        if processing in self.processingDict.keys():
            self.processingDict[processing][0].append(theta)
            self.processingDict[processing][1].append(phi)
        else:
            self.processingDict[processing] = [[theta],[phi]]

    def calculateSphericalCoordinates(self, x, y, z):
        rho = math.sqrt((x**2 + y**2 + z**2))
        if x != 0:
            phi = math.degrees(math.atan2(y, x))
        else:
            phi = 0.0
        if rho != 0:
            theta = math.degrees(math.acos(z/rho))
            theta2 = math.degrees(math.atan2(math.sqrt(x**2+y**2),z))
        else:
            theta = 0.0
            theta = 0.0
        # print "rho = ", rho, " theta = ", theta, " phi = ", phi, " phi2 = ", phi2
        # print
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
                      'rho REAL, theta REAL, phi REAL, processing TEXT'
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
        col_name_list = ['filepath, gradient, xval, yval, zval, rho, theta, phi, processing']
        Handle.writerow(col_name_list)
        SQLiteCommand = "SELECT filepath, gradient, xval, yval, zval, rho, theta, phi, processing " \
                        "FROM dtiprep ORDER BY filepath, gradient;"
        DBinfo = self.getInfoFromDB(SQLiteCommand)
        for line in DBinfo:
            Handle.writerow(line)

    def deleteDB(self):
        os.remove(self.dbFileName)

if __name__ == "__main__":
    ParserObject = ParseXML()
    sqlDBcommandList = ParserObject.main()
    # DBObject = FillDB(sqlDBcommandList)
    # DBObject.main()
    # ReportObject = PrintReport()
    # ReportObject.main()
