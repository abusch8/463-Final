class Color():
    RED     = chr(27) + '[31m'
    GREEN   = chr(27) + '[32m'
    YELLOW  = chr(27) + '[33m'
    BLUE    = chr(27) + '[34m'
    PURPLE  = chr(27) + '[35m'
    CYAN    = chr(27) + '[36m'
    DEFAULT = chr(27) + '[39m'

    def enum(i: int) -> str:
        return {
            1: Color.RED,
            2: Color.GREEN,
            3: Color.YELLOW,
            4: Color.BLUE,
            5: Color.PURPLE,
            6: Color.CYAN,
            7: Color.DEFAULT,
        }[i]

class Style():
    RESET   = chr(27) + '[0m'
    BOLD    = chr(27) + '[1m'
    CLEAR   = chr(27) + '[2J' + chr(27) + '[H'
