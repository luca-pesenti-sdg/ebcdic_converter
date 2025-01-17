# Copybook structure
# The layout of a copybook follows the file layout of Cobol.
# This means that columns have specific uses and this also needs
# to be followed in the Copybook.
# Columns 1-6 are left empty and are where the line numbers were stored on cards.
# This area is called the Sequence number area and is ignored by the compiler.
# Next we have the indicator area which is a single column (7).
# This column is mainly used to indicate if that line is a comment.
# As seen above. However it also has a few other characters such as /, -, and D.
# They have the following effects: a comment that w will be printed, the line
# continues from the previous one, and enables that line in debugging mode.
# Area A (8-11) contains the level numbers such as 01 and 10 in our example.
# After 01 it does not matter the exact numbers used for ordering.
# However, the level numbers do need to be larger than any sections below.
# Columns 12-72 are called Area B and that contains any other code not allowed in
# Area A. This contains the name of the field in the above example that continues
# to around column 25. Next is the definition of the datatype.
# Described in the next section.
# 73+ is the program name area. Historically the max was 80 due to punch cards.
# It is used to identify the sequence of the card.

# Summarizing:
# 1-6: Sequence number area
# 7: Indicator area
# 8-11: Level number area
# 12-72: Area B → Name of the field, datatype, etc.
# 73+: Program name area


class Copybook:
    def __init__(self, lines):
        self._lines = lines
        self.__filler_count = 0
        self.__cursor = 0
        self.__output = {}
        self.__stack = {}

    # Old function getPicSize
    def __get_pic_size(self, arg):
        if arg.find("(") > 0:
            return int(arg[arg.find("(") + 1 : arg.find(")")])
        else:
            return len(arg)

    # Old function getLenType
    def __get_len_type(self, attribute, pic):
        ret = {}
        FirstCh = attribute[pic][:1].upper()
        Picture = attribute[pic].upper()

        if "COMP-2" in attribute and FirstCh == "S":
            ret["type"] = "dp+"
        elif "COMP-2" in attribute:
            ret["type"] = "dp"
        elif "COMP-3" in attribute and FirstCh == "S":
            ret["type"] = "pd+"
        elif "COMP-3" in attribute:
            ret["type"] = "pd"
        elif "COMP" in attribute and FirstCh == "S":
            ret["type"] = "bi+"
        elif "COMP" in attribute:
            ret["type"] = "bi"
        elif FirstCh == "S":
            ret["type"] = "zd+"
        elif FirstCh == "9":
            ret["type"] = "zd"
        else:
            ret["type"] = "ch"

        PicNum = Picture.replace("V", " ").replace("S", "").replace("-", "").split()
        Lgt = self.__get_pic_size(PicNum[0])

        if len(PicNum) == 1 and FirstCh != "V":
            ret["dplaces"] = 0
        elif FirstCh != "V":
            ret["dplaces"] = self.__get_pic_size(PicNum[1])
            Lgt += ret["dplaces"]
        else:
            ret["dplaces"] = self.__get_pic_size(PicNum[0])

        ret["length"] = Lgt

        if ret["type"][:2] == "pd":
            ret["bytes"] = int(Lgt / 2) + 1
        elif ret["type"][:2] == "bi":
            if Lgt < 5:
                ret["bytes"] = 2
            elif Lgt < 10:
                ret["bytes"] = 4
            else:
                ret["bytes"] = 8
        elif ret["type"][:2] in ["dp", "dp+"]:
            ret["bytes"] = 8
        else:
            if FirstCh == "-":
                Lgt += 1
            ret["bytes"] = Lgt
        return ret

    # Old function fGetSetack
    def __get_stack(self):
        tmp = self.__output
        for k in self.__stack:
            tmp = tmp[self.__stack[k]]
        return tmp

    # Old function fRemStack
    def __remove_stack(self, stack, level):
        new_stack = {}
        for k in stack:
            if k < level:
                new_stack[k] = stack[k]
        return new_stack

    def _add2dict(self, level, group, item, statement, id):
        if item.upper() == "FILLER":
            self.__filler_count += 1
            item = item + "_" + str(self.__filler_count)
        if level <= self.__cursor:
            self.__stack = self.__remove_stack(self.__stack, level)

        stack = self.__get_stack()
        stack[item] = {}
        stack[item]["id"] = id
        stack[item]["level"] = level
        stack[item]["group"] = group

        if "OCCURS" in statement: 
            if "TIMES" in statement:
                stack[item]["occurs"] = int(statement[statement.index("TIMES") - 1])
            else:
                raise Exception("OCCURS WITHOUT TIMES?" + " ".join(statement))

        if "REDEFINES" in statement:
            stack[item]["redefines"] = statement[statement.index("REDEFINES") + 1]

        if group == True:
            self.__stack[level] = item
            self.__cursor = level
        else:
            tplen = {}
            if "PIC" in statement:
                pic = statement.index("PIC") + 1
            elif "COMP-2" in statement:
                pic = statement.index("COMP-2")
            else:
                raise Exception("PIC OR COMP-2 MISSING?" + " ".join(statement))
            tplen = self.__get_len_type(statement, pic)
            # stack[item]['pict'] = statement[3]
            stack[item]["pict"] = statement[pic]
            stack[item]["type"] = tplen["type"]
            stack[item]["length"] = tplen["length"]
            stack[item]["bytes"] = tplen["bytes"]
            stack[item]["dplaces"] = tplen["dplaces"]

    def to_dict(self):

        id = 0
        statement = ""
        for line in self._lines:
            content = line[6:72]
            if len(content.strip()) > 1:
                first_char = line[6]
                if first_char in [" ", "-"]:
                    first_word = content.split()[0]
                    if not first_word in ["SKIP1", "SKIP2", "SKIP3"]:
                        statement += content.replace("\t", " ")
                elif first_char != "*":
                    print("Unexpected character in column 7:", line)
                    quit()
        for variable in statement.split("."):
            attribute = variable.split()
            if len(attribute) > 0:
                if attribute[0] != "88" and attribute[0] != "EXEC":
                    id += 1
                    is_group = False if "PIC" in attribute or "COMP-2" in attribute else True
                    self._add2dict(
                        level=int(attribute[0]),
                        group=is_group,
                        item=attribute[1],
                        statement=attribute,
                        id=id,
                    )
        return self.__output
