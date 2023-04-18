
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

#class for parsing arguments from command line
class Argument_parser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("--source", nargs = 1, help="input file with XML representation of source code")
        self.parser.add_argument("--input", nargs = 1, help="input file with inputs for interpretation of source code")
        self.args = self.parser.parse_args()
        self.check_args()

    #check if arguments are valid
    def check_args(self):
        if self.args.source is None and self.args.input is None:
            exit(10)
       
       #check if source file exists
        if self.args.source is not None:
            try:
                self.source = open(self.args.source[0], "r")
                self.source.close()
                self.source = self.args.source[0]
            except IOError:
                exit(11)
        else:        
            self.source = None

        #check if input file exists
        if self.args.input is not None:
            try:
                self.input = open(self.args.input[0], "r")
                #self.input.close()
                #self.input = self.args.input[0]
            except IOError:
                exit(11)
        else:  
            self.input = None 
    
    #return source file
    def get_source(self):
        return self.source
  
    #return input file
    def get_input(self):
        return self.input

    #return arguments
    def get_args(self):
        return self.args

#class for parsing arguments from xml file
class Argument:
    def __init__(self, type, value):
        self.type = type
        self.value = value

#class for parsing instructions from xml file    
class Instruction:
    instruction_list = []
    
    def __init__(self, opcode, order, arg1, arg2, arg3):
        self.opcode = opcode
        self.order = order
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
    
    #append instruction to instruction list
    def append_instruction(self):
        while len(self.instruction_list) <= int(self.order): 
            self.instruction_list.append(None)

        #check if instruction with same order is already in instruction list
        if self.instruction_list[int(self.order)] is not None:
            exit(32)

        self.instruction_list[int(self.order)] = self

