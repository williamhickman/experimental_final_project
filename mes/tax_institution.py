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
        self.environment_address = message.get_sender() #saves the environment address 
        init_dict = message.get_payload()
        #self.log_data(f"The environment says that the number of agents is {init_dict['number_of_agents']}")
        self.number_of_rounds = init_dict['number_of_rounds']
        self.number_of_agents = init_dict['number_of_agents']
        self.tax_rate = init_dict['tax_rate']
        self.payment_per_task = init_dict['payment_per_task']
        self.round_id=0
        #self.log_data(f"Number of rounds is {self.number_of_rounds}. Number of agents is {self.number_of_agents}. Tax rate is {self.tax_rate}. Payment per task is {self.payment_per_task}")
        self.send_message("institution_confirm_init", "Environment", None, True)
    
    @directive_decorator("start_round")
    def start_round(self, message: Message):
        self.agent_addresses = message.get_payload()
        self.address_book.merge_addresses(self.agent_addresses)
        if self.round_id >= 0 & self.round_id<self.number_of_rounds:
            self.round_id += 1
            print(f"INSTITUTION: Starting Round {self.round_id}")
            for agent_id in self.address_book:
                self.send_message("start_round", agent_id, self.round_id, False)
        else:
            complete_experiment()
        

    @directive_decorator("request_random_output")
    def request_random_output(self, message: Message):
        agent_id = message.get_payload() #saves the agent short_name 
        self.log_message(f"Random output requested by {agent_id}")
        self.random_output=self.select_random_output()
        self.send_message("receive_random_output", agent_id, self.random_output, False)
  
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

    def calculate_posttax_earnings(self):
        self.total_taxes_collected = []
        self.taxes_collected_this_round=[]
        for agent_output, self.round_id in self.effort_history:
            self.taxes_collected_this_round.append(agent_output*self.tax_rate)
        self.tax_in_round=sum(self.taxes_collected_this_round)
        self.sent_back_to_each_participant=self.tax_in_round/self.number_of_agents    
        self.send_posttax_earnings_to_agents()
       # need to add more here. add up all taxes paid by each agent in each round, then distribute this amount evenly to all the agents

    def send_posttax_earnings_to_agents(self):
        for agent_output, agent_id, self.round_id in self.effort_history:
            self.send_message("receive_posttax_earnings", agent_id, (agent_output*self.payment_per_task+self.sent_back_to_each_participant) , False)
        self.log_data("ROUND COMPLETE")


    
    def complete_experiment(self):
        self.shutdown_mes()

   