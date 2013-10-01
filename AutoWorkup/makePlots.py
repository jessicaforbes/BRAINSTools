import datetime
import os
from matplotlib.backends.backend_pdf import PdfPages as pdfpages
import sqlite3 as lite
import matplotlib.pyplot as plt

class MakePlots():

    def __init__(self):
        self.dbFileName = "dtiprepxml.db"
        self.tableName = "dtiprep"

    def main(self):
        # self.plotPerSite()
        # self.plotPerSitePerYear()
        self.scatterPlot()

    def scatterPlot(self):
        path = os.path.join("test_SCATTER_{0}_Plots_By_Site_DTIPrep_Output_XML.pdf".format(datetime.date.today().isoformat()))
        pp = pdfpages(path)
        site_list = self.getListFromDB("SELECT DISTINCT project FROM {} ORDER BY project;".format(self.tableName))
        for site in site_list:
            bins = self.getBins(site)
            (x, y, percentGoodList, size) = self.makePlotLists(bins)
            print x, y, percentGoodList, size
            print
            self.setPlotAttributes('Processing Type at Point Phi Vs. Theta \nfor Project {0}\n'.format(site))
            plt.scatter(x, y, s=size, c=percentGoodList)
            print percentGoodList
            # plt.show()
            pp.savefig()
            plt.close()
        pp.close()

    def makePlotLists(self, bins):
        x = list()
        y = list()
        percentGoodList = list()
        size = list()
        for (key,item) in sorted(bins.items()):
            x.append(int(key[0]))
            y.append(int(key[1]))
            (total, percentGood) = self.getStats(item)
            percentGoodList.append(percentGood)
            size.append(total)
        return x, y, percentGoodList, size

    def getStats(self,item):
        good = float(0)
        bad = float(0)
        for val in item:
            if val == "EDDY_MOTION_CORRECTED":
                good += 1
            elif "EXCLUDE_" in val:
                bad += 1
            elif val == "BASELINE_AVERAGED":
                pass
            else:
                print "ERROR: Processing type not known: {}".format(val)
        total = good + bad
        if total == 0:
            percentGood = 0
        else:
            percentGood = good / total
        return total, percentGood

    def getBins(self, site):
        stepSize = 5
        xPoints = range(-180, 180, stepSize)
        yPoints = range(0, 90, stepSize)
        bins = dict()
        for xval in xPoints:
            for yval in yPoints:
                bins[(xval, yval)] = self.getListFromDB("SELECT processing FROM {} WHERE "
                    "phi>={} AND phi<{} AND theta>={} AND theta<{} AND project='{}';".format(
                    self.tableName,xval,xval+stepSize,yval,yval+stepSize,site))
        return bins

    def _querySQLiteDB(self, SQLite_query):
        con = lite.connect(self.dbFileName)
        dbCur = con.cursor()
        dbCur.execute(SQLite_query)
        query_results = dbCur.fetchall()
        dbCur.close()
        return query_results

    def getListFromDB(self, SQLite_query):
        query_results = self._querySQLiteDB(SQLite_query)
        List = list()
        # the project from the database is stored in a tuple EX: (u'Project', )
        for row in query_results:
            list_item = str(row[0])
            List.append(list_item)
        return List

    def plotPerSite(self):
        """
        This function makes plots by site showing the processing method
        for each gradient in spherical coordinates: phi vs theta.
        """
        path = os.path.join("test_{0}_Plots_By_Site_DTIPrep_Output_XML.pdf".format(datetime.date.today().isoformat()))
        pp = pdfpages(path)
        site_list = self.getListFromDB("SELECT DISTINCT project FROM {} ORDER BY project;".format(self.tableName))
        for site in site_list:
            processingDict = self.getProcessingDict(site)
            self.plotPoints(processingDict)
            self.setPlotAttributes('Processing Type at Point Phi Vs. Theta '
                  '\nfor Project {0}\n'.format(site))
            pp.savefig()
            plt.close()
        pp.close()

    def plotPerSitePerYear(self):
        """
        This function makes plots by site and year showing the processing method
        for each gradient in spherical coordinates: phi vs theta.
        """
        path = os.path.join("test_{0}_Plots_By_Year_and_Site_DTIPrep_Output_XML.pdf".format(datetime.date.today().isoformat()))
        pp = pdfpages(path)
        site_list = self.getListFromDB("SELECT DISTINCT project FROM {} ORDER BY project;".format(self.tableName))
        for site in site_list:
            yearList = self.getListFromDB("SELECT DISTINCT year FROM {} WHERE project='{}' ORDER BY year;".format(self.tableName, site))
            for year in yearList:
                processingDict = self.getProcessingDict(site, year)
                self.plotPoints(processingDict)
                self.setPlotAttributes('Processing Type at Point Phi Vs. Theta '
                      '\nfor Project {0} and Year {1}\n'.format(site, year))
                pp.savefig()
                plt.close()
        pp.close()

    def plotPoints(self, processingDict):
        pointColors = {'EXCLUDE_SLICECHECK':'rs', 'EXCLUDE_INTERLACECHECK':'ys', 'EDDY_MOTION_CORRECTED':'bo',
                       'EXCLUDE_GRADIENTCHECK':'gs'}
        for key in sorted(processingDict.keys()):
            if key == 'BASELINE_AVERAGED':
                continue
            plt.plot(processingDict[key][0], processingDict[key][1], pointColors[key],label=key)
            print key, len(processingDict[key][0])
            print processingDict[key]

    def setPlotAttributes(self, title):
        plt.title(title, fontsize = 'large')
        plt.xlabel("Phi (degrees)", fontsize = 'large')
        plt.ylabel("Theta (degrees) \n", fontsize = 'large')
        plt.axis([-180, 180, 0, 90])
        plt.subplots_adjust(bottom = 0.2, top = 0.86, right = .88, left = 0.15)
        # plt.legend(fontsize = 'small', bbox_to_anchor=(0., -.27, 1., .02), loc=3,
        #       ncol=2, mode="expand", borderaxespad=0.,shadow=True)

    def getProcessingDict(self, site, year=None):
        if year == None:
            query_results = self._querySQLiteDB("SELECT processing,phi,theta FROM {} "
                                     "WHERE project='{}';".format(self.tableName,site))
        else:
            query_results = self._querySQLiteDB("SELECT processing,phi,theta FROM {} "
                                     "WHERE project='{}' and year='{}';".format(self.tableName, site, year))
        processingDict = dict()
        for row in query_results:
            processingDict = self.appendEntryProcessingDict(
                processingDict, str(row[0]),row[1],row[2])
        return processingDict

    def appendEntryProcessingDict(self, processingDict, processing, theta, phi):
        if processing in processingDict.keys():
            processingDict[processing][0].append(theta)
            processingDict[processing][1].append(phi)
        else:
            processingDict[processing] = [[theta],[phi]]
        return processingDict