#class for interpreting
class Interpret:
    def __init__(self):

        #call agrument parser to check command line arguments
        self.arg_parser = Argument_parser()

        #get source and input file
        self.source = self.arg_parser.get_source()
        self.input = self.arg_parser.get_input()
        
        #create empty list for instructions and initialize instruction object
        self.instruction_list = []
        self.i = Instruction
    
    #method for parsing xml file
    def parse_xml(self):
        if self.source is not None:
            
            #check for parse error and parse xml file or xml stdin input
            try:
                self.tree = ET.parse(self.source)
            except ET.ParseError:
                exit(31)
            self.root = self.tree.getroot()
        else:
            self.tree = ET.parse(sys.stdin)
            self.root = self.tree.getroot()
    
    #check if xml file is valid
    def check_xml(self):
        if self.root.tag != "program":
            exit(32)

        if self.root.attrib.get("language") != "IPPcode23":
            exit(32)
    
        #for loop for checking if instruction is valid adn performing semantic analysis    
        for instruction in self.root:

            #check if instruction tag is valid
            if instruction.tag != "instruction":
                exit(32)
            
            #check if order attribute is present
            if instruction.attrib.get("order") is None:
                exit(32)

            #check if order attribute is not less than 1
            if int(instruction.attrib.get("order")) < 1:
                exit(32)      
            
            #check if order attribute is integer
            if re.match(r"^[-+]?[0-9]+$", instruction.attrib.get("order")) is None:
                exit(32)  
            
            #check if opcode attribute is present
            if instruction.attrib.get("opcode") is None:
                exit(32)
            
            #check if opcode attribute value is valid
            if instruction.attrib.get("opcode") not in ["MOVE", "CREATEFRAME", "PUSHFRAME", "POPFRAME", "DEFVAR", "CALL", "RETURN", "PUSHS", "POPS", "ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR", "NOT", "INT2CHAR", "STRI2INT", "READ", "WRITE", "CONCAT", "STRLEN", "GETCHAR", "SETCHAR", "TYPE", "LABEL", "JUMP", "JUMPIFEQ", "JUMPIFNEQ", "EXIT", "DPRINT", "BREAK"]:
                exit(32)
            
            #check if arguments are valid
            for argument in instruction:
                
                #check if argument tag is valid
                if argument.tag != "arg1" and argument.tag != "arg2" and argument.tag != "arg3": 
                    exit(32)
                
                #check if type attribute is present
                if argument.attrib.get("type") is None:
                    exit(32)
                
                #check if type attribute value is valid
                if argument.attrib.get("type") not in ["var", "symb", "label", "type", "nil", "int", "bool", "string"]:
                    exit(32)
                
                #semantic analtsis of arguments
                if argument.attrib.get("type") == "var":
                    if re.match(r"^(GF|LF|TF)@[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$", argument.text) is None:
                        exit(32)
               
                #<label>
                if argument.attrib.get("type") == "label":
                    if re.match(r"^[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$", argument.text) is None:
                        exit(32)
                #<type>
                if argument.attrib.get("type") == "type":
                    if argument.text not in ["int", "bool", "string"]:
                        exit(32)
                
                #<int>
                if argument.attrib.get("type") == "int":
                    if re.match(r"^[-+]?[0-9]+$", argument.text) is None:
                        exit(32)
                #<bool>
                if argument.attrib.get("type") == "bool":
                    if argument.text not in ["true", "false"]:
                       exit(32)
                
            #    if argument.attrib.get("type") == "string":
            #        if re.match(r"(?!\\[0-9]{3})[\s\\#]", argument.text) is None:
            #            print(argument.text)
            #            print("BBBBBBBBBBBBBBBBBBBBB")
            #            exit(32)
            #    
                
                #<nil>
                if argument.attrib.get("type") == "nil":
                    if argument.text != "nil":
                        exit(32)
                
                #<symb>
                if argument.attrib.get("type") == "symb":
                    if re.match(r"^(GF|LF|TF)@[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$", argument.text) is None and re.match(r"^([^\#\\\s]|(\\\\[0-9]{3}))*$", argument.text) is None and re.match(r"^[-+]?[0-9]+$", argument.text) is None and argument.text not in ["true", "false", "nil"]:
                        exit(32)

    #load instructions from xml file to instruction list
    def load_instructions(self):

        #for loop for iterating through instructions in xml structure
        for instruction in self.root:
            self.i = Instruction(instruction.attrib.get("opcode"), instruction.attrib.get("order"), None, None, None)
            
            #for loop for iterating through arguments in xml structure
            for argument in instruction:
                if argument.tag == "arg1":
                    self.i.arg1 = Argument(argument.attrib.get("type"), argument.text)
                if argument.tag == "arg2":
                    self.i.arg2 = Argument(argument.attrib.get("type"), argument.text)
                if argument.tag == "arg3":
                    self.i.arg3 = Argument(argument.attrib.get("type"), argument.text)
            
            #append instruction to instruction list
            self.i.append_instruction()
    
    #main function to call all parts of the program
    def main(self):
   
        self.parse_xml()
        
        self.check_xml()   
        
        self.load_instructions()
        
        execute = Execute(self.i.instruction_list)
        
        execute.execute()

