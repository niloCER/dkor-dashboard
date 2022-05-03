import spacy
import re
from spacy.tokens import Token
from spacy.symbols import ORTH
from spacy.symbols import NORM
from spacy.matcher import DependencyMatcher
from spacy.matcher import Matcher

# create member state entity
ms = ['BEL','BGR','DNK','DEU','EST','FIN','FRA','GBR','GRC','IRL','ITA','HRV','LAT','LTU','LUX','MLT','NLD','AUT','POL','PRT','ROU','SWE','SVK','SVN','ESP','CZE','HUN','CYP']
ms.sort()

def get_is_ms(token):
    return token.text in ms

Token.set_extension("IS_MS", getter=get_is_ms)

# List - remove subsets
def removeSublist(lst):
    curr_res = []
    result = []
    for ele in sorted(map(set, lst), key = len, reverse = True):
        if not any(ele <= req for req in curr_res):
            curr_res.append(ele)
            result.append(list(ele))

    for ele in result:
        ele = ele.sort()

    return result

# List - merge sub lists
def Find(id,P):
    if P[id]<0 : return id
    P[id]=Find(P[id],P)
    return P[id]

def Union(id1, id2, P):
    id1 = Find(id1,P)
    id2 = Find(id2,P)
    if id1 != id2:
        P[id2]=id1

# import Drahtberichte
#dkor = open("./NLP Tests/DKORs_clean/20130704_AStV 2 EU US Gruppe.txt").read()
#dkor = open("./NLP Tests/DKORs_clean/20130624_JI ReferentInnen EU US Gruppe.txt").read()
#dkor = open("./NLP Tests/DKORs_clean/20130625_TAG CORTA EU US Datenschutzabkommen.txt").read()

# tests
#dkor = "Mit Ausnahme von GBR und SWE unterstützten alle wortnehmenden MS (FRA, DEU, DNK, NLD, BEL, AUT, ITA, GRC, LVA, PRT, FIN, HUN und BGR) diesen Ansatz, sowie KOM und EAD. "
#dkor = "3. Nachdem GBR und SWE bei ihrer ablehnenden Position blieben, bemerkte DEU, dass der Vorsitz frei darin sei, Schlussfolgerungen zu ziehen. "
#dkor = "Wobei DEU und POL, hierin unterstützt von DNK und NLD den Auftaktcharakter der Veranstaltung zum Zwecke des Beginns eines Arbeitsprozesses betonte, um Fakten zum weiteren Vorgehen zu erarbeiten."
#dkor = "GBR erläuterte, hierin unterstützt von FRA, dass nachrichtendienstliche Fragen der Gruppe 2 in alleiniger Kompetenz der MS lägen."
#dkor = "FRA, NLD, ITA unterstützten DEU."

