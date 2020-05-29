import os
from bs4 import BeautifulSoup as BS
import re
from lxml import etree


def createXML(filename, id, name, date):
    root = etree.Element("BODY")
    root.set('KONKID', id)
    root.set('KONKNAME', name)
    root.set('FILEDATE', date)
    root.set('DCID', '1')
    tree = etree.ElementTree(root)
    handle = etree.tostring(tree, pretty_print=True, encoding='utf-8', xml_declaration=False)
    with open(filename, "wb") as fh:
        fh.write(handle)


def add_price(filename, id, price):
    tree = etree.ElementTree(file=filename)
    root = tree.getroot()
    item = etree.Element("ITEM")
    item.set('medid', id)
    item.set('price', price)
    root.append(item)
    etree.indent(root, space="\t")
    handle = etree.tostring(root, encoding='utf-8')
    with open(filename, "wb") as fh:
        fh.write(handle)


if __name__ == '__main__':
    createXML('assa.xml', '1', 'вфывфывыф', '3213-32')
    for i in range(10):
        add_price('assa.xml', '123123','321313')

