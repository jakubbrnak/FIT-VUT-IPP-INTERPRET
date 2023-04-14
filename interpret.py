
import re
import argparse
import sys
import xml.etree.ElementTree as ET
import itertools as it


#Tento skript bude pracovat s těmito parametry:
# --help viz společný parametr všech skriptů v sekci 2.2;
# --source=file vstupní soubor s XML reprezentací zdrojového kódu dle definice ze sekce 3.1
# doplnění v úvodu sekce 4;
# --input=file soubor se vstupy12 pro samotnou interpretaci zadaného zdrojového kódu.
#Slespoň jeden z parametrů (--source nebo --input) musí být vždy zadán. Pokud jeden z nich
#chybí, jsou chybějící data načítána ze standardního vstupu.

#write code using argparse


class Argument_parser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("--source", nargs = 1, help="input file with XML representation of source code")
        self.parser.add_argument("--input", nargs = 1, help="input file with inputs for interpretation of source code")
        self.args = self.parser.parse_args()
        self.check_args()


    def check_args(self):
        if self.args.source is None and self.args.input is None:
            exit(10)
       
        if self.args.source is not None:
            try:
                self.source = open(self.args.source[0], "r")
                self.source.close()
                self.source = self.args.source[0]
            except IOError:
                exit(11)
        else:        
            self.source = None

        if self.args.input is not None:
            try:
                self.input = open(self.args.input[0], "r")
                self.input.close()
                self.input = self.args.input[0]
            except IOError:
                exit(11)
        else:  
            self.input = None 
    
    def get_source(self):
        return self.source
  
    def get_input(self):
        return self.input

    def get_args(self):
        return self.args
    
class Argument:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    
class Instruction:
    instruction_list = []
    
    def __init__(self, opcode, order, arg1, arg2, arg3):
        self.opcode = opcode
        self.order = order
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
    
    def append_instruction(self):
        self.instruction_list.append(self)
        
    

class Interpret:
    def __init__(self):
        self.arg_parser = Argument_parser()
        self.source = self.arg_parser.get_source()
        self.input = self.arg_parser.get_input()
        self.instruction_list = []
    
    #def load_xml(self):
    #    try:
    #        self.tree = ET.parse(self.source)
    #    except ET.ParseError:
    #        exit(31)
#
    #    self.root = self.tree.getroot()


    def parse_xml(self):
        if self.source is not None:
            self.tree = ET.parse(self.source)
            self.root = self.tree.getroot()
        else:
            self.tree = ET.parse(sys.stdin)
            self.root = self.tree.getroot()
    
    def check_xml(self):
        if self.root.tag != "program":
            exit(32)

        if self.root.attrib.get("language") != "IPPcode23":
            exit(32)
        
        
        
        for instruction in self.root:
            if instruction.tag != "instruction":
                exit(32)
            
            if instruction.attrib.get("order") is None:
                exit(32)

            #write a condition to check if order is not less than 1
            if int(instruction.attrib.get("order")) < 1:
                exit(32)        
            
            if instruction.attrib.get("opcode") is None:
                exit(32)
            
            if instruction.attrib.get("opcode") not in ["MOVE", "CREATEFRAME", "PUSHFRAME", "POPFRAME", "DEFVAR", "CALL", "RETURN", "PUSHS", "POPS", "ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR", "NOT", "INT2CHAR", "STRI2INT", "READ", "WRITE", "CONCAT", "STRLEN", "GETCHAR", "SETCHAR", "TYPE", "LABEL", "JUMP", "JUMPIFEQ", "JUMPIFNEQ", "EXIT", "DPRINT", "BREAK"]:
                exit(32)
            
            for argument in instruction:
                
                if argument.tag != "arg1" and argument.tag != "arg2" and argument.tag != "arg3": 
                    exit(32)
                
                if argument.attrib.get("type") is None:
                    exit(32)
                
                if argument.attrib.get("type") not in ["var", "symb", "label", "type", "nil", "int", "bool", "string"]:
                    exit(32)
                
                if argument.attrib.get("type") == "var":
                    if re.match(r"^(GF|LF|TF)@[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$", argument.text) is None:
                        exit(32)
               
                if argument.attrib.get("type") == "label":
                    if re.match(r"^[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$", argument.text) is None:
                        exit(32)
                
                if argument.attrib.get("type") == "type":
                    if argument.text not in ["int", "bool", "string"]:
                        exit(32)
                
                if argument.attrib.get("type") == "int":
                    if re.match(r"^[-+]?[0-9]+$", argument.text) is None:
                        exit(32)
                
                if argument.attrib.get("type") == "bool":
                    if argument.text not in ["true", "false"]:
                       exit(32)
                
            #    if argument.attrib.get("type") == "string":
            #        if re.match(r"(?!\\[0-9]{3})[\s\\#]", argument.text) is None:
            #            print(argument.text)
            #            print("BBBBBBBBBBBBBBBBBBBBB")
            #            exit(32)
            #    
                if argument.attrib.get("type") == "nil":
                    if argument.text != "nil":
                        exit(32)
                
                if argument.attrib.get("type") == "symb":
                    if re.match(r"^(GF|LF|TF)@[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$", argument.text) is None and re.match(r"^([^\#\\\s]|(\\\\[0-9]{3}))*$", argument.text) is None and re.match(r"^[-+]?[0-9]+$", argument.text) is None and argument.text not in ["true", "false", "nil"]:
                        exit(32)

    def load_instructions(self):
        for instruction in self.root:
            self.i = Instruction(instruction.attrib.get("opcode"), instruction.attrib.get("order"), None, None, None)
            for argument in instruction:
                if argument.tag == "arg1":
                    self.i.arg1 = Argument(argument.attrib.get("type"), argument.text)
                if argument.tag == "arg2":
                    self.i.arg2 = Argument(argument.attrib.get("type"), argument.text)
                if argument.tag == "arg3":
                    self.i.arg3 = Argument(argument.attrib.get("type"), argument.text)
            
            self.i.append_instruction()
    
    def main(self):
        

        #self.load_xml()
        
        self.parse_xml()
       
        
        self.check_xml() 
        
    
        self.load_instructions()
       
        execute = Execute(self.i.instruction_list)
        
        execute.execute()