def dkor_nlp(dkor_path):

    dkor = open(dkor_path).read()

    #nlp = spacy.load("de_core_news_sm")
    #nlp = spacy.load("de_core_news_md")
    nlp = spacy.load("de_core_news_lg")

    # special cases
    special_case_vors = [{ORTH: "Vors"}, {ORTH: ".", NORM: ""}]
    nlp.tokenizer.add_special_case("Vors.", special_case_vors)

    #special_case_vors_ms = [{"REGEX": "BEL|BGR|DNK|DEU|EST|FIN|FRA|GBR|GRC|IRL|ITA|HRV|LAT|LTU|LUX|MLT|NLD|AUT|POL|PRT|ROU|SWE|SVK|SVN|ESP|CZE|HUN|CYP"}, {ORTH: "-", NORM: " "}, {ORTH: "Vors"}, {ORTH: ".", NORM: ""}]
    #nlp.tokenizer.add_special_case("[BEL|BGR|DNK|DEU|EST|FIN|FRA|GBR|GRC|IRL|ITA|HRV|LAT|LTU|LUX|MLT|NLD|AUT|POL|PRT|ROU|SWE|SVK|SVN|ESP|CZE|HUN|CYP]-Vors.", special_case_vors_ms)

    # dependency matcher
    #matcher = Matcher(nlp.vocab)
    matcher_dep = DependencyMatcher(nlp.vocab)
    matcher_unterstuetzen = DependencyMatcher(nlp.vocab)
    matcher_unterstuetzt_von_Verb_ROOT = DependencyMatcher(nlp.vocab)
    matcher_unterstuetzt_von_MS_ROOT = DependencyMatcher(nlp.vocab)
    matcher_unterstuetzt_von_modal = DependencyMatcher(nlp.vocab)
    matcher_votierte_fuer = DependencyMatcher(nlp.vocab)
    matcher_wurde_unterstuetzt = DependencyMatcher(nlp.vocab)
    matcher_wurde_unterstuetzt_nebensatz = DependencyMatcher(nlp.vocab)

    pattern_dep = [
        {
            "RIGHT_ID": "anchor_ms",                                                            # unique name
            "RIGHT_ATTRS": {"_": {"IS_MS": True}, "DEP": {"REGEX": "sb|nk|oa|par|app|ROOT|cj"}}    # token pattern for "ms"
        },
        {
            "LEFT_ID": "anchor_ms",
            "REL_OP": ">>",
            "RIGHT_ID": "dep_ms",
            "RIGHT_ATTRS": {"_": {"IS_MS": True}}
        }
    ]

    pattern_unterstuetzen = [
        {
            "RIGHT_ID": "anchor_unterstuetzen",                                                            # unique name
            "RIGHT_ATTRS": {"LEMMA": {"REGEX": "unterstützen|zustimmen"}, "_": {"IS_MS": False}, "DEP": "ROOT", "POS": "VERB"}  # token pattern for "ms"
        },
        {
            "LEFT_ID": "anchor_unterstuetzen",
            "REL_OP": ">>",
            "RIGHT_ID": "sb",
            "RIGHT_ATTRS": {"_": {"IS_MS": True}, "DEP": "sb"}
        },
        {
            "LEFT_ID": "anchor_unterstuetzen",
            "REL_OP": ">>",
            "RIGHT_ID": "oa",
            "RIGHT_ATTRS": {"_": {"IS_MS": True}, "DEP": "oa"}
        }
    ]

    #Verb_ROOT
    pattern_unterstuetzt_von_Verb_ROOT = [
        {
            "RIGHT_ID": "anchor_unterstuetzt_von_Verb_ROOT",                        # unique name
            "RIGHT_ATTRS": {"_": {"IS_MS": False}, "DEP": "ROOT", "POS": "VERB"}    # token pattern for "ms"
        },
        {
            "LEFT_ID": "anchor_unterstuetzt_von_Verb_ROOT",
            "REL_OP": ">>",
            "RIGHT_ID": "sb",
            "RIGHT_ATTRS": {"_": {"IS_MS": True}, "DEP": "sb",}
        },
        {
            "LEFT_ID": "anchor_unterstuetzt_von_Verb_ROOT",
            "REL_OP": "$++",
            "RIGHT_ID": "unterstuetzt",                                                        
            "RIGHT_ATTRS": {"LEMMA": "unterstützen", "_": {"IS_MS": False}, "DEP": {"REGEX": "par|cj|oc"}, "POS": "VERB"}   
        },
        {
            "LEFT_ID": "unterstuetzt",
            "REL_OP": ">",
            "RIGHT_ID": "sbp",
            "RIGHT_ATTRS": {"_": {"IS_MS": False}, "DEP": "sbp", "ORTH": "von"}
        },
        {
            "LEFT_ID": "unterstuetzt",
            "REL_OP": ">>",
            "RIGHT_ID": "nk",
            "RIGHT_ATTRS": {"_": {"IS_MS": True}, "DEP": "nk"}
        }
    ]

    pattern_unterstuetzt_von_MS_ROOT = [
        {
            "RIGHT_ID": "anchor_unterstuetzt_von_MS_ROOT",                        # unique name
            "RIGHT_ATTRS": {"_": {"IS_MS": True}, "DEP": {"REGEX": "sb|ROOT"}}    # token pattern for "ms"
        },
        {
            "LEFT_ID": "anchor_unterstuetzt_von_MS_ROOT",
            "REL_OP": ".*",
            "RIGHT_ID": "unterstuetzt",                                                        
            "RIGHT_ATTRS": {"LEMMA": "unterstützen", "_": {"IS_MS": False}, "DEP": {"REGEX": "par|cj|mo"}, "POS": "VERB"}   
        },
        {
            "LEFT_ID": "unterstuetzt",
            "REL_OP": ">",
            "RIGHT_ID": "sbp",
            "RIGHT_ATTRS": {"_": {"IS_MS": False}, "DEP": "sbp", "ORTH": "von"}
        },
        {
            "LEFT_ID": "unterstuetzt",
            "REL_OP": ">>",
            "RIGHT_ID": "nk",
            "RIGHT_ATTRS": {"_": {"IS_MS": True}, "DEP": "nk"}
        }
    ]

    pattern_unterstuetzt_von_modal = [
        {
            "RIGHT_ID": "anchor_unterstuetzt_von_modal",                                                          
            "RIGHT_ATTRS": {"LEMMA": {"REGEX": "unterstützen"}, "_": {"IS_MS": False}, "POS": "VERB"}  
        },
        {
            "LEFT_ID": "anchor_unterstuetzt_von_modal",
            "REL_OP": ">>",
            "RIGHT_ID": "sb",
            "RIGHT_ATTRS": {"_": {"IS_MS": True}, "DEP": "sb"}
        },
        {
            "LEFT_ID": "sb",
            "REL_OP": "$++",
            "RIGHT_ID": "von",
            "RIGHT_ATTRS": {"_": {"IS_MS": False}, "DEP": "sbp", "ORTH": "von"}
        },
        {
            "LEFT_ID": "von",
            "REL_OP": ">>",
            "RIGHT_ID": "nk",
            "RIGHT_ATTRS": {"_": {"IS_MS": True}, "DEP": "nk"}
        }
    ]

    pattern_votierte_fuer = [
        {
            "RIGHT_ID": "anchor_votierte",                                                          
            "RIGHT_ATTRS": {"LEMMA": {"REGEX": "votierte|votiert"}, "_": {"IS_MS": False}, "POS": "VERB"}  
        },
        {
            "LEFT_ID": "anchor_votierte",
            "REL_OP": ">>",
            "RIGHT_ID": "sb",
            "RIGHT_ATTRS": {"_": {"IS_MS": True}, "DEP": "sb"}
        },
        {
            "LEFT_ID": "sb",
            "REL_OP": "$++",
            "RIGHT_ID": "fuer",
            "RIGHT_ATTRS": {"_": {"IS_MS": False}, "DEP": "mo", "ORTH": "für"}
        },
        {
            "LEFT_ID": "fuer",
            "REL_OP": ">>",
            "RIGHT_ID": "nk",
            "RIGHT_ATTRS": {"_": {"IS_MS": True}, "DEP": "nk"}
        }
    ]

    pattern_wurde_unterstuetzt = [
        {
            "RIGHT_ID": "wurde",                                                          
            "RIGHT_ATTRS": {"LEMMA": "werden", "_": {"IS_MS": False}, "POS": "AUX"}  
        },
        {
            "LEFT_ID": "wurde",
            "REL_OP": ">>",
            "RIGHT_ID": "sb",
            "RIGHT_ATTRS": {"_": {"IS_MS": True}, "DEP": "sb"}
        },
        {
            "LEFT_ID": "sb",
            "REL_OP": "$++",
            "RIGHT_ID": "unterstuetzt",
            "RIGHT_ATTRS": {"LEMMA": "unterstützen", "_": {"IS_MS": False}, "POS": "VERB"}
        },
        {
            "LEFT_ID": "unterstuetzt",
            "REL_OP": ">>",
            "RIGHT_ID": "von",
            "RIGHT_ATTRS": {"_": {"IS_MS": False}, "DEP": "sbp", "ORTH": "von"}
        },
        {
            "LEFT_ID": "von",
            "REL_OP": ">>",
            "RIGHT_ID": "nk",
            "RIGHT_ATTRS": {"_": {"IS_MS": True}, "DEP": "nk"}
        }

    ]

    pattern_wurde_unterstuetzt_nebensatz = [
         {
            "RIGHT_ID": "anchor_verb",                        
            "RIGHT_ATTRS": {"_": {"IS_MS": False}, "DEP": "ROOT", "POS": "VERB"}    
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">>",
            "RIGHT_ID": "sb",
            "RIGHT_ATTRS": {"_": {"IS_MS": True}, "DEP": "sb",}
        },
        {
            "LEFT_ID": "anchor_verb",
            "REL_OP": ">>",
            "RIGHT_ID": "und",                                                        
            "RIGHT_ATTRS": {"_": {"IS_MS": False}, "DEP": "cd", "ORTH": "und"}   
        },
        {
            "LEFT_ID": "und",
            "REL_OP": ">>",
            "RIGHT_ID": "wurde",
            "RIGHT_ATTRS": {"LEMMA": "werden", "_": {"IS_MS": False}, "POS": "AUX"}
        },
        {
            "LEFT_ID": "wurde",
            "REL_OP": ">>",
            "RIGHT_ID": "unterstuetzt",
            "RIGHT_ATTRS": {"LEMMA": "unterstützen", "_": {"IS_MS": False}, "POS": "VERB", "DEP": "oc"}
        },
        {
            "LEFT_ID": "unterstuetzt",
            "REL_OP": ">>",
            "RIGHT_ID": "von",
            "RIGHT_ATTRS": {"_": {"IS_MS": False}, "DEP": "sbp", "ORTH": "von"}
        },
        {
            "LEFT_ID": "von",
            "REL_OP": ">>",
            "RIGHT_ID": "nk",
            "RIGHT_ATTRS": {"_": {"IS_MS": True}, "DEP": "nk"}
        }

    ]

    #matcher.add("MS", [pattern_ms])
    matcher_dep.add("DEP", [pattern_dep])
    matcher_unterstuetzen.add("UNT", [pattern_unterstuetzen])
    matcher_unterstuetzt_von_Verb_ROOT.add("UNT_VON", [pattern_unterstuetzt_von_Verb_ROOT])
    matcher_unterstuetzt_von_MS_ROOT.add("UNT_VON", [pattern_unterstuetzt_von_MS_ROOT])
    matcher_unterstuetzt_von_modal.add("UNT_VON", [pattern_unterstuetzt_von_modal])
    matcher_votierte_fuer.add("DEP", [pattern_votierte_fuer])
    matcher_wurde_unterstuetzt.add("DEP", [pattern_wurde_unterstuetzt])
    matcher_wurde_unterstuetzt_nebensatz.add("DEP", [pattern_wurde_unterstuetzt_nebensatz])

    # NLP processing
    doc = nlp(dkor)

    #for token in doc:
    #	print(token.text, token.pos_, token.dep_, token.head.text)

    # matching
    matches_dep = matcher_dep(doc)
    matches_unterstuetzen = matcher_unterstuetzen(doc)
    matches_unterstuetzt_von_Verb_ROOT = matcher_unterstuetzt_von_Verb_ROOT(doc)
    matches_unterstuetzt_von_MS_ROOT = matcher_unterstuetzt_von_MS_ROOT(doc)
    matches_unterstuetzt_von_modal = matcher_unterstuetzt_von_modal(doc)
    matches_votierte_fuer = matcher_votierte_fuer(doc)
    matches_wurde_unterstuetzt = matcher_wurde_unterstuetzt(doc)
    matches_wurde_unterstuetzt_nebensatz = matcher_wurde_unterstuetzt_nebensatz(doc)

    #for m in matches_unterstuetzt_von_MS_ROOT:
    #    match_id, token_ids = m
    #    print(m)
    #    for i in range(len(token_ids)):
    #        #print(pattern_unterstuetzt_von_MS_ROOT[i]["RIGHT_ID"] + ":", doc[token_ids[i]].text + " " + str(token_ids[1]) + " " + str(i))
    #        print(pattern_unterstuetzt_von_MS_ROOT[i]["RIGHT_ID"] + ":", doc[token_ids[i]].text)


    # process dep matches
    index_list = []
    index = []
    curr_token = -1
    for m in matches_dep:
        match_id, token_ids = m
        if token_ids[0]!=curr_token: 
            if curr_token > 0 :
                index_list.append(index)
                index = []
            index.append(token_ids[0])
            curr_token = token_ids[0]
        index.append(token_ids[1])
    index_list.append(index)

    index_list = removeSublist(index_list)
    index_list.sort()

    # print index
    #for i in index_list:
    #    print(i)
    #    print("")

    # process special cases
    # 1. unterstützen
    special_cases_list = []
    special_case = []
    curr_token = -1

    for m in matches_unterstuetzen:
        match_id, token_ids = m
        if token_ids[1]!=curr_token: 
            if curr_token > 0 :
                special_cases_list.append(special_case)
                special_case = []
            special_case.append(token_ids[1])
            curr_token = token_ids[1]
        special_case.append(token_ids[2])
    special_cases_list.append(special_case)

    ispecial_cases_list = removeSublist(special_cases_list)
    special_cases_list.sort()

    # 2. unterstüzt von (Verb ROOT)
    special_case = []
    curr_token = -1

    for m in matches_unterstuetzt_von_Verb_ROOT:
        match_id, token_ids = m
        if token_ids[1]!=curr_token: 
            if curr_token > 0 :
                special_cases_list.append(special_case)
                special_case = []
            special_case.append(token_ids[1])
            curr_token = token_ids[1]
        special_case.append(token_ids[4])
    special_cases_list.append(special_case)

    ispecial_cases_list = removeSublist(special_cases_list)
    special_cases_list.sort()

    # 3. unterstützt von (MS ROOT)
    special_case = []
    curr_token = -1

    for m in matches_unterstuetzt_von_MS_ROOT:
        match_id, token_ids = m
        if token_ids[0]!=curr_token: 
            if curr_token > 0 :
                special_cases_list.append(special_case)
                special_case = []
            special_case.append(token_ids[0])
            curr_token = token_ids[0]
        special_case.append(token_ids[3])
    special_cases_list.append(special_case)

    ispecial_cases_list = removeSublist(special_cases_list)
    special_cases_list.sort()

    # 4. unterstützt von (modal)
    special_case = []
    curr_token = -1

    for m in matches_unterstuetzt_von_modal:
        match_id, token_ids = m
        if token_ids[1]!=curr_token: 
            if curr_token > 0 :
                special_cases_list.append(special_case)
                special_case = []
            special_case.append(token_ids[1])
            curr_token = token_ids[1]
        special_case.append(token_ids[3])
    special_cases_list.append(special_case)

    special_cases_list = removeSublist(special_cases_list)
    special_cases_list.sort()

    # 5. votierte fuer
    special_case = []
    curr_token = -1

    for m in matches_votierte_fuer:
        match_id, token_ids = m
        if token_ids[1]!=curr_token: 
            if curr_token > 0 :
                special_cases_list.append(special_case)
                special_case = []
            special_case.append(token_ids[1])
            curr_token = token_ids[1]
        special_case.append(token_ids[3])
    special_cases_list.append(special_case)

    special_cases_list = removeSublist(special_cases_list)
    special_cases_list.sort()

    # 6. wurde unterstuetzt
    special_case = []
    curr_token = -1

    for m in matches_wurde_unterstuetzt:
        match_id, token_ids = m
        if token_ids[1]!=curr_token: 
            if curr_token > 0 :
                special_cases_list.append(special_case)
                special_case = []
            special_case.append(token_ids[1])
            curr_token = token_ids[1]
        special_case.append(token_ids[4])
    special_cases_list.append(special_case)

    special_cases_list = removeSublist(special_cases_list)
    special_cases_list.sort()

    # 7. wurde unterstuetzt nebensatz
    special_case = []
    curr_token = -1

    for m in matches_wurde_unterstuetzt_nebensatz:
        match_id, token_ids = m
        if token_ids[1]!=curr_token: 
            if curr_token > 0 :
                special_cases_list.append(special_case)
                special_case = []
            special_case.append(token_ids[1])
            curr_token = token_ids[1]
        special_case.append(token_ids[6])
    special_cases_list.append(special_case)

    special_cases_list = removeSublist(special_cases_list)
    special_cases_list.sort()    

    # print special case
    #for i in special_cases_list:
    #    print(i)
    #    print("")

    # merge matches with special cases
    index_list = index_list + special_cases_list
    P = {}

    for list in index_list :
        for item in list :
            P[item] = -1

    for list in index_list :
        for i in range(1,len(list)):
                Union(list[i-1], list[i], P)

    ans = {}
    for list in index_list :
        for item in list :
            if Find(item,P) not in ans:
                ans[Find(item,P)] = []
            ans[Find(item,P)].append(item)

    index_list = [sorted(set(x)) for x in ans.values()]
    index_list.sort()

    #for i in index_list:
    #    print(i)
    #    print("")

    # transform index to MS
    matches_list = []
    match = []

    for i in index_list:
        for j in i:
            match.append(doc[j].text)
        matches_list.append(match)
        match = []

    # print matches
    #for m in matches_list:
    #    print(m)
    #    print("")

    #print(matches_list)
    return matches_list
