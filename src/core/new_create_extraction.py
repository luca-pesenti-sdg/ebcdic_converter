def create_extraction(self, obj, altstack=[], partklen=0, sortklen=0):
    for key, val in obj.items():
        if type(val) is dict:
            t = 1 if "occurs" not in val else val["occurs"]

            iTimes = 0
            while iTimes < t:
                iTimes += 1

                if "redefines" not in val:
                    if val["group"] == True:
                        altstack.append(key)
                        self.create_extraction(val, altstack, partklen, sortklen)
                        altstack.remove(key)
                    else:
                        item = {}
                        item["type"] = val["type"]
                        item["bytes"] = val["bytes"]
                        item["offset"] = self._lrecl
                        item["dplaces"] = val["dplaces"]
                        item["name"] = key
                        item["part-key"] = (
                            True if (self._lrecl + val["bytes"]) <= partklen else False
                        )
                        item["sort-key"] = (
                            True
                            if (self._lrecl + val["bytes"]) <= (sortklen + partklen)
                            and (self._lrecl + val["bytes"]) > partklen
                            else False
                        )
                        self._transf.append(item)

                        self._lrecl += +val["bytes"]
                else:
                    add2alt = True
                    for x in self._altlay:
                        if x[list(x)[0]]["newname"] == key:
                            add2alt = False
                    if add2alt:
                        red = {}
                        red[val["redefines"]] = val.copy()
                        red[val["redefines"]]["newname"] = key
                        red[val["redefines"]]["stack"] = altstack.copy()
                        self._altpos += 1
                        self._altlay.insert(self._altpos, red)
