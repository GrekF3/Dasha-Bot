import sqlite3

pars = sqlite3.connect('parsdasha.db')
cu = pars.cursor()

# cu.execute("""CREATE TABLE dasha (pars_all integer, pars_end integer, pars_notend integer, percent integer)""")
# cu.execute("INSERT INTO dasha VALUES(10, 0, 0, 0)")
# cu.execute("INSERT INTO dasha VALUES(10, 10, 10, 10)")
# res = cu.execute("SELECT SUM(pars_all) FROM dasha")
cu.execute("ALTER TABLE dasha DROP COLUMN percent;")
pars.commit()

cu.close()
