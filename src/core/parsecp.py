import json
from core.copybook import Copybook


class EBCDICParser:
    def __init__(self):
        self._transf = []
        self._altlay = []
        self._record_length = 0 #NOTE: I'm not sure if it's correct
        self._altpos = 0
        self._partklen = 0
        self._sortklen = 0


    def create_extraction(self, obj, altstack=[], partklen=0, sortklen=0):
        for k in obj:
            if type(obj[k]) is dict:
                t = 1 if "occurs" not in obj[k] else obj[k]["occurs"]

                iTimes = 0
                while iTimes < t:
                    iTimes += 1

                    if "redefines" not in obj[k]:
                        if obj[k]["group"] == True:
                            altstack.append(k)
                            self.create_extraction(obj[k], altstack, partklen, sortklen)
                            altstack.remove(k)
                        else:
                            item = {}
                            item["type"] = obj[k]["type"]
                            item["bytes"] = obj[k]["bytes"]
                            item["offset"] = self._record_length
                            item["dplaces"] = obj[k]["dplaces"]
                            item["name"] = k
                            item["part-key"] = (
                                True
                                if (self._record_length + obj[k]["bytes"]) <= partklen
                                else False
                            )
                            item["sort-key"] = (
                                True
                                if (self._record_length + obj[k]["bytes"])
                                <= (sortklen + partklen)
                                and (self._record_length + obj[k]["bytes"]) > partklen
                                else False
                            )
                            self._transf.append(item)

                            self._record_length = self._record_length + obj[k]["bytes"]
                    else:
                        add2alt = True
                        for x in self._altlay:
                            if x[list(x)[0]]["newname"] == k:
                                add2alt = False
                        if add2alt:
                            red = {}
                            red[obj[k]["redefines"]] = obj[k].copy()
                            red[obj[k]["redefines"]]["newname"] = k
                            red[obj[k]["redefines"]]["stack"] = altstack.copy()
                            self._altpos += 1
                            self._altlay.insert(self._altpos, red)

    def run_parse(self, log, iparm):
        self._transf = []
        self._record_length = 0

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

        param["input_recl"] = self._record_length
        param["transf_rule"] = []
        param["transf"] = self._transf

        ialt = 0
        for r in self._altlay:
            self._transf = []
            self._record_length = 0
            redfkey = list(r.keys())[0]

            # POSITIONS ON REDEFINES
            newout = output
            for s in r[redfkey]["stack"]:
                newout = newout[s]

            newout[redfkey] = r[redfkey].copy()
            newout[redfkey].pop("redefines")

            self._altpos = ialt # seems useless
            self.create_extraction(output, [], self._partklen, self._sortklen)
            ialt += 1
            param["transf" + str(ialt)] = self._transf
            
        with open(iparm.json, "w") as fout:
            fout.write(json.dumps(param, indent=4))
        return param
