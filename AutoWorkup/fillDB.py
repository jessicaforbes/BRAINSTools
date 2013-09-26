import os
import sqlite3 as lite

class FillDB():

    def __init__(self, sqlDBcommandList):
        self.dbFileName = "dtiprepxml.db"
        self.tableName = "dtiprep"
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
        dbColTypes =  'filepath TEXT, project, TEXT, session TEXT, year TEXT, gradient TEXT, xval REAL,' \
                      ' yval REAL, zval REAL, rho REAL, theta REAL, phi REAL, processing TEXT'
        if os.path.exists(self.dbFileName):
            os.remove(self.dbFileName)
        con = lite.connect(self.dbFileName)
        dbCur = con.cursor()
        dbCur.execute("CREATE TABLE {0}({1});".format(self.tableName, dbColTypes))
        dbCur.close()

    def fillDB(self):
        con = lite.connect(self.dbFileName)
        dbCur = con.cursor()
        for command in self.sqlDBcommandList:
            dbCur.execute(command)
            con.commit()
        dbCur.close()