#!/usr/bin/env python3
"""
Convert FLUENT .scm database (fluids and solids) to .json for usage as database for pythonFluent
"""

import sys
import json
import re

import pandas as pd

PROPDB = 'propdb.scm'  # Original FLUENT scheme database file


def cleanDB(Lines):
    for i, line in enumerate(Lines):
        if line[2:9] == "acetone":
            rawDB = Lines[i:]
            break
    return rawDB


def deleteBracket(line: object) -> object:
    """Delete Scheme programming language bracket string from opening bracket to first position"""
    bracketPosition = line.index('(')
    line = line[bracketPosition + 1:]
    name = ''.join(line)
    return name


def checkNewMaterial(line):
    if "(" in line and not ")" in line and not line.isspace():
        return True
    else:
        return False
    #try:
        #if ("fluid" or "solid" or "combusting-particle" or "inert-particle" or "droplet-particle") in rawDB[i + 1]:
    #        return True
    #    else:
    #      return False
    #except IndexError:
    #    return False


def main():
    """
    Read in FLUENT scheme file and convert it to a JSON string and export to propdb.json
    """

    with open(PROPDB, "r") as propFile:
        Lines = propFile.readlines()

    rawDB = cleanDB(Lines)  # Clean lines before raw database lines start

    jsonString = "{\n"  # Initialize empty JSON string

    # Initialize material parameters
    newMaterial, materialType, chemicalFormula, newProperty = True, False, False, False

    # Loop over raw database lines
    for i, line in enumerate(rawDB):
        newMaterial = checkNewMaterial(line)  # Check if new material is found

        # If new material is encountered in database
        if newMaterial and not line.isspace():
            name = deleteBracket(line)
            name = name.replace("\n", "")
            jsonString += f"\t\"{name}\" : {{\n"
            newMaterial, materialType = False, True
            continue

        # Type of material
        MaterialTypes = ["fluid", "solid", "combusting-particle", "inert-particle", "droplet-particle", "mixture"]
        if materialType:
            containedTypes = []
            for material in MaterialTypes:
                if material in line:
                    containedTypes.append("\"{}\"".format(material))
            string = ', '.join(containedTypes)
            jsonString += "\t\t\"type\" : [{}],\n".format(string)
            materialType, chemicalFormula = False, True

        # Chemical Formula
        if "chemical-formula" in line and chemicalFormula is True:
            line = line.replace("\n", "")
            pos = line.find(".")
            formula = line[pos+2:-1]  # String from two positions after the point until last before parentheses
            jsonString += "\t\t\"chemicalFormula\" : \"{}\",\n".format(formula)
            chemicalFormula, newProperty = False, True

        if newProperty:

            # Density
            if "density" in line:
                if "constant" in line:
                    start = line.find("constant")
                    end = start + len("constant")
                    densityString = line[end + 3:]
                    constantEnd = densityString.find("(")
                    cdString = densityString[:constantEnd]
                    cdString = cdString.replace(")", "")
                    if ";" in cdString:
                        pos = cdString.find(";")
                        cdFloat = float(cdString[:pos])
                    else:
                        cdFloat = float(cdString)
                if "compressible-liquid" in line:
                    start = line.find("compressible-liquid")
                    end = start + len("compressible-liquid")
                    densityString = line[end + 3:]
                    clList = list(densityString.split(" "))
                    clList = clList[1:]
                    clFloats = []
                    for i, s in enumerate(clList):
                        clList[i] = clList[i].replace(")", "")
                        clList[i] = clList[i].replace("\n", "")
                        if ";" in clList[i]:
                            pos = clList[i].find(";")
                            clList[i] = clList[i][:pos]
                        try:
                            clFloats.append(float(clList[i]))
                        except ValueError:
                            pass
                if cdFloat:
                    jsonString += "\t\t\"density\" : {{\n\t\t\t\"constant\" : {}".format(cdFloat)
                    cdFloat = None
                if clFloats:
                    jsonString += ",\n\t\t\t\"compressible-liquid\" : {}\n\t\t}},\n".format(clFloats)
                    clFloats = None
                else:
                    jsonString += "\n\t\t}},\n".format(clFloats)

            # Specific heat cp
            if "specific-heat" in line:
                jsonString += "\t\t\"specific-heat\" : {\n\t\t\t"
                if "constant" in line:
                    start = line.find("constant")
                    end = start + len("constant")
                    cpString = line[end + 3:]
                    constantEnd = cpString.find("(")
                    ccpString = cpString[:constantEnd]
                    ccpString = ccpString.replace(")", "")
                    if ";" in ccpString:
                        pos = ccpString.find(";")
                        cdFloat = float(ccpString[:pos])
                    else:
                        cdFloat = float(ccpString)
                    jsonString += "\"constant\" : {}".format(ccpString)
                if "piecewise-polynomial" in line:
                    start = line.find("piecewise-polynomial")
                    end = start + len("piecewise-polynomial")
                    ppString = line[end + 1:]
                    ppList = list(ppString.split(" "))
                    ranges, nRange, Coeffs = {}, 0, []
                    ppList = [x for x in ppList if x]  # Remove empty list elements
                    b = []
                    for i, j in enumerate(ppList):  # Clean list for retarded inconsistency
                        if ")(" in j:
                            temp = j.split(")(")
                            b.append(temp[0] + ")")
                            b.append("(" + temp[1])
                        else:
                            b.append(j)

                    if b[0] == "(":
                        if b[1][0] == "(":
                            del b[0]
                        else:
                            b[1] = "(" + b[1]
                            del b[0]

                    for i, s in enumerate(b):
                        if ("constant" or "piecewise-linear") in s:
                            break
                        if s[0] == "(" and "constant" not in s:
                            t1 = s[1:]
                            t2 = b[i + 1]
                            ranges[nRange] = {"range": [float(t1), float(t2)]}
                            continue
                        if not s[-1] == (")" or "(") and i > 1:
                            tempList = list(s)
                            newList = []
                            for i, j in enumerate(tempList):
                                try:
                                    float(j)
                                    newList.append(j)
                                except:
                                    if j == ("E" or "e" or "-" or "."):
                                        newList.append(j)
                                    else:
                                        pass
                            s = ''.join(newList)
                            Coeffs.append(float(s))
                        elif s[-1] == ")" and i > 1:
                            #last = float(re.sub("[^0-9]", "", s))
                            if s[-2] == ")":
                                last = float(s[:-2])
                            else:
                                last = float(s[:-1])
                            Coeffs.append(last)
                            ranges[nRange]['coeffs'] = Coeffs
                            Coeffs = []
                            nRange += 1

                    try:
                        float(jsonString[-1])
                        jsonString += ",\n\t\t\t\"piecewise-polynomial\" : "
                        jsonString += "{\n\t\t\t\t"
                        for key, value in ranges.items():
                            lCoeffs = value['coeffs']
                            nCoeffs = len(value['coeffs'])
                            jsonString += "\"range{}\" : [{}, {}]".format(key, value['range'][0], value['range'][1])
                            jsonString += "\"coeffs{}\" : [{}, {}]".format(key, value['coeffs'][0], value['range'][1])
                            for coeff in lCoeffs:
                                jsonString += "\"coeffs{}\" : [{}, {}]".format(key, value['coeffs'][0], value['range'][1])
                    except ValueError:
                        pass
                        #jsonString += "\"piecewise-polynomial\" : "
                        #print("hello")
                        #for key, value in ranges.items():

        newMaterial = True

    with open("test.json", "w") as f:
        f.write(jsonString)


if __name__ == "__main__":
    main()
