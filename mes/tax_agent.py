from tkinter.filedialog import askdirectory
from mTree.microeconomic_system.environment import Environment
from mTree.microeconomic_system.institution import Institution
from mTree.microeconomic_system.agent import Agent
from mTree.microeconomic_system.directive_decorators import *
from mTree.microeconomic_system.message import Message
import importlib
import math
import random
import logging
import time
import datetime

#TODO: make a directive to accept request_standing reminder message
@directive_enabled_class
class TaxAgent(Agent):
    def __init__(self):
        self.my_id = None      
        self.institution_address = None
        self.environment_address = None
        self.agent_dict = None
        self.effort_history = []
        self.pretax_history= []
        self.posttax_history= []

    def send_message(self, directive, receiver, payload, use_env):
        """Sends message
           use_env = True has method use environment address """
        new_message = Message()
        new_message.set_sender(self.myAddress)
        new_message.set_directive(directive)
        new_message.set_payload(payload)
        if use_env:
            receiver = "Environment"
            receiver_address = self.environment_address
        else:
            receiver_address = self.institution_address
        self.log_message(
            f"...<A>.. Message {directive} .. {payload}") 
        self.send(receiver_address, new_message)


    @directive_decorator("init_agent")
    def init_agent(self, message: Message):
        self.environment_address = message.get_sender() 
        payload = message.get_payload()
        self.my_id = payload['id']
        self.tax_rate=payload['tax_rate']
        self.payment_per_task=payload['payment_per_task']
        self.send_message("agent_confirm_init", "Environment", None, True)

    @directive_decorator("start_round")
    def start_round(self, message: Message):
        self.institution_address = message.get_sender()
        self.round_id = message.get_payload()
        self.send_message(f"agent_confirm_start_round_{self.round_id}", "Environment",self.short_name, True)
        if round_id == 1:
            self.choose_effort()
        # add in an else statement for all rounds other than the first
        
    @directive_decorator("choose_effort")
    def choose_effort(self, message: Message):
        self.send_message("request_random_output", "Institution", self.short_name, False)

    @directive_decorator("receive_random_output")
    def receive_random_output(self, message: Message):
        self.random_output= message.get_payload()
        self.send_message("agent_send_output_to_institution", "Institution", self.random_output, True)

    @directive_decorator("receive_post_tax_earnings")
    def receive_post_tax_earnings(self, message: Message):
         self.posttax_earnings= message.get_payload()
         self.posttax_history.append(self.posttax_earnings, self.round_id)
         

    

                  
    
    
    @directive_decorator("end_round")
    def end_round(self, message: Message):
        """
        Informs agents the round has ended and no further offers can be made.

        Messages Handled :
        - standing
            sender: Insitution
            payload: None
        """
        pass
