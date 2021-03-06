from sys_db import system_database
from k4 import *
import requests
import json
import pandas as pd
import pprint
from coinMarketCap import crypto_category
import datetime

def get_json_data(url):
    req = requests.get(url=url)
    response_json = json.loads(req.text)
    return response_json

def pairs_tradeable(obj_json):
    coin_list = []
    for coin in obj_json:
        is_frozen = obj_json[coin]['isFrozen']
        isPost = obj_json[coin]['postOnly']
        if is_frozen == '0' and isPost == '0':
            # print(coin, is_frozen, isPost)
            coin_list.append(coin)
    return coin_list

def Tri_arb_pair_structure(coin_list: list):
    tri_pair_list = []
    remove_duplicate_pairs = []
    pairs_list = coin_list[1:10]
    # PAIR A
    for pair_a in pairs_list:
        pair_a_split = pair_a.split("_")
        a_base = pair_a[0]
        a_quote = pair_a[1]
        a_pair_box = [a_base, a_quote]
        # PAIR B
        for pair_b in pairs_list:
            pair_a_split = pair_b.split("_")
            b_base = pair_b[0]
            b_quote = pair_b[1]
            if pair_b != pair_a:
                if b_base in a_pair_box or a_pair_box:

                    #get pair c
                    for pair_c in pairs_list:
                        pair_c_split = pair_c.split("_")
                        c_base = pair_c[0]
                        c_quote = pair_c[1]
                        #same c items
                        if pair_c != pair_a and pair_c != pair_b:
                            combine_all = [pair_a, pair_b, pair_c]
                            pair_box = [a_base, a_quote, b_base, b_quote, c_base, c_quote]

                            count_c_base = 0
                            for i in pair_box:
                                if i == c_base:
                                    count_c_base += 1
                            count_c_quote = 0
                            for i in pair_box:
                                if i == c_quote:
                                    count_c_quote += 1


                            #tri_match? 2 matches in base or quote
                            if count_c_base == 2 and count_c_base == 2 and c_base != c_quote:
                                trades_combined = pair_a, pair_b, pair_c
                                unqine_pair = ''.join(sorted(combine_all))
                                # print(unqine_pair)
                                count_ = 0
                                if unqine_pair not in remove_duplicate_pairs:
                                    match_dic = {
                                        'a_base:': a_base,
                                        'b_base': b_base,
                                        'c_base': c_base,
                                        'a_quote:': a_quote,
                                        'b_quote': b_quote,
                                        'c_quote': c_quote,
                                        'pair_a': pair_a,
                                        'pair_b': pair_b,
                                        'pair_c': pair_c,
                                        'combined': trades_combined
                                                 }
                                    spec_dic = {'combined': trades_combined}
                                    # print(match_dic)
                                    tri_pair_list.append(match_dic)
                                    remove_duplicate_pairs.append(unqine_pair)
    df = pd.DataFrame(data=list(tri_pair_list))
    # print(df[0:10])
    # print(tri_pair_list[0:10])
    return tri_pair_list

            # return tri_pair_list

#structured prices
def get_price_t_pair(t_pair,prices_json):
    # extract pair information
    pair_a = t_pair["pair_a"]
    pair_b = t_pair["pair_b"]
    pair_c = t_pair["pair_c"]
    # extract price
    pair_a_ask = float(prices_json[pair_a]["lowestAsk"])
    pair_a_bid = float(prices_json[pair_a]["highestBid"])
    pair_b_ask = float(prices_json[pair_b]["lowestAsk"])
    pair_b_bid = float(prices_json[pair_b]["highestBid"])
    pair_c_ask = float(prices_json[pair_c]["lowestAsk"])
    pair_c_bid = float(prices_json[pair_c]["highestBid"])

    #output dic
    return {
        "pair_a_ask": pair_a_ask,
        "pair_a_bid": pair_a_bid,
        "pair_b_ask": pair_b_ask,
        "pair_b_bid": pair_b_bid,
        "pair_c_ask": pair_c_ask,
        "pair_c_bid": pair_c_bid
    }

