
import json
import random
deck_dictionary_main = {}
deck_dictionary_whole = {}
deck_list_clean = []

def parser(decklist, mode):
    # might need 2 parser functions for whole and only main. or make a mode switch
    # add to local then overwrite real if valid
    # categorize on creation? should leave it to 
    global deck_dictionary_whole, deck_dictionary_main
    if mode == 'whole':
        local_dict_whole = {}
        for i in range(len(decklist)-1):
            if decklist[i][0].isnumeric():
                local_dict_whole[decklist[i][2:]] = int(decklist[i][0])
        # check if valid
        #print(local_dict_whole)
        if local_dict_whole != {}:
            deck_dictionary_whole.clear()
            deck_dictionary_whole = local_dict_whole.copy()
            return 1
        else:
            return 0
    elif mode == 'main':
        local_dict_main = {}
        for i in range(len(decklist)-1):
            if decklist[i] == 'Extra':
                # only add main deck
                break
            elif decklist[i][0].isnumeric():
                local_dict_main[decklist[i][2:]] = int(decklist[i][0])
        # return correct dictionary
        if local_dict_main != {}:
            deck_dictionary_main.clear()
            deck_dictionary_main  = local_dict_main.copy()
            return 1
        else:
            return 0


def validate_json(input_json):
    check_1 = ['Engine', 'Non-Engine', '']
    check_2 = ['Starter', 'Extender', 'Defensive', 'Offensive', 'Garnet', 'Consistency', '']
    for value in input_json.values():
        if value[0] > 3:
            return False
        elif value[1] not in check_1:
            return False
        elif value[2] not in check_2:
            return False
    return True

def converter(input_list):
    output = {}
    # {'Sunseed Genius Loci': 3}
    for key, value in input_list.items():
        dic_list = [0, '', '']
        dic_list[0] = value
        output[key] = dic_list
    return output


class Card:
    # all card shared properties. currently none
    
    def __init__(self, name):
        # specific card
        self.name = name
        self.copy = 1
        # number in deck, default 1
        self.amount = 1
        # Either engine or non-engine since calcluating playability
        self.card_type = ''
        # applying Patrick Hoban's card type theory-turn into list since possible to have multiple
        # Starter, extender, defensive, offensive, garnet, consistency
        self.subtype = ''
        
    def __str__(self):
        return self.name

def create_card(deck_dictionary):
    # input is decklist.data
    # have it assign the things as well
    card_object_list = []
    for card_name, feature in deck_dictionary.items():
        for i in range(feature[0]):
            new_card = Card(card_name)
            new_card.copy = i+1
            new_card.amount = feature[0]
            new_card.card_type = feature[1]
            new_card.subtype = feature[2]
            card_object_list.append(new_card)
    return card_object_list

def deck_importer(decklist_input):
    # global card_object_list
    global deck_dictionary_whole, deck_dictionary_main
    deck_list = decklist_input.split("\r\n")
    # print(deck_list)
    parser(deck_list, 'whole')
    success = parser(deck_list, 'main')
    
    if success == 1:
        # valid decklist-create json
        # print(deck_dictionary_whole)
        json_object = json.dumps(deck_dictionary_main, sort_keys=True, indent=4)
        # print(json_object)
        
        return converter(deck_dictionary_main)
    else:
        # tried to add invalid deck
        print("Invalid Deck Format. Press Enter to continue")
        return None


def combo_checker(combo_list, deck_data):
    if len(combo_list) == 1:
        if combo_list[0] == []:
            return True
    for combo in combo_list:
        if len(combo)>0:
            for card in combo:
                if card not in deck_data.keys():
                    return False
        else:
            return False
        
    return True

