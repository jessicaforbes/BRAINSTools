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
        self.plotPerSite()

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
            list_item = row[0]
            List.append(list_item)
        return List

    def plotPerSite(self):
        """
        This function makes plots by site showing the processing method
        for each gradient in spherical coordinates: phi vs theta.
        """
        path = os.path.join("{0}_Plots_By_Site_DTIPrep_Output_XML.pdf".format(datetime.date.today().isoformat()))
        pp = pdfpages(path)
        site_list = self.getListFromDB("SELECT DISTINCT project FROM {};".format(self.tableName))
        print site_list
        pointColors = {'EXCLUDE_SLICECHECK':'rs', 'EXCLUDE_INTERLACECHECK':'ys', 'EDDY_MOTION_CORRECTED':'bo',
                       'EXCLUDE_GRADIENTCHECK':'gs', 4:'c', 5:'m', 6:'k'}
        for site in site_list:
            processingDict = self.getProcessingDict(site)
            print processingDict
            for key in sorted(processingDict.keys()):
                if key == 'BASELINE_AVERAGED':
                    continue
                plt.plot(processingDict[key][0], processingDict[key][1], pointColors[key],label=key)
                print key, len(processingDict[key][0])
                print processingDict[key]
            plt.title('Processing Type at Point Phi Vs. Theta '
                      '\nfor Project {0}\n'.format(site), fontsize = 'large')
            plt.xlabel("Phi (degrees)", fontsize = 'large')
            plt.ylabel("Theta (degrees) \n", fontsize = 'large')
            plt.axis([-180, 180, 0, 90])
            plt.subplots_adjust(bottom = 0.2, top = 0.86, right = .88, left = 0.15)
            plt.legend(fontsize = 'small', bbox_to_anchor=(0., -.27, 1., .02), loc=3,
                  ncol=2, mode="expand", borderaxespad=0.,shadow=True)
            pp.savefig()
            plt.close()
        pp.close()

    def getProcessingDict(self, site):
        query_results = self._querySQLiteDB("SELECT processing,phi,theta FROM {} "
                                     "WHERE project='{}';".format(self.tableName,site))
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
