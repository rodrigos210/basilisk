'''
Copyright (c) 2016, Autonomous Vehicle Systems Lab, Univeristy of Colorado at Boulder

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

'''
from xml.etree import ElementTree
import numpy as np


class RadiationPressureLookupParser():
    def __init__(self):
        self.sHatBLookup = np.zeros([1, 3])
        self.forceBLookup = np.zeros([1, 3])
        self.torqueBLookup = np.zeros([1, 3])

    def parseXML(self, filePath):
        document = ElementTree.parse(filePath)

        sHatBTree = document.find('sHatBValues')
        forceBTree = document.find('forceBValues')
        torqueBTree = document.find('torqueBValues')
        handler = SRPLookupTableHandler(len(sHatBTree.getchildren()))

        for node in sHatBTree.getchildren():
            idx = node.attrib['index']
            for value in node.getchildren():
                if value.tag == 'value_1':
                    handler.sHatBLookup[idx, 0] = value.text
                if value.tag == 'value_2':
                    handler.sHatBLookup[idx, 1] = value.text
                if value.tag == 'value_3':
                    handler.sHatBLookup[idx, 2] = value.text

        for node in forceBTree.getchildren():
            idx = node.attrib['index']
            for value in node.getchildren():
                if value.tag == 'value_1':
                    handler.forceBLookup[idx, 0] = value.text
                if value.tag == 'value_2':
                    handler.forceBLookup[idx, 1] = value.text
                if value.tag == 'value_3':
                    handler.forceBLookup[idx, 2] = value.text

        for node in torqueBTree.getchildren():
            idx = node.attrib['index']
            for value in node.getchildren():
                if value.tag == 'value_1':
                    handler.torqueBLookup[idx, 0] = value.text
                if value.tag == 'value_2':
                    handler.torqueBLookup[idx, 1] = value.text
                if value.tag == 'value_3':
                    handler.torqueBLookup[idx, 2] = value.text
