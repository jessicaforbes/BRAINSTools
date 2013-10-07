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
        site_list = self.getListFromDB("SELECT DISTINCT project FROM {} "
                                       "ORDER BY project;".format(self.tableName))
        self.scatterPlotBySite(site_list)
        self.scatterPlotBySiteByYear(site_list)

    def scatterPlotBySite(self, site_list):
        path = os.path.join("{0}_Scatter_Plots_By_Site_DTIPrep_"
                            "Output_XML.pdf".format(datetime.date.today().isoformat()))
        pp = pdfpages(path)
        for site in site_list:
            print "Creating scatter plot for site:", site
            (bins, stepSize) = self.getBins(site)
            (x, y, percentGoodList, size) = self.makePlotLists(bins)
            self.setPlotAttributes("Percentage of Good Gradients at Point Phi vs Theta "
                                   "\n(Binned Every {} Degrees) for Project "
                                   "{}\n".format(stepSize, site))
            cmap = plt.get_cmap('RdYlGn')
            sc = plt.scatter(x, y, s=size, c=percentGoodList,
                             cmap=cmap, edgecolors='none', vmin=0.5)
            plt.colorbar(sc)
            pp.savefig()
            plt.close()
        pp.close()
        print "\nScatter plots by site saved in file: \n{}\n".format(path)

    def scatterPlotBySiteByYear(self, site_list):
        path = os.path.join("{0}_Scatter_Plots_By_Site_By_Year_DTIPrep_"
                            "Output_XML.pdf".format(datetime.date.today().isoformat()))
        pp = pdfpages(path)
        for site in site_list:
            year_list = self.getListFromDB("SELECT DISTINCT year FROM {} WHERE project='{}' "
                                           "ORDER BY year;".format(self.tableName, site))
            for year in year_list:
                print "Creating scatter plot for Site {} and Year {}".format(site, year)
                (bins, stepSize) = self.getBins(site, year)
                (x, y, percentGoodList, size) = self.makePlotLists(bins)
                self.setPlotAttributes("Percentage of Good Gradients at Point Phi vs Theta "
                                       "\n(Binned Every {} Degrees) for Project {} "
                                       "in Year {}\n".format(stepSize, site, year))
                cmap = plt.get_cmap('RdYlGn')
                sc = plt.scatter(x, y, s=size, c=percentGoodList,
                                 cmap=cmap, edgecolors='none', vmin=0.5)
                plt.colorbar(sc)
                pp.savefig()
                plt.close()
        pp.close()
        print "\nScatter plots by site and year saved in file: \n{}".format(path)

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

    def getBins(self, site, year=None):
        stepSize = 5
        xPoints = range(-180, 180, stepSize)
        yPoints = range(0, 90, stepSize)
        bins = dict()
        for xval in xPoints:
            for yval in yPoints:
                if year == None:
                    bins[(xval, yval)] = self.getListFromDB("SELECT processing FROM {} WHERE "
                    "phi>={} AND phi<{} AND theta>={} AND theta<{} AND project='{}';".format(
                    self.tableName, xval, xval+stepSize, yval, yval+stepSize, site))
                else:
                    bins[(xval, yval)] = self.getListFromDB("SELECT processing FROM {} WHERE "
                    "phi>={} AND phi<{} AND theta>={} AND theta<{} AND project='{}' "
                    "AND year='{}';".format(self.tableName, xval, xval+stepSize, yval,
                                            yval+stepSize, site, year))
        return bins, stepSize

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

    def setPlotAttributes(self, title):
        plt.title(title, fontsize = 'large')
        plt.xlabel("\nPhi (degrees)", fontsize = 'large')
        plt.ylabel("Theta (degrees) \n", fontsize = 'large')
        plt.axis([-180, 180, 0, 90])
        plt.subplots_adjust(bottom = 0.2, top = 0.86,
                            right = .88, left = 0.15)