def analysis_func(local_list, combo):
    # make copy of list and edit to check
    
    # [1 starter, total starter, garnets, playable, 2 card combo (exists)]
    output = [0, 0, 0, 0, 0]
    for card in local_list:
        if card.subtype == 'Starter':
            # becomes playable
            output[0] = 1
            output[1] += 1
        elif card.subtype == 'Garnet':
            output[2] += 1
        # add combo for playable later
        else:
            for subcombo in combo:
                if card.name in subcombo:
                    # loop through rest?
                    local_copy = subcombo.copy()
                    local_copy.remove(card.name)
                    for card in local_list:
                        if local_copy[0] == card.name:
                            # counts as 2 card combo
                            # count 2 hand combo once only?
                            # check if playable or other 1 card starter
                            output[4] = 1
    if output[0] == 0 and output[4] == 0:
        # unplayable
        pass
    else:
        output[3] = 1
    return output

def simulation(card_list, runs, hand_size, combo):
    # list of list?
    
    total_starter = 0
    analysis_dict = {'Hands with at least 1 Starter': 0, 
                'Hands with no Starters': 0,
                'Hands with Garnets': 0,
                'Average Starters in Hand': 0,
                'Hands with a 2 Card Combo': 0,
                '"Playable Hands"': 0,
                '"Unplayable Hands"': 0,
                'Average Hand Playability': '0%'}
    results = []
    
    for run in range(runs):
        analysis_results = []
        # current hand
        local_result = []
        local_card = []
        random.shuffle(card_list)
        # handsize
        for card in range(hand_size):
            local_result.append(card_list[card].name)
            local_card.append(card_list[card])
        analysis_results = analysis_func(local_card, combo)
        analysis_dict['Hands with at least 1 Starter'] += analysis_results[0]
        total_starter += analysis_results[1]
        if analysis_results[1] == 0:
            analysis_dict['Hands with no Starters'] += 1
        analysis_dict['Hands with Garnets'] += analysis_results[2]
        analysis_dict['Hands with a 2 Card Combo'] += analysis_results[4]
        if analysis_results[3] != 0:
            analysis_dict['"Playable Hands"'] += analysis_results[3]
        else:
            analysis_dict['"Unplayable Hands"'] += 1
        playable_percent = analysis_dict['"Playable Hands"']/runs
        analysis_dict['Average Hand Playability'] = f'{playable_percent * 100}%'
        # print(local_result)
        results.append(local_result)
        # local results, add to global after printing
    
    analysis_dict['Average Starters in Hand'] = total_starter/runs
    # print(analysis_dict)
    return (analysis_dict, results)

    # have analysis in here
    # what to evaluate

    # analysis here?
    # export_option = input("Enter Option, Press Enter to Return: ")
    # if export_option == '1':
    #     # Just data
    #     export_name = input('Enter Export File Name: ')
    #     with open(f"results/{export_name}.csv", 'w') as file:
    #         for line in results:
    #             writer = csv.writer(file, lineterminator="\n")
    #             writer.writerow(sorted(line))
    #         writer.writerow(['Total Runs', runs])
    #     input("Exported Results to results Folder. Press Enter to continue.")
    # elif export_option == '2':
    #     # Just analysis
    #     export_name = input('Enter Export File Name: ')
    #     with open(f"results/{export_name}.csv", 'w') as file:
    #         for key, value in analysis_dict.items():
    #             out = [key, value]
    #             writer = csv.writer(file, lineterminator="\n")
    #             writer.writerow(out)
    #         writer.writerow(['Total Runs', runs])
    #     input("Exported Results to results Folder. Press Enter to continue.")
    # elif export_option == '3':
    #     # Both-most common
    #     export_name = input('Enter Export File Name: ')
    #     with open(f"results/{export_name}.csv", 'w') as file:
    #         for line in results:
    #             writer = csv.writer(file, lineterminator="\n")
    #             writer.writerow(sorted(line))
    #         writer.writerow('\n')
    #         for key, value in analysis_dict.items():
    #             out = [key, value]
    #             writer.writerow(out)
    #         writer.writerow(['Total Runs', runs])
    #     input("Exported Results to results Folder. Press Enter to continue.")
    # elif export_option == '4':
    #     simulation(card_list, runs, hand_size, combo)