class Variable:
    def __init__(self, name, value):
        self.name = name
        self.value = value     

class Execute:
    def __init__(self, instruction_list):
        self.instruction_list = instruction_list
        self.data_stack = []
        self.call_stack = []
        self.frame_stack = []
        self.temporary_frame = None
        self.global_frame = {}
        self.instruction_counter = int(0)
        self.labels = {}

    def load_labels(self):
        for instruction in self.instruction_list:
            if instruction.opcode == "LABEL":
                if instruction.arg1.value in self.labels:
                    exit(52)
                self.labels[instruction.arg1.value] = int(instruction.order)

    def execute(self):

        self.load_labels()
        while self.instruction_counter < len(self.instruction_list):
            
            if self.instruction_list[self.instruction_counter].opcode == "MOVE":
                self.move(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "CREATEFRAME":
                self.createframe()
            
            elif self.instruction_list[self.instruction_counter].opcode == "PUSHFRAME":
                self.pushframe()
            
            elif self.instruction_list[self.instruction_counter].opcode == "POPFRAME":
                self.popframe()
            
            elif self.instruction_list[self.instruction_counter].opcode == "DEFVAR":
                self.defvar(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "CALL":
                self.call(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "RETURN":
                self.return_()
            
            elif self.instruction_list[self.instruction_counter].opcode == "PUSHS":
                self.pushs(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "POPS":
                self.pops(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "ADD":
                self.add(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "SUB":
                self.sub(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "MUL":
                self.mul(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "IDIV":
                self.idiv(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "LT":
                self.lt(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "GT":
                self.gt(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "EQ":
                self.eq(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "AND":
                self.and_(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "OR":
                self.or_(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "NOT":
                self.not_(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "INT2CHAR":
                self.int2char(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "STRI2INT":
                self.stri2int(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "READ":
                self.read(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "WRITE":
                self.write(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "CONCAT":
                self.concat(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "STRLEN":
                self.strlen(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "GETCHAR":
                self.getchar(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "SETCHAR":
                self.setchar(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "TYPE":
                self.type_(self.instruction_list[self.instruction_counter])
            
            #elif self.instruction_list[self.instruction_counter].opcode == "LABEL":
            #    self.label(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "JUMP":
                self.jump(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "JUMPIFEQ":
                self.jumpifeq(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "JUMPIFNEQ":
                self.jumpifneq(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "EXIT":
                self.exit(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "DPRINT":
                self.dprint(self.instruction_list[self.instruction_counter])
            
            elif self.instruction_list[self.instruction_counter].opcode == "BREAK":
                self.break_(self.instruction_list[self.instruction_counter])
            
            self.instruction_counter += 1

        sys.exit(0)

    def get_frame(self, arg):
        var_name = arg.value
        frame_name, variable_name = var_name.split('@', maxsplit=1)
        return frame_name, variable_name

    def get_type(self, arg):
        if arg.type == "var":
            frame_name, variable_name = self.get_frame(arg)
            if frame_name == "GF":
                return self.global_frame[variable_name]['type']
            elif frame_name == "LF":
                return self.frame_stack[-1][variable_name]['type']
            elif frame_name == "TF":
                return self.temporary_frame[variable_name]['type']
        else:
            return arg.type

    def symb_check(self, arg, type, var_type):
        
        if arg.type not in type:
            exit(53)
        
        if arg.type == "var":
            frame_name, variable_name = self.get_frame(arg)
            
            if frame_name == 'GF':
                if variable_name not in self.global_frame:
                    exit(54)

                if var_type and self.global_frame[variable_name]['type'] != None and self.global_frame[variable_name]['type'] not in var_type:
                    #print("AAAAAAAAAAAA")
                    exit(53)
                value = self.global_frame[variable_name]['value']
            
            elif frame_name == 'LF':
                if len(self.frame_stack) == 0:
                    exit(55)
                
                if self.frame_stack[-1] is None:
                    exit(55)
                
                if variable_name not in self.frame_stack[-1]:
                    exit(54)
               
                if var_type and self.frame_stack[-1][variable_name]['type'] != None and self.frame_stack[-1][variable_name]['type'] not in var_type:
                    exit(53)
                value = self.frame_stack[-1][variable_name]['value']
            
            elif frame_name == 'TF':
                if self.temporary_frame is None:
                    exit(55)
                
                if variable_name not in self.temporary_frame:
                    exit(54)

                if var_type and self.temporary_frame[variable_name]['type'] != None and self.temporary_frame[variable_name]['type'] not in var_type:
                    exit(53)    
                
                value = self.temporary_frame[variable_name]['value']
         
            return value
        
        elif arg.type in ("int", "bool", "string", "nil", "type", "label"):
            
            if arg.type == "string" and arg.value is None:
                return ""
            else:
                return arg.value
       
        #elif arg.type == "nil":
        #    return None
        
        else:
            exit(32)
    
    def string_replace(self, toreplace):
        toreplace = toreplace.replace("\\032", " ")
        toreplace = toreplace.replace("\\092", "\\")
        toreplace = toreplace.replace("\\010", "\n")
        toreplace = toreplace.replace("\\035", "#")
        return toreplace
    
    def assign(self, arg, to_assign, type_):
        frame_name, variable_name = self.get_frame(arg)
        if frame_name == 'GF':
            self.global_frame[variable_name]= {'value': to_assign, 'type': type_}
        elif frame_name == 'LF':
            if len(self.frame_stack) == 0:
                exit(55)
            self.frame_stack[-1][variable_name] = {'value': to_assign, 'type': type_}
        elif frame_name == 'TF':
            if self.temporary_frame is None:
                exit(55)
            self.temporary_frame[variable_name] = {'value': to_assign, 'type': type_}
        else:
            exit(32)

    def move(self, inst):
        arg1 = self.symb_check(inst.arg1, 'var', None)
        arg2 = self.symb_check(inst.arg2, {'int', 'bool', 'string', 'var', 'nil'}, None)

        if arg2 is None:
            exit(56)

        if inst.arg2.type == 'string':
            arg2 = self.string_replace(arg2)
            if inst.arg2.value is None:
                inst.arg2.value = ""

        self.assign(inst.arg1, arg2, inst.arg2.type)


    #    frame_name, variable_name = self.get_frame(inst.arg1)
    #    if frame_name == 'GF':
    #        self.global_frame[variable_name]['value'] = inst.arg2.value
    #        self.global_frame[variable_name]['type'] = inst.arg2.type
    #    elif frame_name == 'LF':
    #        self.frame_stack[-1][variable_name]['value'] = inst.arg2.value
    #        self.frame_stack[-1][variable_name]['type'] = inst.arg2.type
    #    elif frame_name == 'TF':
    #        self.temporary_frame[variable_name]['value'] = inst.arg2.value
    #        self.temporary_frame[variable_name]['type'] = inst.arg2.type
    #    else:
    #        exit(32)

    def createframe(self):
        self.temporary_frame = {}

    def pushframe(self):
        if self.temporary_frame == None:
            exit(55)
        else:
            self.frame_stack.append(self.temporary_frame)
            self.temporary_frame = None


    def popframe(self):
        if len(self.frame_stack) == 0:
            exit(55)
        else:
            self.temporary_frame = self.frame_stack.pop()

    def defvar(self, inst):
        frame_name, variable_name = self.get_frame(inst.arg1)
       
        if frame_name == 'GF':
            self.global_frame[variable_name] = {'value': None, 'type': None}
       
        elif frame_name == 'LF':
            if len(self.frame_stack) == 0:
                exit(55)  # no frame to define variable in
            self.frame_stack[-1][variable_name] = {'value': None, 'type': None}
       
        elif frame_name == 'TF':
            if self.temporary_frame is None:

                exit(55)  # no frame to define variable in

            self.temporary_frame[variable_name] = {'value': None, 'type': None}
        else:
            exit(32)

            

    def call(self, inst):
        if inst.arg1.type != "label":
            exit(32)
        
        if inst.arg1.value in self.labels:
            self.call_stack.append(self.instruction_counter)
            self.instruction_counter = self.labels[inst.arg1.value] - 1
        else:
            exit(52)

    
    def return_(self):
        if len(self.call_stack) == 0:
            exit(56)
        else:
            self.instruction_counter = self.call_stack.pop()

    def pushs(self, inst):
        arg1 = self.symb_check(inst.arg1, {'int', 'bool', 'string', 'var', 'nil'}, None)

        if arg1 is None:
            exit(56)
        
        self.data_stack.append(arg1)

    def pops(self, inst):
        
        if len(self.data_stack) == 0:
            exit(56)
        arg1 = self.symb_check(inst.arg1, {'var'}, None)
        
        to_assign = self.data_stack.pop()
        self.assign(inst.arg1, to_assign, type(to_assign))
    #    frame_name, variable_name = self.get_frame(inst.arg1)
    #    if frame_name == 'GF':
    #        self.global_frame[variable_name]['value'] = self.data_stack.pop()
    #        self.global_frame[variable_name]['type'] = type(self.global_frame[variable_name]['value'])

    def add(self, inst):
        
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value= self.symb_check(inst.arg2, {'int', 'var'}, {'int'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var'}, {'int'})

        if arg2_value is None or arg3_value is None:
            exit(56)
        
        


        self.assign(inst.arg1, int(arg2_value) + int(arg3_value), 'int')

    #    frame_name, variable_name = self.get_frame(inst.arg1)
    #    
    #    if frame_name == 'GF':
    #        self.global_frame[variable_name] = {'value': int(arg2_value) + int(arg3_value), 'type': 'int'}
    #    elif frame_name == 'LF':
    #        if not self.frame_stack[-1]:
    #            exit(55)  # no frame to define variable in
    #        self.frame_stack[-1][variable_name] = {'value': int(arg2_value) + int(arg3_value), 'type': 'int'}
    #    elif frame_name == 'TF':
    #        if not self.temporary_frame:
    #            exit(55)  # no frame to define variable in
    #        self.temporary_frame[variable_name] = {'value': int(arg2_value) + int(arg3_value), 'type': 'int'}
    #    else:
    #        exit(32)

    
    
    def sub(self, inst):
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value= self.symb_check(inst.arg2, {'int', 'var'}, {'int'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var'}, {'int'})

        if arg2_value is None or arg3_value is None:
            exit(56)


        self.assign(inst.arg1, int(arg2_value) - int(arg3_value), 'int')
        
        ##frame_name, variable_name = self.get_frame(inst.arg1)
        ##
        ##if frame_name == 'GF':
        ##    self.global_frame[variable_name] = {'value': int(arg2_value) - int(arg3_value), 'type': 'int'}
        ##elif frame_name == 'LF':
        ##    if not self.frame_stack[-1]:
        ##        exit(55)  # no frame to define variable in
        ##    self.frame_stack[-1][variable_name] = {'value': int(arg2_value) - int(arg3_value), 'type': 'int'}
        ##elif frame_name == 'TF':
        ##    if not self.temporary_frame:
        ##        exit(55)  # no frame to define variable in
        ##    self.temporary_frame[variable_name] = {'value': int(arg2_value) - int(arg3_value), 'type': 'int'}
        ##else:
        ##    exit(32)
    
    def mul(self, inst):
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value= self.symb_check(inst.arg2, {'int', 'var'}, {'int'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var'}, {'int'})

        if arg2_value is None or arg3_value is None:
            exit(56)
        
        self.assign(inst.arg1, int(arg2_value) * int(arg3_value), 'int')
      #  frame_name, variable_name = self.get_frame(inst.arg1)
      #  
      #  if frame_name == 'GF':
      #      self.global_frame[variable_name] = {'value': int(arg2_value) * int(arg3_value), 'type': 'int'}
      #  elif frame_name == 'LF':
      #      if not self.frame_stack[-1]:
      #          exit(55)  # no frame to define variable in
      #      self.frame_stack[-1][variable_name] = {'value': int(arg2_value) * int(arg3_value), 'type': 'int'}
      #  elif frame_name == 'TF':
      #      if not self.temporary_frame:
      #          exit(55)  # no frame to define variable in
      #      self.temporary_frame[variable_name] = {'value': int(arg2_value) * int(arg3_value), 'type': 'int'}
      #  else:
      #      exit(32)
    

    def idiv(self, inst):
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'int', 'var'}, {'int'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var'}, {'int'})

        if arg2_value is None or arg3_value is None:
            exit(56)
        
        if int(arg3_value) == 0:
            exit(57)

        self.assign(inst.arg1, int(arg2_value) // int(arg3_value), 'int')

    #    frame_name, variable_name = self.get_frame(inst.arg1)
    #    
    #    if frame_name == 'GF':
    #        self.global_frame[variable_name] = {'value': int(arg2_value) // int(arg3_value), 'type': 'int'}
    #    elif frame_name == 'LF':
    #        if not self.frame_stack[-1]:
    #            exit(55)  # no frame to define variable in
    #        self.frame_stack[-1][variable_name] = {'value': int(arg2_value) // int(arg3_value), 'type': 'int'}
    #    elif frame_name == 'TF':
    #        if not self.temporary_frame:
    #            exit(55)  # no frame to define variable in
    #        self.temporary_frame[variable_name] = {'value': int(arg2_value) // int(arg3_value), 'type': 'int'}
    #    else:
    #        exit(32)
    
    def lt(self, inst):
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'int', 'var', 'string', 'bool'}, {'int', 'string', 'bool'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var', 'string', 'bool'}, {'int', 'string', 'bool'})

        if arg2_value is None or arg3_value is None:
            exit(56)
        
        if inst.arg2.type == 'nil' or inst.arg3.type == 'nil':
            exit(56)

        if inst.arg2.type != inst.arg3.type:
            exit(53)

        if inst.arg2.type == 'bool':
            if arg2_value == 'true':
                arg2_value = 1
            else:
                arg2_value = 0

            if arg3_value == 'true':
                arg3_value = 1
            else:
                arg3_value = 0

            to_assign = arg2_value < arg3_value   

        if inst.arg2.type == 'int':
            arg2_value = int(arg2_value)
            arg3_value = int(arg3_value)
        
        if inst.arg2.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
            arg2_value = re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1), 10)), arg2_value)
        
        if inst.arg2.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
                arg3_value = re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1), 10)), arg3_value)
        
        if inst.arg2.type != 'bool':
            to_assign = arg2_value < arg3_value
             
        to_assign = str(to_assign)
        to_assign = to_assign.lower()

        self.assign(inst.arg1, to_assign, 'bool')
        
        
        
        #frame_name, variable_name = self.get_frame(inst.arg1)
        #if frame_name == 'GF':
        #    self.global_frame[variable_name] = {'value': to_assign, 'type': 'bool'}
        #elif frame_name == 'LF':
        #    if self.frame_stack[-1] is None:
        #        exit(55)
        #    self.frame_stack[-1][variable_name] = {'value': to_assign, 'type': 'bool'}
        #elif frame_name == 'TF':
        #    if self.temporary_frame is None:
        #        exit(55)
        #    self.temporary_frame[variable_name] = {'value': to_assign, 'type': 'bool'}
        #else:
        #    exit(32)

    def gt(self, inst):
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'int', 'var', 'string', 'bool'}, {'int', 'string', 'bool'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var', 'string', 'bool'}, {'int', 'string', 'bool'})

        if arg2_value is None or arg3_value is None:
            exit(56)
        
        if inst.arg2.type == 'nil' or inst.arg3.type == 'nil':
            exit(53)

        if inst.arg2.type != inst.arg3.type:
            exit(53)

        if inst.arg2.type == 'bool':
            if arg2_value == 'true':
                arg2_value = 1
            else:
                arg2_value = 0

            if arg3_value == 'true':
                arg3_value = 1
            else:
                arg3_value = 0

            to_assign = arg2_value > arg3_value   

        if inst.arg2.type == 'int':
            arg2_value = int(arg2_value)
            arg3_value = int(arg3_value)
        
        if inst.arg2.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
            arg2_value = re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1), 10)), arg2_value)
        
        if inst.arg2.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
                arg3_value = re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1), 10)), arg3_value)

        if inst.arg2.type != 'bool':
            to_assign = arg2_value > arg3_value
             
        to_assign = str(to_assign)
        to_assign = to_assign.lower()

        self.assign(inst.arg1, to_assign, 'bool')


    #    frame_name, variable_name = self.get_frame(inst.arg1)
    #    if frame_name == 'GF':
    #        self.global_frame[variable_name] = {'value': to_assign, 'type': 'bool'}
    #    elif frame_name == 'LF':
    #        if self.frame_stack[-1] is None:
    #            exit(55)
    #        self.frame_stack[-1][variable_name] = {'value': to_assign, 'type': 'bool'}
    #    elif frame_name == 'TF':
    #        if self.temporary_frame is None:
    #            exit(55)
    #        self.temporary_frame[variable_name] = {'value': to_assign, 'type': 'bool'}
    #    else:
    #        exit(32)

    def eq(self, inst):
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'int', 'var', 'string', 'bool', 'nil'}, {'int', 'string', 'bool', 'nil'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var', 'string', 'bool', 'nil'}, {'int', 'string', 'bool', 'nil'})

        if arg2_value is None or arg3_value is None:
            exit(56)
        
        if inst.arg2.type == 'nil' or inst.arg3.type == 'nil':
            if inst.arg2.value == 'nil' and inst.arg3.value == 'nil':
                to_assign = True
            else:
                to_assign = False
        else:
            if inst.arg2.type != inst.arg3.type:
                exit(53)
        
        if inst.arg2.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
            arg2_value = re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1), 10)), arg2_value)
        
        if inst.arg3.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
                arg3_value = re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1), 10)), arg3_value)

        to_assign = arg2_value == arg3_value

        #print("XX", to_assign, arg2_value, arg3_value, "XX")
        to_assign = str(to_assign)
        to_assign = to_assign.lower()

        self.assign(inst.arg1, to_assign, 'bool')

        #frame_name, variable_name = self.get_frame(inst.arg1)
        #if frame_name == 'GF':
        #    self.global_frame[variable_name] = {'value': to_assign, 'type': 'bool'}
        #elif frame_name == 'LF':
        #    if self.frame_stack[-1] is None:
        #        exit(55)
        #    self.frame_stack[-1][variable_name] = {'value': to_assign, 'type': 'bool'}
        #elif frame_name == 'TF':
        #    if self.temporary_frame is None:
        #        exit(55)
        #    self.temporary_frame[variable_name] = {'value': to_assign, 'type': 'bool'}
        #else:
        #    exit(32)

    def and_(self, inst):
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'bool', 'var'}, {'bool'})
        arg3_value = self.symb_check(inst.arg3, {'bool', 'var'}, {'bool'})

        if arg2_value is None or arg3_value is None:
            exit(56)
        
        if arg2_value == 'true' and arg3_value == 'true':
            to_assign = True
        else:
            to_assign = False
        
        to_assign = str(to_assign)
        to_assign = to_assign.lower()

        self.assign(inst.arg1, to_assign, 'bool')
    #    frame_name, variable_name = self.get_frame(inst.arg1)
    #    if frame_name == 'GF':
    #        self.global_frame[variable_name] = {'value': to_assign, 'type': 'bool'}
    #    elif frame_name == 'LF':
    #        if self.frame_stack[-1] is None:
    #            exit(55)
    #        self.frame_stack[-1][variable_name] = {'value': to_assign, 'type': 'bool'}
    #    elif frame_name == 'TF':
    #        if self.temporary_frame is None:
    #            exit(55)
    #        self.temporary_frame[variable_name] = {'value': to_assign, 'type': 'bool'}
    #    else:
    #        exit(32)

    def or_(self, inst):
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'bool', 'var'}, {'bool'})
        arg3_value = self.symb_check(inst.arg3, {'bool', 'var'}, {'bool'})

        if arg2_value is None or arg3_value is None:
            exit(56)
        
        if arg2_value == 'true' or arg3_value == 'true':
            to_assign = True
        else:
            to_assign = False
        
        to_assign = str(to_assign)
        to_assign = to_assign.lower()

        self.assign(inst.arg1, to_assign, 'bool')
        #frame_name, variable_name = self.get_frame(inst.arg1)
        #if frame_name == 'GF':
        #    self.global_frame[variable_name] = {'value': to_assign, 'type': 'bool'}
        #elif frame_name == 'LF':
        #    if self.frame_stack[-1] is None:
        #        exit(55)
        #    self.frame_stack[-1][variable_name] = {'value': to_assign, 'type': 'bool'}
        #elif frame_name == 'TF':
        #    if self.temporary_frame is None:
        #        exit(55)
        #    self.temporary_frame[variable_name] = {'value': to_assign, 'type': 'bool'}
        #else:
        #    exit(32)

    def not_(self, inst):
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'bool', 'var'}, {'bool'})

        if arg2_value is None:
            exit(56)

        if arg2_value == 'true':
            to_assign = False
        else:
            to_assign = True

        to_assign = str(to_assign)
        to_assign = to_assign.lower()

        self.assign(inst.arg1, to_assign, 'bool')
    #    frame_name, variable_name = self.get_frame(inst.arg1)
    #    if frame_name == 'GF':
    #        self.global_frame[variable_name] = {'value': to_assign, 'type': 'bool'}
    #    elif frame_name == 'LF':
    #        if self.frame_stack[-1] is None:
    #            exit(55)
    #        self.frame_stack[-1][variable_name] = {'value': to_assign, 'type': 'bool'}
    #    elif frame_name == 'TF':
    #        if self.temporary_frame is None:
    #            exit(55)
    #        self.temporary_frame[variable_name] = {'value': to_assign, 'type': 'bool'}
    #    else:
    #        exit(32)

        

        


        #    if inst.arg2.type == 'int':
        #        arg2_value = int(arg2_value)
        #        arg3_value = int(arg3_value)
        #    
        #    if inst.arg2.type == 'string':
        #        arg2_value = s = re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1), 10)), arg2_value)
        #    
        #    if inst.arg3.type == 'string':
        #            arg3_value = s = re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1), 10)), arg3_value)
#
        #    if inst.arg2.type != 'bool':
        #        to_assign = arg2_value == arg3_value
        
    def int2char(self, inst):
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'int', 'var'}, {'int'})

        if arg2_value is None:
            exit(56)

        try:
            to_assign = chr(int(arg2_value))
        except ValueError:
            exit(58)

        self.assign(inst.arg1, to_assign, 'string')

    def stri2int(self, inst):
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'string', 'var'}, {'string'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var'}, {'int'})

        if inst.arg2.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
            arg2_value = re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1), 10)), arg2_value)

        if arg2_value is None or arg3_value is None:
            exit(56)

        if int(arg3_value) < 0 or int(arg3_value) >= len(arg2_value):
            exit(58)

        try:
            to_assign = ord(arg2_value[int(arg3_value)])
        except IndexError:
            exit(58)

        self.assign(inst.arg1, to_assign, 'int')

    def read(self, inst):
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'type'}, None)

        if arg2_value is None:
            exit(56)

        if arg2_value == 'int':
            try:
                to_assign = input()
            except EOFError or ValueError:
                to_assign = 'nil'
                arg2_value = 'nil'
        
        elif arg2_value == 'bool':
            try:
                to_assign = input().lower()
            except EOFError or ValueError:
                to_assign = 'nil'
                arg2_value = 'nil'
           
            if to_assign != 'nil':
                if to_assign == 'true':
                    to_assign = True
                else:
                    to_assign = False
        
        elif arg2_value == 'string':
            try:
                to_assign = input()
            except EOFError or ValueError:
                to_assign = 'nil'
                arg2_value = 'nil'
            
            if to_assign != 'nil':
                to_assign = re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1), 10)), to_assign)

        self.assign(inst.arg1, to_assign, arg2_value)

    def write(self, inst):
        arg1 = self.symb_check(inst.arg1, {'var', 'int', 'bool', 'string', 'nil'}, None)

        if arg1 is None:
            exit(56)

        if inst.arg1.type == 'string':
            arg1 = self.string_replace(arg1)
        

        if inst.arg1.type == 'var':
            frame_name, variable_name = self.get_frame(inst.arg1)
            if frame_name == 'GF':
                if self.global_frame[variable_name]['type'] == 'nil':
                    arg1 = "" 
            elif frame_name == 'LF':
                if self.frame_stack[-1][variable_name]['type'] == 'nil':
                    arg1 = ""
            elif frame_name == 'TF':
                if self.temporary_frame[variable_name]['type'] == 'nil':
                    arg1 = ""
            else:
                exit(32)
        
        if inst.arg1.type in ["var","int", "bool", "string"]:
            print(arg1, end="")
        elif inst.arg1.type == "nil":
            print("", end="")
        else:
            exit(32)


    def concat(self, inst):
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'string', 'var'}, {'string'})
        arg3_value = self.symb_check(inst.arg3, {'string', 'var'}, {'string'})

        if arg2_value is None or arg3_value is None:
            exit(56)

        if inst.arg2.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
            arg2_value = re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1), 10)), arg2_value)
        if inst.arg3.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
            arg3_value = re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1), 10)), arg3_value)

        to_assign = arg2_value + arg3_value

        self.assign(inst.arg1, to_assign, 'string')   

    def strlen(self, inst):
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'string', 'var'}, {'string'})

        if arg2_value is None:
            exit(56)

        if inst.arg2.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
            arg2_value = re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1), 10)), arg2_value)

        to_assign = len(arg2_value)

        self.assign(inst.arg1, to_assign, 'int') 

    def getchar(self, inst):
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'string', 'var'}, {'string'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var'}, {'int'})

        if arg2_value is None or arg3_value is None:
            exit(56)

        if inst.arg2.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
            arg2_value = re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1), 10)), arg2_value)

        if int(arg3_value) < 0 or int(arg3_value) >= len(arg2_value):
            exit(58)

        to_assign = arg2_value[int(arg3_value)]

        self.assign(inst.arg1, to_assign, 'string')
    
    def setchar(self, inst):
        arg1_value = self.symb_check(inst.arg1, {'string', 'var'}, {'string'})
        arg2_value = self.symb_check(inst.arg2, {'int', 'var'}, {'int'})
        arg3_value = self.symb_check(inst.arg3, {'string', 'var'}, {'string'})

        if arg1_value is None or arg2_value is None or arg3_value is None:
            exit(56)

        if inst.arg1.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
            arg1_value = re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1), 10)), arg1_value)
        if inst.arg3.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
            arg3_value = re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1), 10)), arg3_value)

        if int(arg2_value) < 0 or int(arg2_value) >= len(arg1_value):
            exit(58)

        if len(arg3_value) < 1:
            exit(58)

        if len (arg3_value) > 1:
            arg3_value = arg3_value[0]

        to_assign = arg1_value[:int(arg2_value)] + arg3_value + arg1_value[int(arg2_value)+1:]

        self.assign(inst.arg1, to_assign, 'string')

    def type_(self, inst):
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'var', 'int', 'bool', 'string', 'nil'}, None)

        
        if arg2_value is None:
            to_assign = ""
        elif inst.arg2.type == 'var':
            frame_name, variable_name = self.get_frame(inst.arg2)
            if frame_name == 'GF':
                to_assign = self.global_frame[variable_name]['type']
            elif frame_name == 'LF':
                to_assign = self.frame_stack[-1][variable_name]['type']
            elif frame_name == 'TF':
                to_assign = self.temporary_frame[variable_name]['type']
            else:
                exit(32)
        else:
            to_assign = inst.arg2.type
        
        frame_name, variable_name = self.get_frame(inst.arg1)
        if frame_name == 'GF':
            if to_assign == "":
                self.global_frame[variable_name]['value'] = ""
            else:
                self.global_frame[variable_name]['value'] = to_assign
            self.global_frame[variable_name]['type'] = 'string'
        
        elif frame_name == 'LF':
            if to_assign == "":
                self.frame_stack[-1][variable_name]['value'] = ""
            else:
                self.frame_stack[-1][variable_name]['value'] = to_assign
            self.frame_stack[-1][variable_name]['type'] = 'string'
        
        elif frame_name == 'TF':
            if to_assign == "":
                self.temporary_frame[variable_name]['value'] = ""
            else:
                self.temporary_frame[variable_name]['value'] = to_assign
            self.temporary_frame[variable_name]['type'] = 'string'
        else:
            exit(32)

    def jump(self, inst):
        self.symb_check(inst.arg1, {'label'}, None)
        self.instruction_counter = self.labels[inst.arg1.value] - 1
    
    def jumpifeq(self, inst):
        arg1_value = self.symb_check(inst.arg1, {'label'}, None)
        arg2_value = self.symb_check(inst.arg2, {'int', 'var', 'string', 'bool', 'nil'}, {'int', 'string', 'bool', 'nil'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var', 'string', 'bool', 'nil'}, {'int', 'string', 'bool', 'nil'})

        if arg2_value is None or arg3_value is None:
            exit(56)

        if arg1_value not in self.labels:
            exit(52)
        
        if inst.arg2.type == 'nil' or inst.arg3.type == 'nil':
            if inst.arg2.value == 'nil' and inst.arg3.value == 'nil':
                value = True
            else:
                value = False
        else:
            if inst.arg2.type != inst.arg3.type:
                exit(53)
        
        if inst.arg2.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
            arg2_value = re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1), 10)), arg2_value)
        
        if inst.arg3.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
                arg3_value = re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1), 10)), arg3_value)

        value = arg2_value == arg3_value

        if value == True:
            self.instruction_counter = self.labels[inst.arg1.value] - 1

    def jumpifneq(self, inst):
        arg1_value = self.symb_check(inst.arg1, {'label'}, None)
        arg2_value = self.symb_check(inst.arg2, {'int', 'var', 'string', 'bool', 'nil'}, {'int', 'string', 'bool', 'nil'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var', 'string', 'bool', 'nil'}, {'int', 'string', 'bool', 'nil'})

        if arg2_value is None or arg3_value is None:
            exit(56)

        if arg1_value not in self.labels:
            exit(52)
        
        if inst.arg2.type == 'nil' or inst.arg3.type == 'nil':
            if inst.arg2.value == 'nil' and inst.arg3.value == 'nil':
                value = True
            else:
                value = False
        else:
            if inst.arg2.type != inst.arg3.type:
                exit(53)
        
        if inst.arg2.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
            arg2_value = re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1), 10)), arg2_value)
        
        if inst.arg3.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
                arg3_value = re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1), 10)), arg3_value)

        value = arg2_value == arg3_value

        if value == False:
            self.instruction_counter = self.labels[inst.arg1.value] - 1


    def exit(self, inst):
        arg1_value = self.symb_check(inst.arg1, {'int', 'var'}, {'int'})
        
       
        if arg1_value is None:
            exit(56)

        arg1_value = int(arg1_value)
        if arg1_value < 0 or arg1_value > 49:
            exit(57)

        sys.exit(arg1_value)
    
    

if __name__ == '__main__':
    I = Interpret()
    I.main()
    




