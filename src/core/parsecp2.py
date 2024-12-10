import json
from core.copybook2 import Copybook


class EBCDICParser:
    def _init_(self):
        self._transf = []
        self._altlay = []
        self._lrecl = 0
        self._altpos = 0
        self._partklen = 0
        self._sortklen = 0

    @property
    def _transf(self):
        return self._transf

    @_transf.setter
    def _transf(self, value):
        self._transf = value

    @property
    def _altlay(self):
        return self._transf

    @_altlay.setter
    def _altlay(self, value):
        self._altlay = value

    @property
    def _lrecl(self):
        return self._transf

    @_lrecl.setter
    def _lrecl(self, value):
        self._lrecl = value

    @property
    def _altpos(self):
        return self._transf

    @_altpos.setter
    def _altpos(self, value):
        self._altpos = value

    @property
    def _partklen(self):
        return self._transf

    @_partklen.setter
    def _partklen(self, value):
        self._partklen = value

    @property
    def _sortklen(self):
        return self._transf

    @_sortklen.setter
    def _sortklen(self, value):
        self._sortklen = value

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
                                True
                                if (self._lrecl + val["bytes"]) <= partklen
                                else False
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

    def run_parse(self, log, iparm):
        self._transf = []
        self._lrecl = 0

        # Open the copybook for reading and creates the dictionary
        with open(iparm.copybook, "r") as finp:
            output = Copybook(finp.readlines()).to_dict()

        # Write the dict into a file if requested
        if iparm.json_debug != "":
            with open(iparm.json_debug, "w") as fout:
                fout.write(json.dumps(output, indent=4))

        # get the default values
        param = vars(iparm)

        self._partklen = iparm.part_k_len
        self._sortklen = iparm.sort_k_len

        self.create_extraction(output, [], self._partklen, self._sortklen)

        param["input_recl"] = self._lrecl
        param["transf_rule"] = []
        param["transf"] = self._transf

        ialt = 0
        for r in self._altlay:
            self._transf = []
            self._lrecl = 0
            redfkey = list(r.keys())[0]

            # POSITIONS ON REDEFINES
            newout = output
            for s in r[redfkey]["stack"]:
                newout = newout[s]

            newout[redfkey] = r[redfkey].copy()
            newout[redfkey].pop("redefines")

            # self._altpos = ialt # seems useless
            self.create_extraction(output, [], self._partklen, self._sortklen)
            ialt += 1
            param["transf" + str(ialt)] = self._transf

        with open(iparm.json, "w") as fout:
            fout.write(json.dumps(param, indent=4))