# calucate sturface rate tri arb
def cal_tri_surface_rate(t_pair,prices_dict):
    starting_capital = 1
    min_surface_rate = 0
    surface_dict = {}
    contract_2 = ""
    contract_3 = ""
    direction_of_trade_1 = ""
    direction_of_trade_2 = ""
    direction_of_trade_3 = ""
    calculated = 0

    # extract pair variables
    t_p = t_pair["pair_a"][0]
    t_p1 = t_pair["pair_a"][1]
    t_p2 = t_pair["pair_a"][2]
    p0_q = t_pair["pair_a"][-3]
    p1_q = t_pair["pair_a"][-2]
    p2_q = t_pair["pair_a"][-1]

    t2_p = t_pair["pair_b"][0]
    t2_p1 = t_pair["pair_b"][1]
    t2_p2 = t_pair["pair_b"][2]
    p0_q2 = t_pair["pair_b"][-3]
    p1_q2 = t_pair["pair_b"][-2]
    p2_q2 = t_pair["pair_b"][-1]

    t3_p = t_pair["pair_b"][0]
    t3_p1 = t_pair["pair_b"][1]
    t3_p2 = t_pair["pair_b"][2]
    p0_q3 = t_pair["pair_b"][-3]
    p1_q3 = t_pair["pair_b"][-2]
    p2_q3 = t_pair["pair_b"][-1]


    a_base = f"{t_p}{t_p1}{t_p2}"
    a_quote = f"{p0_q}{p1_q}{p2_q}"
    b_base = f"{t2_p}{t2_p1}{t2_p2}"
    b_quote = f"{p0_q}{p1_q}{p2_q}"
    c_base = f"{t3_p}{t3_p1}{t3_p2}"
    c_quote = f"{p0_q3}{p1_q3}{p2_q3}"

    
    pair_a = t_pair["pair_a"]
    pair_b = t_pair["pair_b"]
    pair_c = t_pair["pair_c"]

    #extract prices
    a_ask = prices_dict["pair_a_ask"]
    a_bid = prices_dict["pair_a_bid"]
    b_ask = prices_dict["pair_b_ask"]
    b_bid = prices_dict["pair_b_bid"]
    c_ask = prices_dict["pair_c_ask"]
    c_bid = prices_dict["pair_c_bid"]


    # directions and loops to the right and left
    direction_list = ['forward','reverse']
    for direction in direction_list:
        # swap information variables for tracking
        # what rate to use in leg trade rate
        # swap = coin/token
        swap_1 = 0
        swap_rate_1 = 0
        swap_2 = 0
        swap_rate_2 = 0
        swap_3 = 0
        swap_rate_3 = 0

        '''
        TRADE DIRECTION 
        !! POLONIEX RULES !!
        if swaping coin left (base) to right (quote) then trading_capital (1 / lowest ask)
        if swaping coin right (quote) to left (base) then trading_capital * highestbid 
        !! !!
        '''

        """
        >> THEORY: ASSUMING STARTING WITH a_base & a_quote <<
        """

        #
        # ESTABLISH BASE & QUOTE POSITIONS WITH RESPECT TO
        # DIRECTIONS
        if direction == 'forward':
            swap_1 = a_base
            swap_2 = a_quote
            swap_rate_1 = 1 /a_ask
            direction_of_trade_1 = "base_to_quote"
        if direction == 'reverse':
            swap_1 = a_quote
            swap_2 = a_base
            swap_rate_1 = a_bid * starting_capital
            direction_of_trade_1 = "quote_to_base"

        contract_1 = pair_a

        token_holdings_t1 = starting_capital * swap_rate_1

        '''
                        TEST CASES

        '''

        """forward"""

        '''
        CASE 1
        '''
        # CASE 1: check if a_quote (token holding) matches b_quote
        if direction == 'forward':
            if a_quote == b_quote and calculated == 0:
                swap_rate_2 = b_bid
                token_holdings_t2 = token_holdings_t1 * swap_rate_2
                direction_of_trade_2 = 'quote_to_base'
                contract_2 = pair_b

                # if b_base (token_holding_2) == c_base
                if b_base == c_base:
                    swap_3 = c_base
                    swap_rate_3 = 1/c_ask
                    direction_of_trade_3 = 'base_to_quote'
                    contract_3 = pair_c
                # if b_base (token_holding_2) == c_quote
                if b_base == c_quote:
                    swap_3 = c_quote
                    swap_rate_3 = c_bid
                    direction_of_trade_3 = 'quote_to_base'
                    contract_3 = pair_c
                token_holdings_t3 = token_holdings_t2 * swap_rate_2
                calculated = 1

        """
        
        CASE 2
        
        
        """
        # check if a_quote (token holding) matches b_base
        if direction == 'forward':
                if a_quote == b_base and calculated == 0:
                    swap_rate_2 = 1 / b_ask
                    token_holdings_t2 = token_holdings_t1 * swap_rate_2
                    direction_of_trade_2 = 'base_to_quote'
                    contract_2 = pair_b

                    # if b_quote (token_holding_2) == c_base
                    if b_quote == c_base:
                        swap_3 = c_base
                        swap_rate_3 = 1 / c_ask
                        direction_of_trade_3 = 'base_to_quote'
                        contract_3 = pair_c
                    # if b_quote (token_holding_2) == c_quote
                    if b_quote == c_quote:
                        swap_3 = c_quote
                        swap_rate_3 = c_bid
                        direction_of_trade_3 = 'quote_to_base'
                        contract_3 = pair_c
                    token_holdings_t3 = token_holdings_t2 * swap_rate_2
                    calculated = 1
        '''
        
        CASE 3
        
        '''
        # check if a_quote (token holding) matches c_quote
        if direction == 'forward':
            if a_quote == c_quote and calculated == 0:
                swap_rate_2 = c_bid
                token_holdings_t2 = token_holdings_t1 * swap_rate_2
                direction_of_trade_2 = 'quote_to_base'
                contract_2 = pair_c

                # if c_base (token_holding_2) == b_base
                if c_base == b_base:
                    swap_3 = b_base
                    swap_rate_3 = 1/b_ask
                    direction_of_trade_3 = 'base_to_quote'
                    contract_3 = pair_b
                # if c_base (token_holding_2) == b_quote
                if c_base == b_quote:
                    swap_3 = b_quote
                    swap_rate_3 = b_bid
                    direction_of_trade_3 = 'quote_to_base'
                    contract_3 = pair_b
                token_holdings_t3 = token_holdings_t2 * swap_rate_2
                calculated = 1

        """
        
        CASE 4
        
        """

        # check if a_quote (token holding) matches c_base
        if direction == 'forward':
                if a_quote == c_base and calculated == 0:
                    swap_rate_2 = 1 / c_ask
                    token_holdings_t2 = token_holdings_t1 * swap_rate_2
                    direction_of_trade_2 = 'base_to_quote'
                    contract_2 = pair_c

                # if c_quote (token_holding_2) == b_base
                    if c_quote == b_base:
                        swap_3 = b_base
                        swap_rate_3 = 1 / b_ask
                        direction_of_trade_3 = 'base_to_quote'
                        contract_3 = pair_b

                # if c_quote (token_holding_2) == b_quote
                    if b_quote == c_quote:
                        swap_3 = b_quote
                        swap_rate_3 = c_bid
                        direction_of_trade_3 = 'quote_to_base'
                        contract_3 = pair_b

                    token_holdings_t3 = token_holdings_t2 * swap_rate_2
                    calculated = 1

                """REVERSE"""

                '''
                CASE 1
                '''
                # CASE 1: check if a_base (token holding) matches b_quote
        if direction == 'reverse':
                if a_base == b_quote and calculated == 0:
                    swap_rate_2 = b_bid
                    token_holdings_t2 = token_holdings_t1 * swap_rate_2
                    direction_of_trade_2 = 'quote_to_base'
                    contract_2 = pair_b

                    # if b_base (token_holding_2) == c_base
                    if b_base == c_base:
                            swap_3 = c_base
                            swap_rate_3 = 1 / c_ask
                            direction_of_trade_3 = 'base_to_quote'
                            contract_3 = pair_c
                        # if b_base (token_holding_2) == c_quote
                    if b_base == c_quote:
                                swap_3 = c_quote
                                swap_rate_3 = c_bid
                                direction_of_trade_3 = 'quote_to_base'
                                contract_3 = pair_c
                    token_holdings_t3 = token_holdings_t2 * swap_rate_2
                    calculated = 1

                """

                CASE 2


                """
                # check if a_base (token holding) matches b_base
        if direction == 'reverse':
                if a_base == b_base and calculated == 0:
                        swap_rate_2 = 1 / b_ask
                        token_holdings_t2 = token_holdings_t1 * swap_rate_2
                        direction_of_trade_2 = 'base_to_quote'
                        contract_2 = pair_b

                        # if b_quote (token_holding_2) == c_base
                        if b_quote == c_base:
                            swap_3 = c_base
                            swap_rate_3 = 1 / c_ask
                            direction_of_trade_3 = 'base_to_quote'
                            contract_3 = pair_c
                        # if b_quote (token_holding_2) == c_quote
                        if b_quote == c_quote:
                            swap_3 = c_quote
                            swap_rate_3 = c_bid
                            direction_of_trade_3 = 'quote_to_base'
                            contract_3 = pair_c
                        token_holdings_t3 = token_holdings_t2 * swap_rate_2
                        calculated = 1
                '''

                CASE 3

                '''
                # check if a_base (token holding) matches c_quote
        if direction == 'reverse':
                if a_base == c_quote and calculated == 0:
                        swap_rate_2 = c_bid
                        token_holdings_t2 = token_holdings_t1 * swap_rate_2
                        direction_of_trade_2 = 'quote_to_base'
                        contract_2 = pair_c

                        # if c_base (token_holding_2) == b_base
                        if c_base == b_base:
                            swap_3 = b_base
                            swap_rate_3 = 1 / b_ask
                            direction_of_trade_3 = 'base_to_quote'
                            contract_3 = pair_b
                        # if c_base (token_holding_2) == b_quote
                        if c_base == b_quote:
                            swap_3 = b_quote
                            swap_rate_3 = b_bid
                            direction_of_trade_3 = 'quote_to_base'
                            contract_3 = pair_b
                        token_holdings_t3 = token_holdings_t2 * swap_rate_2
                        calculated = 1

                """

                CASE 4

                """

                # check if a_base (token holding) matches c_base
        if direction == 'reverse':
            if a_base == c_base and calculated == 0:
                        swap_rate_2 = 1 / c_ask
                        token_holdings_t2 = token_holdings_t1 * swap_rate_2
                        direction_of_trade_2 = 'base_to_quote'
                        contract_2 = pair_c

                        # if c_quote (token_holding_2) == b_base
                        if c_quote == b_base:
                            swap_3 = b_base
                            swap_rate_3 = 1 / b_ask
                            direction_of_trade_3 = 'base_to_quote'
                            contract_3 = pair_b

                        # if c_quote (token_holding_2) == b_quote
                        if b_quote == c_quote:
                            swap_3 = b_quote
                            swap_rate_3 = c_bid
                            direction_of_trade_3 = 'quote_to_base'
                            contract_3 = pair_b

                        token_holdings_t3 = token_holdings_t2 * swap_rate_2
                        calculated = 1


            '''
            PNL OUTPUT
            '''
            #PNL INFO
            PNL = token_holdings_t3 - starting_capital
            PNL_percentage = (PNL/starting_capital)*100 if PNL != 0 else 0

            # TRADE INFO
            describtion_t1 = f'Start with {starting_capital} of {swap_1}. ' \
                             f'\nSwap at {swap_rate_1} for  {swap_2} GETTING {token_holdings_t1}' \
                             f'\n PAIR: {pair_a}' \
                             f'\n{direction_of_trade_1}'
            describtion_t2 = f'Swap {token_holdings_t1} of {swap_2} for {swap_3} at {float(int(swap_rate_2))} getting {token_holdings_t2}' \
                             f'\n PAIR: {pair_b}' \
                             f'\n{direction_of_trade_2}'
            describtion_t3 = f'Swap {token_holdings_t2} of {swap_1} at {swap_rate_3} getting {token_holdings_t3}' \
                             f'\n PAIR: {pair_c}' \
                             f'\n{direction_of_trade_3}'

            print("        -            >>>>>        PNL         <<<<<            -       ")
            print(describtion_t1)
            print(describtion_t2)
            print(describtion_t3)
            print('------------------------------------------------------------------')













