import pipeline_register as pr

#a class to simulate the control unit 
class ControlUnit:
    
    def __init__(self):
        self.RegDst:str = '0'
        self.ALUSrc:str = '0'
        self.Branch:str = '0'
        self.MemRead:str = '0'
        self.MemWrite:str = '0'
        self.RegWrite:str = '0'
        self.MemToReg:str = '0'

    def set_control_signals(self, instruction):
        if instruction == 'lw':
            self.ALUSrc = '1'
            self.MemRead = '1'
            self.RegWrite = '1'
            self.MemToReg = '1'
        elif instruction == 'sw':
            self.RegDst = 'X'
            self.MemToReg = 'X'
            self.ALUSrc = '1'
            self.MemWrite = '1'
        elif instruction == 'add':
            self.RegDst = '1'
            self.RegWrite ='1'
        elif instruction == 'sub':
            self.RegDst = '1'
            self.RegWrite = '1'
        elif instruction == 'beq':
            self.Branch = '1'
            self.RegDst = 'X'
            self.MemToReg = 'X'
    def clear_control_signals(self):
        self.RegDst = '0'
        self.ALUSrc = '0'
        self.Branch = '0'
        self.MemRead = '0'
        self.MemWrite = '0'
        self.RegWrite = '0'
        self.MemToReg = '0'

    def get_control_signals(self):
        return {'RegDst':self.RegDst,'ALUSrc':self.ALUSrc, 'Branch':self.Branch, 'MemRead':self.MemRead, 'MemWrite':self.MemWrite, 'RegWrite':self.RegWrite, 'MemToReg':self.MemToReg}
        

#a class to simulate the hazard detection unit
#check if the instruction need to be stall (lw, sw, beq)
#check the last and second last instruction in the pipeline
#check fowarding
#check if the instruction need to be stall (lw, sw, beq)
#check the last and second last instruction in the pipeline
class HazardDetectionUnit:
    
    def __init__(self):
        self.ins_name = ''
        self.second_last_name = ''
        self.next_name = ''
        self.rt = ''
        self.rs = ''
        self.next_rs = ''
        self.next_rt = ''
        self.last_rd = ''
        self.second_last_rt = ''
    #----new def----------
    def set_lw_sw(self, this_instruction:pr.PipelineRegister, next_instruction:pr.PipelineRegister):
        self.ins_name = this_instruction.get_name()
        self.next_name = next_instruction.get_name()
        self.rt = this_instruction.get_one_register('rt')
        self.next_rs = next_instruction.get_one_register('rs')
        self.next_rt = next_instruction.get_one_register('rt')

    def set_beq(self, this_instruction:pr.PipelineRegister, last_instruction:pr.PipelineRegister, second_last_instruction:pr.PipelineRegister):
        
        self.second_last_name = second_last_instruction.get_name()
        self.rs = this_instruction.get_one_register('rs')
        self.rt = this_instruction.get_one_register('rt')
        self.last_rd = last_instruction.get_one_register('rd')
        self.second_last_rt = second_last_instruction.get_one_register('rt')
    #just check if the instruction need to be stall
    def checkHazard_lw_sw(self):
        if(self.ins_name == 'lw' and self.rt == self.next_rs):
            return True
        elif(self.ins_name == 'lw' and self.rt == self.next_rt and (self.next_name != 'lw' or self.next_name != 'sw')):
            return True
        else:
            return False
        
    def checkHazard_beq(self):
        if(self.rs == self.last_rd or self.rt == self.last_rd):
            return True
        elif self.second_last_name == 'lw' and (self.rs == self.second_last_rt or self.rt == self.second_last_rt):
            return True
        else:
            return False



