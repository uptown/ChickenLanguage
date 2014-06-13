# -*- coding: utf-8 -*-


class ChickenException(Exception):


    def __init__(self, message):
        self.message = message


    def __str__(self):
        return self.message

def all_indices(value, qlist):
    indices = []
    idx = -1
    while True:
        try:
            idx = qlist.index(value, idx+1)
            indices.append(idx)
        except ValueError:
            break
    return indices

class ChickenInterpreter(object):

    def __init__(self, chickens):
        self._chickens = chickens
        self._memory = {}
        self._labels = {}
        self._commands = {
            u"개업": [self._do_not_thing1, 1], #메모리 할당
            u"전화번호": [self._do_not_thing1, 1], #label 정의
            u"후라이드": [self._move, 2], #move
            u"파닭": [self._add, 3], #add
            u"순살": [self._sub, 3],
            u"양념": [self._mul, 3],
            u"불닭": [self._div, 3],
            u"찜닭": [self._write, 1],
            u"무많이": [self._jmp, 1],
            u"피클많이": [self._jmpz, 2],
            u"파많이": [self._jmpn, 2],
        }
        self._keywords = [u'뭐에요', u'없는번호']
        self._start_point = None

    def _is_reserved(self, word, except_keyword=False):
        return word in self._commands or (not except_keyword and word in self._keywords)

    def _raise_error(self, reason=None):
        raise ChickenException(reason)

    def run(self):
        commands = self._chickens.split()
        lenC = len(commands)
        cursor = None
        endpoint = None
        memory_allocs = all_indices(u"개업", commands)
        for mem_alloc in memory_allocs:
            name = commands[mem_alloc + 1]
            if self._is_reserved(name) or name[0].isdigit():
                self._raise_error(u"치킨집 이름 그따구로 지으면 안돼!")
            self._memory[name] = {}

        label_allocs = all_indices(u"전화번호", commands)
        for label in label_allocs:
            if self._is_reserved(commands[label + 1], True):
                self._raise_error(u"전화번호 그따구로 지으면 안돼!")
            self._define_label(commands[label + 1], label)
            if commands[label + 1] == u"뭐에요":
                cursor = label
            if commands[label + 1] == u"없는번호":
                endpoint = label
        if not cursor:
            self._raise_error(u"치킨집 문닫음여 ㅅㄱ")

        while lenC > cursor and endpoint != cursor:
            word = commands[cursor]
            # print self._memory
            # print word, cursor
            if unicode.startswith(word, '#'):
                cursor += 1
                continue
            c_info = self._commands[word]
            command = c_info[0]
            num_operands = c_info[1]
            ret = None
            if num_operands == 0:
                ret = command()
            elif num_operands == 1:
                ret = command(commands[cursor + 1])
            elif num_operands == 2:
                ret = command(commands[cursor + 1], commands[cursor + 2])
            elif num_operands == 3:
                ret = command(commands[cursor + 1], commands[cursor + 2], commands[cursor + 3])
            if ret:
                cursor = ret
            else:
                cursor += num_operands + 1
        return

    def _do_not_thing1(self, _unused):
        pass

    def _get_op_object(self, op):
        if op.isdigit() or (op[0] == '-' and op[1:].isdigit()):
            return [0, int(op)]
        s = op.split('(')
        if len(s) == 2:
            area, index = s
            index = index[:-1]
            if area in self._memory:
                return [1, self._memory[area], index]
        elif s in self._labels:
            return [2, self._labels[s]]
        self._raise_error(u"개업은 하시고 찾으시죠?")

    def _get_value(self, oop):
        if oop[0] == 0:
            return int(oop[1])
        elif oop[0] == 1:
            val = oop[1][oop[2]]
            if isinstance(val, list):
                return self._get_value(val)
            return val
        self._raise_error(u"올바른 치킨이 아닙니다")

    def _get_label(self, oop):
        if oop[0] == 2:
            return oop[1]
        self._raise_error(u"올바른 치킨이 아닙니다")

    def _set_value(self, oop, value):
        if oop[0] == 1:
            oop[1][oop[2]] = value
            return
        self._raise_error(u"올바른 치킨이 아닙니다")

    def _move(self, op0, op1):
        oop0 = self._get_op_object(op0)
        oop1 = self._get_op_object(op1)
        self._set_value(oop1, oop0)

    def _add(self, op0, op1, op2):
        oop0 = self._get_op_object(op0)
        oop1 = self._get_op_object(op1)
        oop2 = self._get_op_object(op2)
        self._set_value(oop2, self._get_value(oop0) + self._get_value(oop1))

    def _sub(self, op0, op1, op2):
        oop0 = self._get_op_object(op0)
        oop1 = self._get_op_object(op1)
        oop2 = self._get_op_object(op2)
        self._set_value(oop2, self._get_value(oop0) - self._get_value(oop1))

    def _mul(self, op0, op1, op2):
        oop0 = self._get_op_object(op0)
        oop1 = self._get_op_object(op1)
        oop2 = self._get_op_object(op2)
        self._set_value(oop2, self._get_value(oop0) * self._get_value(oop1))

    def _div(self, op0, op1, op2):
        oop0 = self._get_op_object(op0)
        oop1 = self._get_op_object(op1)
        oop2 = self._get_op_object(op2)
        self._set_value(oop2, int((self._get_value(oop0)/float(self._get_value(oop1)))))

    def _jmp(self, op0):
        if op0 in self._labels:
            return self._labels[op0]
        return self._get_label(op0)

    def _jmpz(self, op0, op1):
        if self._get_value(self._get_op_object(op0)) == 0:
            if op1 in self._labels:
                return self._labels[op1]
            return self._get_label(op1)

    def _jmpn(self, op0, op1):
        if self._get_value(self._get_op_object(op0)) < 0:
            if op1 in self._labels:
                return self._labels[op1]
            return self._get_label(op1)

    def _write(self, op0):
        if op0[0] == "\"":
            print op0[1:-1]
            return
        print self._get_value(self._get_op_object(op0))

    def _define_label(self, label, index):
        if label in self._labels:
            self._raise_error(u"치킨법을 위반하셨습니다. 근처 1.5km 이내에 치킨집이 있어요.")
        self._labels[label] = index
"""
self._commands = {
    u"개업": [self._do_not_thing1, 1], #메모리 할당
    u"전화번호": [self._do_not_thing1, 1], #label 정의
    u"후라이드": [self._move, 2], #move
    u"파닭": [self._add, 3], #add
    u"순살": [self._sub, 3],
    u"양념": [self._mul, 3],
    u"불닭": [self._div, 3],
    u"찜닭": [self._write, 1],
    u"무많이": [self._jmp, 1],
    u"피클많이": [self._jmpz, 2],
    u"파많이": [self._jmpn, 2],
}
"""
ChickenInterpreter(u"""개업 교촌치킨 개업 무봤나촌닭 전화번호 뭐에요 찜닭 "구구단시작" 후라이드 2 교촌치킨(0) 전화번호 1577xxxx 후라이드 2 교촌치킨(1)"""
"""전화번호 1588xxxx 양념 교촌치킨(0) 교촌치킨(1) 무봤나촌닭(0) 찜닭 무봤나촌닭(0) 파닭 1 교촌치킨(1) 교촌치킨(1) 순살 교촌치킨(1) 10 무봤나촌닭(0)"""
"""파많이 무봤나촌닭(0) 1588xxxx 찜닭 "" 파닭 1 교촌치킨(0) 교촌치킨(0) 순살 교촌치킨(0) 10 무봤나촌닭(0) 파많이 무봤나촌닭(0) 1577xxxx 전화번호 없는번호
""").run()