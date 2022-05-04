from mTree.microeconomic_system.environment import Environment
from mTree.microeconomic_system.institution import Institution
from mTree.microeconomic_system.agent import Agent
from mTree.microeconomic_system.directive_decorators import *
from mTree.microeconomic_system.message import Message
import math
import random
import logging
import time
import datetime

@directive_enabled_class
class TaxInstitution(Institution):
    
    def __init__(self):
        self.environment_address = None
        self.agents = None
        self.number_of_rounds = None
        self.agent_id = None
        self.effort_history = []
        self.pretax_history= []
        self.posttax_history= []
        self.round_id=[]
        self.number_of_agents= None


    def send_message(self, directive, receiver, payload, use_env = False):
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
            receiver_address = self.address_book.select_addresses(
                               {"short_name": receiver})
        self.log_message(
            f"..<M>..Message {directive} from Institution sent to {receiver}") 
        self.send(receiver_address, new_message)


    @directive_decorator("init_institution")
    def init_institution(self, message: Message):
        """
        Messages Handled :
        - init_institution
            sender: Environment 
            payload: dict = {'starting_bid': int, 'starting_ask': int}

        Messages Sent: 
        - institution_confirm_init
            receiver: Environment, 
            payload:  None
        """
        self.environment_address = message.get_sender() #saves the environment address 
        init_dict = message.get_payload()
        self.number_of_rounds = init_dict['number_of_rounds']
        self.number_of_agents = init_dict['number_of_agents']
        self.tax_rate = init_dict['tax_rate']
        self.payment_per_task = init_dict['payment_per_task']
        self.random_output = self.select_random_output()

        self.send_message("institution_confirm_init", "Environment", None, True)
    
    @directive_decorator("start_round")
    def start_round(self, message: Message):
        if self.round_id > 0:
            self.round_id -= 1
            print(f"INSTITUTION: Starting Round {self.round_id}")
            for agent_id in self.address_book.get_addresses():
                self.send_message("start_round", agent, self.round_id, False)
            elif:
                self.round_id == self.number_of_rounds:
                    self.complete_experiment()
        

    @directive_decorator("request_random_output")
    def request_random_output(self, message: Message):
        agent_id = message.get_payload() #saves the agent short_name 
        self.log_message(f"Random output requested by {agent_id}")
        self.send_message("receive_random_output", agent_id, self.random_output, False)
  
   
    @directive_decorator("select_random_output")
    def select_random_output(self, message: Message):
        self.random_output=random.randint(0, 100)

    @directive_decorator("agent_send_output_to_institution")
    def agent_send_output_to_institution(self, message: Message):
        agent_id = message.get_sender()
        agent_output = message.get_payload()
        self.effort_history.append((agent_output, agent_id, self.round_id))
        self.pretax_history.append((agent_output*self.payment_per_task, agent_id, self.round_id))
        if len(self.effort_history) == self.number_of_agents:
            self.log_data("ROUND COMPLETE")
            self.calculate_posttax_earnings()
            self.start_round()
            else:
                self.log_data("ROUND INCOMPLETE. WAITING FOR MORE OUTPUTS.")

    
        
    @directive_decorator("calculate_posttax_earnings")
    def calculate_posttax_earnings(self, message: Message):
        self.total_taxes_collected = []
        self.taxes_collected_this_round=[]
        for agent_output, self.round_id in self.effort_history:
            self.taxes_collected_this_round.append(agent_output*self.tax_rate)
        self.tax_in_round=self.total_taxes_collected.append(sum(taxes_collected_this_round), self.round_id))
        self.sent_back_to_each_participant=self.tax_in_round/self.number_of_agents    
        self.send_posttax_earnings_to_agents()
       # need to add more here. add up all taxes paid by each agent in each round, then distribute this amount evenly to all the agents

    @directive_decorator("send_posttax_earnings_to_agents")
    def send_posttax_earnings_to_agents(self, message: Message):
        for agent_output, agent_id, self.round_id in self.pretax_history:
            self.send_message("receive_posttax_earnings", agent_id, (agent_output*self.payment_per_task+self.sent_back_to_each_participant) , False)
        self.log_data("ROUND COMPLETE")
        self.complete_round()

    @directive_decorator("complete_round")
    def complete_round(self, message: Message):
        self.start_round()

    @directive_decorator("end_period")
    def end_period(self, message: Message):
        pass

   