class ForwardingUnit:
    #in ID stage

    def __init__(self):
        self.ins_name = ''
        self.last_name = ''
        self.second_last_name = ''
        self.rt = ''
        self.rs = ''
        self.last_rd = ''
        self.last_rt = ''
        self.second_last_rd = ''
        self.second_last_rt = ''
        self.forwarding_type =''

        self.rs_value = ''
        self.rt_value = ''
        self.last_data = ''
        self.second_last_data = ''
    
    
    def set(self, this_instruction:pr.PipelineRegister, last_instruction:pr.PipelineRegister, second_last_instruction:pr.PipelineRegister,rs_value,rt_value):
        self.ins_name = this_instruction.get_name()
        self.rt = this_instruction.get_one_register('rt')
        self.rs = this_instruction.get_one_register('rs')
        self.last_rd = last_instruction.get_one_register('rd')
        self.last_rt = last_instruction.get_one_register('rt')
        self.second_last_rd = second_last_instruction.get_one_register('rd')
        self.second_last_rt = second_last_instruction.get_one_register('rt')
        self.last_data = last_instruction.get_data()
        self.second_last_data = second_last_instruction.get_data()
        self.rs_value=rs_value
        self.rt_value=rt_value

    
    def set_sw(self, this_instruction:pr.PipelineRegister, last_instruction:pr.PipelineRegister,rt_value):
        self.this_name = this_instruction.get_name() #if this is sw
        self.rt = this_instruction.get_one_register('rt')
        self.last_rd = last_instruction.get_one_register('rd')
        self.rt_value = rt_value
        self.last_data = last_instruction.get_data()
    def checkForwarding(self, ALUSrc):
    #check rd is the same as ID/EX.rt or ID/EX.rs and EX/MEM.rt or EX/MEM.rs
    #if yes then forward(replace the value of the register with the value in the pipeline register)
    
        #R-format
        #forwarding type:(EX_rt:從EX/MEM讀取data給rt,EX_rs:從EX/MEM讀取data給rs, MEM_rt:從MEM/WB讀取data給rt, MEM_rs:從MEM/WB讀取data給rs)
        if ALUSrc == '0':
            #rt
            if(self.rt==self.last_rd):   #EX hazrad
                self.rt_value = self.last_data
            elif(self.rt==self.second_last_rd):     #MEM hazrad(R-format)
                self.rt_value = self.second_last_data
            elif(self.rt==self.second_last_rt and self.second_last_rd == ''):#MEM hazrad(I-format)
                self.rt_value = self.second_last_data
            
            #rs
            if(self.rs==self.last_rd):  #EX hazrad
                self.rs_value = self.last_data
            elif(self.rs==self.second_last_rd): #MEM hazrad(R-format)
                self.rs_value = self.second_last_data
            elif(self.rs==self.second_last_rt and self.second_last_rd == ''):    #MEM hazrad(I-format)
                self.rs_value = self.second_last_data
            
       

    def checkForwarding_branch(self):
        #rt
        if(self.rt==self.last_rd):   #EX hazrad
             self.rt_value = self.last_data
        elif(self.rt==self.second_last_rd):     #MEM hazrad(R-format)
                self.rt_value = self.second_last_data
        elif(self.rt==self.second_last_rt and self.second_last_rd == ''):#MEM hazrad(I-format)
                self.rt_value = self.second_last_data
            
        #rs
        if(self.rs==self.last_rd):  #EX hazrad
            self.rs_value = self.last_data
        elif(self.rs==self.second_last_rd): #MEM hazrad(R-format)
            self.rs_value = self.second_last_data
        elif(self.rs==self.second_last_rt and self.second_last_rd == ''):    #MEM hazrad(I-format)
            self.rs_value = self.second_last_data

    def get_rt_value(self):
        return self.rt_value

    def get_rs_value(self):
        return self.rs_value
        
    def checkForwarding_sw(self):
        if (self.this_name == 'sw' and self.last_rd == self.rt):
            
            self.rt_value = self.last_data
            
        return self.rt_value
    
    def clear(self):
        self.ins_name = ''
        self.last_name = ''
        self.second_last_name = ''
        self.rt = ''
        self.rs = ''
        self.last_rd = ''
        self.last_rt = ''
        self.second_last_rd = ''
        self.second_last_rt = ''
        self.forwarding_type =''
        self.rs_value = ''
        self.rt_value = ''
        self.last_data = ''
        self.second_last_data = ''