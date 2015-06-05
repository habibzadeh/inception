from .submaker import Submaker
import logging
import os
import sqlite3
from inception.common.database import Database
logger = logging.getLogger(__name__)
class DatabasesSubmaker(Submaker):
    def make(self, workDir):
        allSettings = self.getConfigValue(".")
        for name, dbData in allSettings.items():
            if name == "__make__":
                continue
            elif "__make__" in dbData and dbData["__make__"] is False:
                continue
            path = workDir + dbData["path"]
            if not "version" in dbData:
               raise ValueError("Must specify db version for %s " % name)
            logger.debug("Making %s" % dbData["path"])

            schemaPath = self.getConfigProperty(name.replace(".", "\.") + ".schema").resolveAsRelativePath()

            with open(schemaPath, 'r') as schemaFile:
                schemaData = schemaFile.read()
                db = Database(schemaData)

                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))

                if os.path.exists(path):
                    os.remove(path)

                conn = sqlite3.connect(path)

                for tableName, data in dbData["data"].items():
                    table = db.getTable(tableName)
                    assert table, "Table %s is not in supplied schema" % tableName
                    for row in data:
                        table.createRow(**row)

                conn.executescript("PRAGMA user_version = %s;" % dbData["version"])
                conn.executescript(schemaData)
                queries = db.getQueries()
                for q in queries:
                    conn.execute(q)

                conn.commit()
                conn.close()