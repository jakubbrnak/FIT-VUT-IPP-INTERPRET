
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
                
                if argument.attrib.get("type") == "string":
                    if re.match(r"^([^\#\\\s]|(\\\\[0-9]{3}))*$", argument.text) is None:
                        print("asdfasdfasdfasdfasd")
                        exit(32)
                
                if argument.attrib.get("type") == "nil":
                    if argument.text is not None:
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
        self.instruction_counter = 0
        self.labels = {}

    def execute(self):
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
                self.return_(self.instruction_list[self.instruction_counter])
            
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
            
            elif self.instruction_list[self.instruction_counter].opcode == "LABEL":
                self.label(self.instruction_list[self.instruction_counter])
            
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
            
                if var_type and self.global_frame[variable_name]['type'] != var_type:
                    exit(53)
                value = self.global_frame[variable_name]['value']
            
            elif frame_name == 'LF':
                if len(self.frame_stack) == 0:
                    exit(55)
                
                if self.frame_stack[-1] is None:
                    exit(55)
                
                if variable_name not in self.frame_stack[-1]:
                    exit(54)
               
                if var_type and self.frame_stack[-1][variable_name]['type'] != var_type:
                    exit(53)
                value = self.frame_stack[-1][variable_name]['value']
            
            elif frame_name == 'TF':
                if not self.temporary_frame:
                    exit(55)
                
                if variable_name not in self.temporary_frame:
                    exit(54)

                if var_type and self.temporary_frame[variable_name]['type'] != var_type:
                    exit(53)    
                
                value = self.temporary_frame[variable_name]['value']
         
            return value
        
        elif arg.type in ("int", "bool", "string", "nil"):
            return arg.value
       
        elif arg.type == "nil":
            return None
        
        else:
            exit(32)
    
    def string_replace(self, toreplace):
        toreplace = toreplace.replace("\\032", " ")
        toreplace = toreplace.replace("\\092", "\\")
        toreplace = toreplace.replace("\\010", "\n")
        toreplace = toreplace.replace("\\035", "#")
        return toreplace

    def move(self, inst):
        arg1 = self.symb_check(inst.arg1, 'var', None)
        arg2 = self.symb_check(inst.arg2, {'int', 'bool', 'string', 'var', 'nil'}, None)

        if inst.arg2.type == 'string':
            arg2 = self.string_replace(arg2)

        frame_name, variable_name = self.get_frame(inst.arg1)
        if frame_name == 'GF':
            self.global_frame[variable_name]['value'] = inst.arg2.value
            self.global_frame[variable_name]['type'] = inst.arg2.type
        elif frame_name == 'LF':
            self.frame_stack[-1][variable_name]['value'] = inst.arg2.value
            self.frame_stack[-1][variable_name]['type'] = inst.arg2.type
        elif frame_name == 'TF':
            self.temporary_frame[variable_name]['value'] = inst.arg2.value
            self.temporary_frame[variable_name]['type'] = inst.arg2.type
        else:
            exit(32)

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
            if self.frame_stack[-1] is None:
                exit(55)  # no frame to define variable in
            self.frame_stack[-1][variable_name] = {'value': None, 'type': None}
       
        elif frame_name == 'TF':
            if self.temporary_frame is None:

                exit(55)  # no frame to define variable in

            self.temporary_frame[variable_name] = {'value': None, 'type': None}
        else:
            exit(32)

    def call(self, inst):
        if inst.arg1.type == "label":
            self.instruction_counter = self.labels[self.instruction_list[self.instruction_counter].arg1.value]
        else:
            exit(32)
    
    def return_(self):
        if len(self.frame_stack) == 0:
            exit(56)
        else:
            self.instruction_counter = self.frame_stack.pop()

    def pushs(self, inst):
        arg1 = self.instruction_list[self.instruction_counter].arg1
        value = None
    
        if arg1.type == "var":
            value = self.variables.get(arg1.value)
        elif arg1.type in ("int", "bool", "string", "nil"):
            value = arg1.value
    
        if value is None:
            exit(56) 
    
        self.data_stack.append(value)

    def pops(self):
        if self.instruction_list[self.instruction_counter].arg1.type == "var":
            if self.data_stack == []:
                exit(56)
            else:
                self.variables[self.instruction_list[self.instruction_counter].arg1.value] = self.data_stack.pop()
        else:
            exit(32)

    def add(self, inst):
        
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value= self.symb_check(inst.arg2, {'int', 'var'}, {'int'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var'}, {'int'})

        
        
        frame_name, variable_name = self.get_frame(inst.arg1)
        
        if frame_name == 'GF':
            self.global_frame[variable_name] = {'value': arg2_value + arg3_value, 'type': 'int'}
        elif frame_name == 'LF':
            if not self.frame_stack[-1]:
                exit(55)  # no frame to define variable in
            self.frame_stack[-1][variable_name] = {'value': arg2_value + arg3_value, 'type': 'int'}
        elif frame_name == 'TF':
            if not self.temporary_frame:
                exit(55)  # no frame to define variable in
            self.temporary_frame[variable_name] = {'value': arg2_value + arg3_value, 'type': 'int'}
        else:
            exit(32)

    
    
    def sub(self, inst):
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value= self.symb_check(inst.arg2, {'int', 'var'}, {'int'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var'}, {'int'})

        frame_name, variable_name = self.get_frame(inst.arg1)
        
        if frame_name == 'GF':
            self.global_frame[variable_name] = {'value': arg2_value - arg3_value, 'type': 'int'}
        elif frame_name == 'LF':
            if not self.frame_stack[-1]:
                exit(55)  # no frame to define variable in
            self.frame_stack[-1][variable_name] = {'value': arg2_value - arg3_value, 'type': 'int'}
        elif frame_name == 'TF':
            if not self.temporary_frame:
                exit(55)  # no frame to define variable in
            self.temporary_frame[variable_name] = {'value': arg2_value - arg3_value, 'type': 'int'}
        else:
            exit(32)
    
    def mul(self, inst):
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value= self.symb_check(inst.arg2, {'int', 'var'}, {'int'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var'}, {'int'})

        frame_name, variable_name = self.get_frame(inst.arg1)
        
        if frame_name == 'GF':
            self.global_frame[variable_name] = {'value': arg2_value * arg3_value, 'type': 'int'}
        elif frame_name == 'LF':
            if not self.frame_stack[-1]:
                exit(55)  # no frame to define variable in
            self.frame_stack[-1][variable_name] = {'value': arg2_value * arg3_value, 'type': 'int'}
        elif frame_name == 'TF':
            if not self.temporary_frame:
                exit(55)  # no frame to define variable in
            self.temporary_frame[variable_name] = {'value': arg2_value * arg3_value, 'type': 'int'}
        else:
            exit(32)
    

    def idiv(self, inst):
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value= self.symb_check(inst.arg2, {'int', 'var'}, {'int'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var'}, {'int'})

        frame_name, variable_name = self.get_frame(inst.arg1)
        
        if arg3_value == 0:
            exit(57)

        if frame_name == 'GF':
            self.global_frame[variable_name] = {'value': arg2_value / arg3_value, 'type': 'int'}
        elif frame_name == 'LF':
            if not self.frame_stack[-1]:
                exit(55)  # no frame to define variable in
            self.frame_stack[-1][variable_name] = {'value': arg2_value / arg3_value, 'type': 'int'}
        elif frame_name == 'TF':
            if not self.temporary_frame:
                exit(55)  # no frame to define variable in
            self.temporary_frame[variable_name] = {'value': arg2_value / arg3_value, 'type': 'int'}
        else:
            exit(32)
    

    def write(self, inst):
        arg1 = self.symb_check(inst.arg1, {'var', 'int', 'bool', 'string', 'nil'}, None)
        
        if inst.arg1.type == 'string':
            arg1 = self.string_replace(arg1)
            #print("AAAAAAAAAAAAAAAA",arg1,"AAAAAAAAAAAAAAAAA" )
      
        
        if inst.arg1.type in ["var","int", "bool", "string"]:
            print(arg1, end="")
        elif arg1.type == "nil":
            print("", end="")
        else:
            exit(32)
        

    
    

if __name__ == '__main__':
    I = Interpret()
    I.main()
    