#class for executiin of instructions
class Execute:
    def __init__(self, instruction_list):

        #instruction list initialization
        self.instruction_list = instruction_list
        
        #stack lists initialization
        self.data_stack = []
        self.call_stack = []
        self.frame_stack = []

        #temporary frame and global frame initialization
        self.temporary_frame = None
        self.global_frame = {}

        #instruction counter initialization
        self.instruction_counter = int(0)

        #labels dictionary initialization
        self.labels = {}

    #method for loading labels to labels dictionary during first go through instructions
    def load_labels(self):
        for instruction in self.instruction_list:
            if instruction != None:
                if instruction.opcode == "LABEL":
                    if instruction.arg1.value in self.labels:
                        exit(52)
                    self.labels[instruction.arg1.value] = int(instruction.order)

    #method for executing instructions
    def execute(self):

        #load labels to labels dictionary
        self.load_labels()

        #while loop for executing instructions until the end of instruction list
        while self.instruction_counter < len(self.instruction_list):

            #check if instruction is not None, if yes skip to next instruction
            if self.instruction_list[self.instruction_counter] != None:

                #check opcode and execure appropriate method
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

            #increment instruction counter
            self.instruction_counter += 1

        #exit program after successful interpretation
        sys.exit(0)

    #helper method to get frame name and variable name from argument value
    def get_frame(self, arg):
        var_name = arg.value
        frame_name, variable_name = var_name.split('@', maxsplit=1)
        return frame_name, variable_name

    #helper method to get type of argument either from variable or from constant
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

    #helper method to check if argument is of correct type and get its value
    def symb_check(self, arg, type, var_type):
        
        #check if argument is present
        if arg is None:
            exit(32)
            
        #check if argument is of correct type
        if arg.type not in type:
            exit(53)
        
        #if argument is variable
        if arg.type == "var":

            #get frame name and variable name from helper method get_frame()
            frame_name, variable_name = self.get_frame(arg)

            #check if variable is defined in corresponding framem perform type check if necessary and assign value to return
            if frame_name == 'GF':

                #check if variable is defined in global frame
                if variable_name not in self.global_frame:
                    exit(54)

                #check if value stored in variable is of correct type
                if var_type and self.global_frame[variable_name]['type'] != None and self.global_frame[variable_name]['type'] not in var_type:
                    exit(53)
                
                #assign value to return
                value = self.global_frame[variable_name]['value']
            
            elif frame_name == 'LF':

                #check if frame stack is not empty
                if len(self.frame_stack) == 0:
                    exit(55)

                #check if variable is defined in local frame
                if variable_name not in self.frame_stack[-1]:
                    exit(54)
               
                #check if value stored in variable is of correct type
                if var_type and self.frame_stack[-1][variable_name]['type'] != None and self.frame_stack[-1][variable_name]['type'] not in var_type:
                    exit(53)
                
                #assign value to return
                value = self.frame_stack[-1][variable_name]['value']
            
            elif frame_name == 'TF':
                
                #check if temporary frame is initialized
                if self.temporary_frame is None:
                    exit(55)
                
                #check if variable is defined in temporary frame
                if variable_name not in self.temporary_frame:
                    exit(54)
                
                #check if value stored in variable is of correct type
                if var_type and self.temporary_frame[variable_name]['type'] != None and self.temporary_frame[variable_name]['type'] not in var_type:
                    exit(53)    
                
                #assign value to return
                value = self.temporary_frame[variable_name]['value']
         
            return value
        
        #if agrument is constant
        elif arg.type in ("int", "bool", "string", "nil", "type", "label"):
            
            #if argument type is string and value is none, return empty string
            if arg.type == "string" and arg.value is None:
                return ""
            else:
                return arg.value
            
        else:
            exit(32)

        
    #helper method to convert escape sequences in string to their corresponding characters
    def string_replace(self, toreplace):
        toreplace = re.sub(r'\\(\d{1,3})', lambda m: chr(int(m.group(1), 10)), toreplace)
        return toreplace
    
    #helper method to assign value to variable in correct frame
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

    #execution of instruction MOVE
    def move(self, inst):

        #check if arguments are of correct type and get necessary values
        self.symb_check(inst.arg1, 'var', None)
        arg2 = self.symb_check(inst.arg2, {'int', 'bool', 'string', 'var', 'nil'}, None)

        #check if argument is present
        if arg2 is None:
            exit(56)

        #edit string to be compatible with further operations
        if inst.arg2.type == 'string':
            arg2 = self.string_replace(arg2)
            if inst.arg2.value is None:
                inst.arg2.value = ""

        #assign value to variable
        self.assign(inst.arg1, arg2, inst.arg2.type)

    #execution of instruction CREATEFRAME
    def createframe(self):

        #initialize temporary_frame as empty dictionary
        self.temporary_frame = {}

    #execution of instruction PUSHFRAME
    def pushframe(self):

        #check if temporary frame is initialized, if not, exit with error code 55
        if self.temporary_frame == None:
            exit(55)
        else: 

            #push temporary frame to frame_stack and set temporary frame to None
            self.frame_stack.append(self.temporary_frame)
            self.temporary_frame = None

    #execution of instruction POPFRAME
    def popframe(self):

        #check if frame stack is not empty, if it is, exit with error code 55
        if len(self.frame_stack) == 0:
            exit(55)
        else:
            self.temporary_frame = self.frame_stack.pop()

    #execution of instruction DEFVAR
    def defvar(self, inst):

        #check if argument is of correct type
        frame_name, variable_name = self.get_frame(inst.arg1)

        #check if variable is not already defined in corresponding frame and define it
        if frame_name == 'GF':
            if variable_name in self.global_frame:
                exit(52)
            self.global_frame[variable_name] = {'value': None, 'type': None}
       
        elif frame_name == 'LF':
            if len(self.frame_stack) == 0:
                exit(55) 
            
            if variable_name in self.frame_stack[-1]:
                exit(52)
            self.frame_stack[-1][variable_name] = {'value': None, 'type': None}
       
        elif frame_name == 'TF':
            if self.temporary_frame is None:
                exit(55)  

            if variable_name in self.temporary_frame:
                exit(52)

            self.temporary_frame[variable_name] = {'value': None, 'type': None}
        else:
            exit(32)

    #execution of instruction CALL
    def call(self, inst):

        #check if argument is of correct type
        if inst.arg1.type != "label":
            exit(32)
        
        #check if label is defined and set instruction counter to label value
        if inst.arg1.value in self.labels:
            self.call_stack.append(self.instruction_counter)
            self.instruction_counter = self.labels[inst.arg1.value] - 1
        else:
            exit(52)

    #execution of instruction RETURN
    def return_(self):

        #check if call stack is not empty, if it is, exit with error code 56
        if len(self.call_stack) == 0:
            exit(56)
        else:

            #pop value from call stack to instruction counter
            self.instruction_counter = self.call_stack.pop()

    #execution of instruction PUSHS
    def pushs(self, inst):
        
        #check if argument is of correct type and get necessary values
        arg1 = self.symb_check(inst.arg1, {'int', 'bool', 'string', 'var', 'nil'}, None)

        if arg1 is None:
            exit(56)
        
        #push value to data stack
        self.data_stack.append(arg1)

    def pops(self, inst):
        
        #check if data stack is not empty, if it is, exit with error code 56
        if len(self.data_stack) == 0:
            exit(56)
        self.symb_check(inst.arg1, {'var'}, None)
        
        #pop value from data stack to variable
        to_assign = self.data_stack.pop()
        self.assign(inst.arg1, to_assign, type(to_assign))

    #execution of instruction ADD
    def add(self, inst):
        
        #check if arguments are of correct type and get necessary values
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value= self.symb_check(inst.arg2, {'int', 'var'}, {'int'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var'}, {'int'})

        #check if arguments are present
        if arg2_value is None or arg3_value is None:
            exit(56)
        
        #assign value to variable
        self.assign(inst.arg1, int(arg2_value) + int(arg3_value), 'int')
    
    #execution of instruction SUB
    def sub(self, inst):

        #check if arguments are of correct type and get necessary values
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value= self.symb_check(inst.arg2, {'int', 'var'}, {'int'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var'}, {'int'})

        #check if arguments are present
        if arg2_value is None or arg3_value is None:
            exit(56)

        #assign value to variable
        self.assign(inst.arg1, int(arg2_value) - int(arg3_value), 'int')
    
    #execution of instruction MUL
    def mul(self, inst):

        #check if arguments are of correct type and get necessary values
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value= self.symb_check(inst.arg2, {'int', 'var'}, {'int'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var'}, {'int'})

        #check if arguments are present
        if arg2_value is None or arg3_value is None:
            exit(56)
        
        #assign value to variable
        self.assign(inst.arg1, int(arg2_value) * int(arg3_value), 'int')

    #execution of instruction IDIV
    def idiv(self, inst):

        #check if arguments are of correct type and get necessary values
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'int', 'var'}, {'int'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var'}, {'int'})

        #check if arguments are present
        if arg2_value is None or arg3_value is None:
            exit(56)
        
        #check if division by zero occurs, if it does, exit with error code 57
        if int(arg3_value) == 0:
            exit(57)

        #assign value to variable
        self.assign(inst.arg1, int(arg2_value) // int(arg3_value), 'int')
    
    #execution of instruction LT
    def lt(self, inst):

        #check if arguments are of correct type and get necessary values
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'int', 'var', 'string', 'bool'}, {'int', 'string', 'bool'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var', 'string', 'bool'}, {'int', 'string', 'bool'})

        #check if arguments are present
        if arg2_value is None or arg3_value is None:
            exit(56)
        
        #check if areguments are not nil
        if inst.arg2.type == 'nil' or inst.arg3.type == 'nil':
            exit(56)

        #check if arguments are of same type
        if self.get_type(inst.arg2) != self.get_type(inst.arg3):
            exit(53)

        #compare variable according to type
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
            arg2_value = self.string_replace(arg2_value)
        
        if inst.arg2.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
                arg3_value = self.string_replace(arg3_value)
        
        if inst.arg2.type != 'bool':
            to_assign = arg2_value < arg3_value
             
        to_assign = str(to_assign)
        to_assign = to_assign.lower()

        #assign value to variable
        self.assign(inst.arg1, to_assign, 'bool')

    #execution of instruction GT
    def gt(self, inst):

        #check if arguments are of correct type and get necessary values
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'int', 'var', 'string', 'bool'}, {'int', 'string', 'bool'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var', 'string', 'bool'}, {'int', 'string', 'bool'})

        #check if arguments are present
        if arg2_value is None or arg3_value is None:
            exit(56)
        
        #check if arguments are not nil
        if inst.arg2.type == 'nil' or inst.arg3.type == 'nil':
            exit(53)

        #check if arguments are of same type
        if self.get_type(inst.arg2) != self.get_type(inst.arg3):
            exit(53)

        #compare variable according to type
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
            arg2_value = self.string_replace(arg2_value)
        
        if inst.arg2.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
                arg3_value = self.string_replace(arg3_value)

        if inst.arg2.type != 'bool':
            to_assign = arg2_value > arg3_value
             
        to_assign = str(to_assign)
        to_assign = to_assign.lower()

        #assign value to variable
        self.assign(inst.arg1, to_assign, 'bool')

    def eq(self, inst):

        #check if arguments are of correct type and get necessary values
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'int', 'var', 'string', 'bool', 'nil'}, {'int', 'string', 'bool', 'nil'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var', 'string', 'bool', 'nil'}, {'int', 'string', 'bool', 'nil'})

        #check if arguments are present
        if arg2_value is None or arg3_value is None:
            exit(56)
        
        #check if arguments are of same type or nil
        if inst.arg2.type == 'nil' or inst.arg3.type == 'nil':
            if inst.arg2.value == 'nil' and inst.arg3.value == 'nil':
                to_assign = True
            else:
                to_assign = False
        else:
            if inst.arg2.type != inst.arg3.type:
                exit(53)

        #compare variable according to type
        if inst.arg2.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
            arg2_value = self.string_replace(arg2_value)
        
        if inst.arg3.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
                arg3_value = self.string_replace(arg3_value)

        to_assign = arg2_value == arg3_value
        to_assign = str(to_assign)
        to_assign = to_assign.lower()

        #assign value to variable
        self.assign(inst.arg1, to_assign, 'bool')

    #execution of instruction AND
    def and_(self, inst):

        #check if arguments are of correct type and get necessary values
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'bool', 'var'}, {'bool'})
        arg3_value = self.symb_check(inst.arg3, {'bool', 'var'}, {'bool'})

        #check if arguments are present
        if arg2_value is None or arg3_value is None:
            exit(56)
        
        #compare values
        if arg2_value == 'true' and arg3_value == 'true':
            to_assign = True
        else:
            to_assign = False
        
        to_assign = str(to_assign)
        to_assign = to_assign.lower()

        #assign value to variable
        self.assign(inst.arg1, to_assign, 'bool')
    
    #execution of instruction OR
    def or_(self, inst):

        #check if arguments are of correct type and get necessary values
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'bool', 'var'}, {'bool'})
        arg3_value = self.symb_check(inst.arg3, {'bool', 'var'}, {'bool'})

        #check if arguments are present
        if arg2_value is None or arg3_value is None:
            exit(56)
        
        #compare values
        if arg2_value == 'true' or arg3_value == 'true':
            to_assign = True
        else:
            to_assign = False
        
        to_assign = str(to_assign)
        to_assign = to_assign.lower()

        #assign value to variable
        self.assign(inst.arg1, to_assign, 'bool')
    
    #execution of instruction NOT
    def not_(self, inst):

        #check if arguments are of correct type and get necessary values
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'bool', 'var'}, {'bool'})

        #check if argument is present
        if arg2_value is None:
            exit(56)

        #negate value
        if arg2_value == 'true':
            to_assign = False
        else:
            to_assign = True

        to_assign = str(to_assign)
        to_assign = to_assign.lower()

        #assign value to variable
        self.assign(inst.arg1, to_assign, 'bool')

    #execution of instruction INT2CHAR
    def int2char(self, inst):

        #check if arguments are of correct type and get necessary values
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'int', 'var'}, {'int'})

        #check if argument is present
        if arg2_value is None:
            exit(56)

        #convert ordinal value to char
        try:
            to_assign = chr(int(arg2_value))
        except ValueError:
            exit(58)

        #assign value to variable
        self.assign(inst.arg1, to_assign, 'string')

    #execution of instruction STRI2INT
    def stri2int(self, inst):

        #check if arguments are of correct type and get necessary values
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'string', 'var'}, {'string'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var'}, {'int'})

        #edit replace escape sequences if necessary
        if inst.arg2.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
            arg2_value = self.string_replace(arg2_value)

        #check if arguments are present
        if arg2_value is None or arg3_value is None:
            exit(56)

        #check if index is in range of string
        if int(arg3_value) < 0 or int(arg3_value) >= len(arg2_value):
            exit(58)

        #convert char to ordinal value
        try:
            to_assign = ord(arg2_value[int(arg3_value)])
        except IndexError:
            exit(58)

        #assign value to variable
        self.assign(inst.arg1, to_assign, 'int')

    #execution of instruction READ
    def read(self, inst):

        #check if arguments are of correct type and get necessary values
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'type'}, None)

        #check if argument is present
        if arg2_value is None:
            exit(56)
        
        #read value according to type and input file
        if arg2_value == 'int':
            try:
                if I.input is not None:
                    to_assign = I.input.readline().rstrip()
                else:
                    to_assign = input()
            except EOFError or ValueError:
                to_assign = 'nil'
                arg2_value = 'nil'
        
        elif arg2_value == 'bool':
            try:
                if I.input is not None:
                    to_assign = I.input.readline().rstrip().lower()
                else:
                    to_assign = input().lower()

                if to_assign != 'true':
                    to_assign = 'false'
            except EOFError or ValueError:
                to_assign = 'nil'
                arg2_value = 'nil'
           
            if to_assign != 'nil':
                if to_assign == 'true':
                    to_assign = 'true'
                else:
                    to_assign = 'false'
        
        elif arg2_value == 'string':
            try:
                if I.input is not None:
                    to_assign = I.input.readline().rstrip()
                else:
                    to_assign = input()

            except EOFError or ValueError:
                to_assign = 'nil'
                arg2_value = 'nil'
            
            if to_assign != 'nil':
                to_assign = self.string_replace(to_assign)

        #assign value to variable
        self.assign(inst.arg1, to_assign, arg2_value)

    #execution of instruction WRITE
    def write(self, inst):

        #check if argument is of correct type and get necessary values
        arg1 = self.symb_check(inst.arg1, {'var', 'int', 'bool', 'string', 'nil'}, None)

        #check if argument is present
        if arg1 is None:
            exit(56)

        #replace escape sequences if necessary
        if inst.arg1.type == 'string':
            arg1 = self.string_replace(arg1)
        
        #check if value is nil
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
        
        #print value
        if inst.arg1.type in ["var","int", "bool", "string"]:
            print(arg1, end="")
        elif inst.arg1.type == "nil":
            print("", end="")
        else:
            exit(32)

    #execution of instruction CONCAT
    def concat(self, inst):

        #check if arguments are of correct type and get necessary values
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'string', 'var'}, {'string'})
        arg3_value = self.symb_check(inst.arg3, {'string', 'var'}, {'string'})

        #check if arguments are present
        if arg2_value is None or arg3_value is None:
            exit(56)

        #replace escape sequences if necessary
        if inst.arg2.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
            arg2_value = self.string_replace(arg2_value)
        if inst.arg3.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
            arg3_value = self.string_replace(arg3_value)

        #concatenate strings
        to_assign = arg2_value + arg3_value

        #assign value to variable
        self.assign(inst.arg1, to_assign, 'string')   

    #execution of instruction STRLEN
    def strlen(self, inst):

        #check if arguments are of correct type and get necessary values
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'string', 'var'}, {'string'})

        #check if argument is present
        if arg2_value is None:
            exit(56)

        #replace escape sequences if necessary
        if inst.arg2.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
            arg2_value = self.string_replace(arg2_value)

        #get length of string
        to_assign = len(arg2_value)

        #assign value to variable
        self.assign(inst.arg1, to_assign, 'int') 

    #execution of instruction GETCHAR
    def getchar(self, inst):

        #check if arguments are of correct type and get necessary values
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'string', 'var'}, {'string'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var'}, {'int'})

        #check if arguments are present
        if arg2_value is None or arg3_value is None:
            exit(56)
        
        #replace escape sequences if necessary
        if inst.arg2.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
            arg2_value = self.string_replace(arg2_value)

        #check if index is out of range
        if int(arg3_value) < 0 or int(arg3_value) >= len(arg2_value):
            exit(58)

        #get character from string
        to_assign = arg2_value[int(arg3_value)]

        #assign value to variable
        self.assign(inst.arg1, to_assign, 'string')
    
    #execution of instruction SETCHAR
    def setchar(self, inst):
        arg1_value = self.symb_check(inst.arg1, {'string', 'var'}, {'string'})
        arg2_value = self.symb_check(inst.arg2, {'int', 'var'}, {'int'})
        arg3_value = self.symb_check(inst.arg3, {'string', 'var'}, {'string'})

        #check if arguments are present
        if arg1_value is None or arg2_value is None or arg3_value is None:
            exit(56)

        #replace escape sequences if necessary
        if inst.arg1.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
            arg1_value = self.string_replace(arg1_value)
        if inst.arg3.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
            arg3_value = self.string_replace(arg3_value)

        #check if index is out of range
        if int(arg2_value) < 0 or int(arg2_value) >= len(arg1_value):
            exit(58)

        #check if string is empty
        if len(arg3_value) < 1:
            exit(58)

        #check if string is longer than 1 character
        if len (arg3_value) > 1:
            arg3_value = arg3_value[0]

        #set character in string
        to_assign = arg1_value[:int(arg2_value)] + arg3_value + arg1_value[int(arg2_value)+1:]

        #assign value to variable
        self.assign(inst.arg1, to_assign, 'string')

    #execution of instruction TYPE
    def type_(self, inst):

        #check if arguments are of correct type and get necessary values
        self.symb_check(inst.arg1, {'var'}, None)
        arg2_value = self.symb_check(inst.arg2, {'var', 'int', 'bool', 'string', 'nil'}, None)
        
        #check if argument is value is None, if so, assign empty string, else assign type of argument
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
        
        #assign value to variable
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

    #execution of instruction LABEL
    def jump(self, inst):
        #check if argument is of correct type and get necessary value
        arg1_value = self.symb_check(inst.arg1, {'label'}, None)

        #check if label is defined    
        if arg1_value not in self.labels:
            exit(52)
        
        #set instruction counter to label
        self.instruction_counter = self.labels[inst.arg1.value] - 1
    
    #execution of instruction JUMPIFEQ
    def jumpifeq(self, inst):

        #check if arguments are of correct type and get necessary values
        arg1_value = self.symb_check(inst.arg1, {'label'}, None)
        arg2_value = self.symb_check(inst.arg2, {'int', 'var', 'string', 'bool', 'nil'}, {'int', 'string', 'bool', 'nil'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var', 'string', 'bool', 'nil'}, {'int', 'string', 'bool', 'nil'})

        #check if arguments are present
        if arg2_value is None or arg3_value is None:
            exit(56)

        #check if label is defined
        if arg1_value not in self.labels:
            exit(52)
        
        #check if arguments are of same type or if one of them is nil
        if inst.arg2.type == 'nil' or inst.arg3.type == 'nil':
            if inst.arg2.value == 'nil' and inst.arg3.value == 'nil':
                value = True
            else:
                value = False
        else:
            if self.get_type(inst.arg2) != self.get_type(inst.arg3):
                exit(53)
        
        #replace escape sequences if necessary
        if inst.arg2.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
            arg2_value = self.string_replace(arg2_value)
        
        if inst.arg3.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
                arg3_value = self.string_replace(arg3_value)

        #check if arguments are equal
        value = str(arg2_value) == str(arg3_value)

        #set instruction counter to label if arguments are equal
        if value == True:
            self.instruction_counter = self.labels[inst.arg1.value] - 1

    #execution of instruction JUMPIFNEQ
    def jumpifneq(self, inst):

        #check if arguments are of correct type and get necessary values
        arg1_value = self.symb_check(inst.arg1, {'label'}, None)
        arg2_value = self.symb_check(inst.arg2, {'int', 'var', 'string', 'bool', 'nil'}, {'int', 'string', 'bool', 'nil', 'var'})
        arg3_value = self.symb_check(inst.arg3, {'int', 'var', 'string', 'bool', 'nil'}, {'int', 'string', 'bool', 'nil', 'var'})
        
        #check if arguments are present
        if arg2_value is None or arg3_value is None:
            exit(56)
        
        #check if label is defined
        if arg1_value not in self.labels:
            exit(52)
        
        #check if arguments are of same type or if one of them is nil
        if inst.arg2.type == 'nil' or inst.arg3.type == 'nil':
            if inst.arg2.value == 'nil' and inst.arg3.value == 'nil':
                value = True
            else:
                value = False
        else:
            if self.get_type(inst.arg2) != self.get_type(inst.arg3):
                exit(53)
        
        #replace escape sequences if necessary
        if inst.arg2.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
            arg2_value = self.string_replace(arg2_value)
        
        if inst.arg3.type == 'string' or (inst.arg3.type == 'var' and self.get_type(inst.arg3) == 'string'):
                arg3_value = self.string_replace(arg3_value)

        #check if arguments are equal
        value = str(arg2_value) == str(arg3_value)

        #set instruction counter to label if arguments are not equal
        if value == False:
            self.instruction_counter = self.labels[inst.arg1.value] - 1

    #execution of instruction EXIT
    def exit(self, inst):
        
        #check if argument is of correct type and get necessary value
        arg1_value = self.symb_check(inst.arg1, {'int', 'var'}, {'int'})
        
       #check if argument is present
        if arg1_value is None:
            exit(56)

        #check if argument is of correct value
        arg1_value = int(arg1_value)
        if arg1_value < 0 or arg1_value > 49:
            exit(57)

        #exit program with given exit code
        sys.exit(arg1_value)
    
    

if __name__ == '__main__':
    
    #create instance of Interpret class and run main method
    I = Interpret()
    I.main()
    