testlist = """Monster
3 Sunseed Genius Loci
1 Therion "King" Regulus
1 Therion "Lily" Borea
1 Snowdrop the Rikka Fairy
2 Mudan the Rikka Fairy
1 Primula the Rikka Fairy
3 Rikka Princess
1 Lonefire Blossom
2 Ash Blossom & Joyous Spring
1 Sunseed Twin
2 Droll & Lock Bird
2 Rikka Petal
Spell
2 Dark Ruler No More
1 One for One
3 Rikka Glamour
2 Sunvine Sowing
2 Triple Tactics Talent
3 Unexpected Dai
1 Called by the Grave
3 Crossout Designator
2 Rikka Konkon
1 Therion Discolosseum
Trap
2 Infinite Impermanence
1 Rikka Sheet
Extra
1 Sacred Tree Beast, Hyperyton
1 Teardrop the Rikka Queen
2 Rikka Queen Strenna
1 Benghalancer the Resurgent
1 Sunavalon Melias
2 Aromaseraphy Jasmine
1 Sylvan Dancepione
1 Sunvine Thrasher
2 Sunvine Healer
3 Sunavalon Dryas
Side
2 Nibiru, the Primal Being
1 Naturia Rosewhip
1 Predaplant Spider Orchid
1 Harpie's Feather Duster
2 Triple Tactics Thrust
2 Book of Eclipse
2 Cosmic Cyclone
1 Dimensional Barrier
2 Evenly Matched
1 Spiritual Water Art - Aoi
"""

testcombo = []

testoutput = """
{'Sunseed Genius Loci': 3, 'Therion "King" Regulus': 1, 'Therion "Lily" Borea': 1, 'Snowdrop the Rikka Fairy': 1, 'Mudan the Rikka Fairy': 2, 'Primula the Rikka Fairy': 1, 'Rikka Princess': 3, 'Lonefire Blossom': 1, 'Ash Blossom & Joyous Spring': 2, 'Sunseed Twin': 1, 'Droll & Lock Bird': 2, 'Rikka Petal': 2, 'Dark Ruler No More': 2, 
'One for One': 1, 'Rikka Glamour': 3, 'Sunvine Sowing': 2, 'Triple Tactics Talent': 2, 'Unexpected Dai': 3, 'Called by the Grave': 1, 'Crossout Designator': 3, 'Rikka Konkon': 2, 'Therion Discolosseum': 1, 'Infinite Impermanence': 2, 'Rikka Sheet': 1}"""
# print(testlist.split("\n"))
# testout = deck_importer(testlist)
#print(testout)
# print(converter(testout))

testout2 = {
    "Kashtira Unicorn": [
      2,
      "Engine",
      "Starter"
    ],
    "Kashtira Fenrir": [
      3,
      "Engine",
      "Extender"
    ],
    "Scareclaw Kashtira": [
      1,
      "Engine",
      "Extender"
    ],
    "Dimension Shifter": [
      3,
      "Non-Engine",
      "Offensive"
    ],
    "Kashtira Riseheart": [
      2,
      "Engine",
      "Extender"
    ],
    "Ash Blossom & Joyous Spring": [
      3,
      "",
      ""
    ],
    "Kashtiratheosis": [
      3,
      "",
      ""
    ],
    "Pot of Prosperity": [
      3,
      "Engine",
      "Consistency"
    ],
    "Terraforming": [
      1,
      "Engine",
      "Starter"
    ],
    "Triple Tactics Talent": [
      3,
      "",
      ""
    ],
    "Book of Moon": [
      3,
      "Non-Engine",
      "Offensive"
    ],
    "Kashtira Birth": [
      3,
      "Engine",
      "Extender"
    ],
    "Forbidden Lance": [
      3,
      "Non-Engine",
      "Defensive"
    ],
    "Pressured Planet Wraitsoth": [
      3,
      "Engine",
      "Starter"
    ],
    "Infinite Impermanence": [
      3,
      "Non-Engine",
      "Defensive"
    ],
    "Kashtira Big Bang": [
      1,
      "Engine",
      "Garnet"
    ]
  }


# testin2 = {['asdf', 'fda'], ['ff', 'cv']}
# testout3 = json.loads(testin2)
#outs = create_card(testout2)
#print(simulation(outs, 5, 5, []))