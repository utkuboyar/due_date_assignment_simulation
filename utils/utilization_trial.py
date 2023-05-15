
import numpy as np
from env_variables import *



class Utilization(object):

        
    def ro(prod_type):
        
        arr_rate = None # düzelt OrderParameters.get_interarrivals()
        unit_process = ProductParameters.get_params(check= -1) # return edilen ilk liste
        product_probs = ProductParameters.get_probs()
        cust_probs = CustomerParameters.get_probs()
        quantity_dict = OrderParameters.get_quantity_dist()
        
        arr_rate_prod = arr_rate*product_probs[prod_type]
#         arr_rate_1 = arr_rate*product_probs[1]
#         arr_rate_2 = arr_rate*product_probs[2]

        # service rate of product i  =  1 / expected process time of product i
        
        quantity_cust0 = [value for key, value in quantity_dict.items() if key == (prod_type, 0)][0][0]
        quantity_cust1 = [value for key, value in quantity_dict.items() if key == (prod_type, 1)][0][0]
        avg_quantity = cust_probs[0]*quantity_cust0 + cust_probs[1]*quantity_cust1
        mean_unit_process = unit_process[prod_type][0] + unit_process[prod_type][1]/2
        
        serv_rate = 1 / (avg_quantity * mean_unit_process_0)
    
        return arr_rate_prod/serv_rate

        
#         quantity_1_0 = [value for key, value in quantity_dict.items() if key == (1, 0)][0][0]
#         quantity_1_1 = [value for key, value in quantity_dict.items() if key == (1, 1)][0][0]
#         avg_quantity_1 = cust_probs[0]*quantity_1_0 + cust_probs[1]*quantity_1_1        
#         mean_unit_process_1 = unit_process[1][0] + unit_process[1][1]/2
        
#         serv_rate_1 = 1 / (avg_quantity_1 * mean_unit_process_1)    
        
        
#         quantity_2_0 = [value for key, value in quantity_dict.items() if key == (2, 0)][0][0]
#         quantity_2_1 = [value for key, value in quantity_dict.items() if key == (2, 1)][0][0]
#         avg_quantity_2 = cust_probs[0]*quantity_2_0 + cust_probs[1]*quantity_2_1        
#         mean_unit_process_2 = unit_process[2][0] + unit_process[2][1]/2
        
#         serv_rate_2 = 1 / (avg_quantity_2 * mean_unit_process_2)       
        
        
#         ro_0 = arr_rate_0 / serv_rate_0
#         ro_1 = arr_rate_1 / serv_rate_1
#         ro_2 = arr_rate_2 / serv_rate_2