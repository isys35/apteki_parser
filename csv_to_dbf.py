from dbfpy import dbf
import csv
import io


def add_data_in_dbf(file_name, data):
    SCHEMA = (
        ("DRUG_ID", "N", 25, 0),
        ("DRUG_NAME", "C", 120),
    )
    db = dbf.Dbf(file_name, new=True)
    db.addField(*SCHEMA)
    for drug in data:
        rec = db.newRecord()
        rec["DRUG_ID"] = int(drug[0])
        rec["DRUG_NAME"] = drug[1].encode("cp1251")
        rec.store()
    db.close()


def csv_to_dbf(csv_file, dbf_file):
    with io.open(csv_file, "r") as file:
        txt = file.read()
    rows = txt.split('\n')
    data = []
    for row in rows:
        cols = row.split(';')
        if cols[0] and cols[1]:
            data.append(cols)
    add_data_in_dbf(dbf_file, data)


if __name__ == '__main__':
    csv_to_dbf('aptekamos_data/catalog_aptekamos_dragid.csv', 'aptekamos_data/catalog_aptekamos_dragid.dbf')