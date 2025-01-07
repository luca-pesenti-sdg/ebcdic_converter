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
    def __init__(self, file):
        self._file = file

    def _readlines(self):
        with open(self._file, "r") as f:
            lines = f.readlines()
        return lines

    def parse(self):
        """
        Parses the copybook file and returns a dictionary.

        Returns:
        - dict: The parsed copybook
        """
        copybook = {}
        stack = []
        current = copybook
        lines = self._readlines()
        for line in lines:
            content = line[6:72]
            if content[0] in ["*", "D", "/"]:
                continue
            elif content[0] == "-": # TODO: implement this
                continue
            line = line.strip()
            level = int(line[7:11])
            name = line[7:11].strip()
            if level == 1:
                copybook[name] = {}
                current = copybook[name]
                stack = [name]
            else:
                while len(stack) >= level:
                    stack.pop()
                current = copybook
                for item in stack:
                    current = current[item]
                current[name] = {}
                current = current[name]
                stack.append(name)
        return copybook


copybook = Copybook("LegacyReference/ES0MOVGP.cpy").parse()

print(copybook)
