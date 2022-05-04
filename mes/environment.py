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
class TaxEnvironment(Environment):
    def __init__(self):
        self.tax_rates = [0.0,0.25,0.5,0.75,1.0]

    def send_message(self, directive, receiver, payload):
        """Sends message"""
        new_message = Message()
        new_message.set_sender(self.myAddress)
        new_message.set_directive(directive)
        new_message.set_payload(payload)
        self.log_message(
            f"Message {directive} from Environment sent to {receiver}")
        receiver_address = self.address_book.select_addresses(
            {"short_name": receiver})
        self.send(receiver_address, new_message)

    @directive_decorator("start_environment")
    def start_environment(self, message: Message):
        # get the number of rounds from the config file
        self.number_of_rounds = self.get_property("number_of_rounds")
        self.number_of_agents = self.get_property("number_of_agents")
        self.payment_per_task = self.get_property("payment_per_task")
        self.choose_tax_rate()
        self.log_data(f"The selected tax rate is {self.tax_rate}")
        self.shutdown_mes()
        institution_payload = {'number_of_rounds': self.number_of_rounds,
                                 'number_of_agents': self.number_of_agents,
                                 'tax_rate': self.tax_rate,
                                 'payment_per_task':self.payment_per_task}
        self.send_message("init_institution", 
                          "institution.TaxInstitution 1",
                           institution_payload)
        self.send_message("environment_confirm_init","Environment",None)


    @directive_decorator("choose_tax_rate")
    def choose_tax_rate(self, message: Message):
        # randomly select a tax rate from a list of tax rates
        self.tax_rate = random.choice(self.tax_rates)
    

    """@directive_decorator("report_previous_round")
    def report_previous_round(self, message: Message):
        previous_output= random.randint(0,100)
        for agent in self.agent_addresses:
            new_message = Message()  
            new_message.set_sender(self.myAddress) 
            new_message.set_directive("set_endowment") 
            # to do: add the previous output to the payload
            new_message.set_payload("previous_output": )
            self.send(agent, new_message )""" 


    @directive_decorator("env_end_period")
    def env_end_period(self, message: Message):
        self.shutdown_mes()


    @directive_decorator("institution_confirm_init")
    def institution_confirm_init(self, message: Message):

        agent_payload = {"id": 1, "tax_rate": self.state['tax_rate'], "payment_per_task": self.state['payment_per_task']}
        self.send_message("init_agent", "agent.TaxAgent 1",
                           agent_payload)

        agent_payload = {"id": 2, "tax_rate": self.state['tax_rate'], "payment_per_task": self.state['payment_per_task']}
        self.send_message("init_agent", "agent.TaxAgent 2",
                           agent_payload)
        
        agent_payload = {"id": 3, "tax_rate": self.state['tax_rate'], "payment_per_task": self.state['payment_per_task']}
        self.send_message("init_agent", "agent.TaxAgent 3",
                           agent_payload)

        agent_payload = {"id": 4, "tax_rate": self.state['tax_rate'], "payment_per_task": self.state['payment_per_task']}
        self.send_message("init_agent", "agent.TaxAgent 4",
                           agent_payload)

        agent_payload = {"id": 5, "tax_rate": self.state['tax_rate'], "payment_per_task": self.state['payment_per_task']}
        self.send_message("init_agent", "agent.TaxAgent 5",
                           agent_payload)



    @directive_decorator("agent_confirm_init")
    def agent_confirm_init(self, message: Message):
        """
        Receives confirmation from the agents that they are finished initializing. 
        """
        self.agents_ready += 1
        if self.agents_ready == self.number_of_agents:
            self.agents_ready = 0
            self.log_message(f"agents confirmed")
            payload = self.address_book.get_agents()
            self.send_message("start_round", 
                              "institution.TaxInstitution 1",
                               payload)

@directive_decorator("env_end_period")
def env_end_period(self, message: Message):
    self.shutdown_mes()