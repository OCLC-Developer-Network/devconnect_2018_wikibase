#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from pywikibot import family
import pywikibot, os.path, json, sys

reload(sys)
sys.setdefaultencoding('utf8')

# add a statement to a pywikibot item object
def add_statement(label,value,reference_source,reference_value):

    global entity_dictionary
    global entity_id

    # if the property label is in the property dictionary
    if label in entity_dictionary['property']:
    
        # if there is an object value for the statement + 
        if len(value) > 0:

            # add a statement for the last item created
            print(entity_id+" add statement "+entity_dictionary['property'][label]['id'] + " " + entity_dictionary['property'][label]['datatype'] + " " + value)
            target = get_target(value,entity_dictionary['property'][label]['datatype'])
            
            try:
                claim = pywikibot.page.Claim(repo, entity_dictionary['property'][label]['id'], datatype=entity_dictionary['property'][label]['datatype'])
                msg = "bot adding new " + label + " statement"
                claim.setTarget(target)
                entity_obj.addClaim(claim, summary=msg)
                
                # if there is a reference source and value for the statement
                if len(reference_source) > 0 and len(reference_value) > 0:
                    
                    # create a reference using the property for reference_source as the predicate
                    # and the Wikidata ID as the object
                    if reference_source in entity_dictionary['property']:
                        reference = pywikibot.Claim(repo, entity_dictionary['property'][reference_source]['id'], isReference=True)
                        reference.setTarget(reference_value)
                        try:
                            msg = "Add a reference url"
                            claim.addSource(reference, summary=msg)  
                            print("Add to "+entity_id+" reference "+entity_dictionary['property'][reference_source]['id']+ " " +reference_value)
                        except Exception as e:
                            if debug:
                                write_exception("ERROR ADDING REFERENCE")
                                write_exception(str(e))
                            
            except Exception, e:
                print("ERROR ADDING STATEMENT: " + entity_dictionary['property'][label]['id'] + " " + entity_dictionary['property'][label]['datatype'] + " " + value)
                print(e)
                pass
        else:
            print("ERROR ADDING STATEMENT: value is length 0")
                
    else:
        print("ERROR ADDING STATEMENT: label '" + label +"' is not in entity_dictionary['property']")


# given an initial target value and a datatype, return a statement target object
def get_target(value,datatype):

    global entity_id
    
    target = None

    if len(datatype) > 0:

        try:

            if datatype == 'globe-coordinate':

                precision = 0
                if 'precision' in value:
                       if not str(value['precision']) == "null" and not value['precision'] == None:
                           precision = float(value['precision'])
                try:
                    target = pywikibot.Coordinate(site=repo, lat=value['latitude'], lon=value['longitude'], precision=precision, globe='earth')
                except Exception, e:
                    msg = str(e).replace("\n"," ").replace("\r"," ")
                    print("Coordinate ERROR IN "+entity_id+": "+msg)
                    pass

            elif datatype == 'time':
                try:
                    precision = int(value['precision'])
                    target = pywikibot.WbTime.fromTimestr(value['time'], precision=precision, before=value['before'], after=value['after'], timezone=value['timezone'], calendarmodel=calendar_model[value['calendarmodel']], site=repo)
                except Exception, e:
                    msg = str(e).replace("\n"," ").replace("\r"," ")
                    print("WbTime ERROR IN "+entity_id+" FOR "+ds+": "+msg)
                    pass

            elif datatype == 'monolingualtext':
                if value['language'] in language_codes:
                    try:
                        target = pywikibot.WbMonolingualText(text=value['text'], language=value['language'])
                    except Exception, e:
                        msg = str(e).replace("\n"," ").replace("\r"," ")
                        print("WbMonolingualText ERROR IN "+entity_id+" FOR "+value['text']+": "+msg)
                        pass

            elif datatype == 'string' or datatype == 'url':
                target = value.strip()

            elif datatype == 'quantity':
                try:
                    target = pywikibot.WbQuantity(site=repo,amount=value['amount'],unit=value['unit'])
                except Exception, e:
                    msg = str(e).replace("\n"," ").replace("\r"," ")
                    print("WbQuantity ERROR IN "+entity_id+" FOR "+str(value['amount'])+": "+msg)
                    pass

            elif datatype == "external-id":
                try:
                    target = value.strip()
                except Exception, e:
                    msg = str(e).replace("\n"," ").replace("\r"," ")
                    print("getTarget external-id ERROR IN "+entity_id+" FOR "+str(value)+": "+msg)
                    pass

            elif datatype == 'wikibase-item':
                # look up the item's id using its label
                if value in entity_dictionary['item']:
                    try:
                        target = pywikibot.ItemPage(repo, entity_dictionary['item'][value]['id'])
                    except Exception, e:
                        msg = str(e).replace("\n"," ").replace("\r"," ")
                        print("getTarget wikibase-item ERROR IN "+entity_id+" FOR "+str(value)+": "+msg)
                        pass

            elif datatype == 'wikibase-property':
                try:
                    target = pywikibot.PropertyPage(repo, value)
                except Exception, e:
                    msg = str(e).replace("\n"," ").replace("\r"," ")
                    print("getTarget wikibase-property ERROR IN "+entity_id+" FOR "+str(value)+": "+msg)
                    pass

            elif datatype == "commonsMedia":
                try:
                    commonssite = pywikibot.Site("commons", "commons")
                    imagelink = pywikibot.Link(value, source=commonssite,defaultNamespace=6)
                    target = pywikibot.FilePage(imagelink)
                except Exception, e:
                    msg = str(e).replace("\n"," ").replace("\r"," ")
                    print("commonsMedia ERROR IN "+entity_id+" FOR "+str(value)+": "+msg)
                    pass

        except Exception, e:

            print("EXCEPTION IN get_target")
            print("ERROR: "+str(e))

    return target

if __name__ == "__main__":

    # initialize variables
    entity_label = ""
    entity_type = ""
    entity_id = ""
    entity_dictionary = {}
    entity_dictionary['item']= {}
    entity_dictionary['property'] = {}
    datatypes = {
      "http://wikiba.se/ontology#ExternalId": "external-id",
      "http://wikiba.se/ontology#GlobeCoordinate": "globe-coordinate",
      "http://wikiba.se/ontology#Monolingualtext": "monolingualtext",
      "http://wikiba.se/ontology#Quantity": "quantity",
      "http://wikiba.se/ontology#String": "string",
      "http://wikiba.se/ontology#Time": "time",
      "http://wikiba.se/ontology#WikibaseItem": "wikibase-item",
      "http://wikiba.se/ontology#WikibaseProperty": "wikibase-property",
      "http://wikiba.se/ontology#CommonsMedia": "commonsMedia",
      "http://wikiba.se/ontology#Url": "url"
    }

    # set the wikibase site and login
    site = pywikibot.Site('en', 'wikibasedocker')
    site.login()
    
    # set the site data repository
    repo = site.data_repository()
    
    # set the path and tsv file names to process
    pathname = 'scripts/userscripts/'
    filenames = [
        pathname+'initial_properties.tsv',
        pathname+'domain_properties.tsv',
        pathname+'initial_classes.tsv'
    ]

    # for each file name ...
    for fname in filenames:
        
        # open the file for reading ...
        with open(fname,'r') as infile:
        
            print("Processing data from "+fname)
        
            # for each line in the file ...
            for line in infile:

                # split the line on tabs into a list of elements
                line = line.strip()
                elements = line.split('\t')
                
                # GUIDE to the line elements
                # A line includes either data for creating a new entity, or data for adding a statement to the
                # most recently created entity
                # Lines for creating a new entity have these values in these tab-delimited positions:
                # 0 = The string "CREATE"
                # 1 = A string representing the entity type, "item" or "property"
                # 2 = The entity label
                # 3 = The entity description
                # 4 = The entity aliases
                # 5 = The entity datatype (optional)
                # Lines for adding statements have these values i these tab-delimited positions
                # 0 = The label for the statement property
                # 1 = A string representing the statement's object
                # 2 = A property for a reference source of the entity (optional)
                # 3 = A property value for a reference source of the entity (optional)
                
                # if the first item in the elements list is a "CREATE" instruction ...
                if elements[0] == 'CREATE':
                
                    # reset the current entity type and label and its datatype
                    entity_type = elements[1]
                    entity_label = elements[2]
                
                    # construct a fingerprint data object
                    lang = 'en'
                    fingerprint = {
                        'descriptions': {
                            'en': {
                                'language': lang,
                                'value': elements[3]
                            }
                        },
                        'labels': {
                            'en': {
                                'language': lang,
                                'value': entity_label
                            }
                        }
                    }
                    
                    # if there are aliases ...
                    if len(elements) >= 5:
                        if len(elements[4]) > 0:
                        
                            # create a list of aliases, splitting the string on a comma separator
                            aliases = elements[4].split(',')
                        
                            # construct a list of English language-tagged alias objects
                            aliases_object_list = []
                            for alias in aliases:
                                obj = {}
                                obj['value'] = alias
                                obj['language'] = lang
                                aliases_object_list.append(obj)
                            
                            # add the aliases list to the data object
                            fingerprint['aliases'] = {}
                            fingerprint['aliases'][lang] = aliases_object_list
                    
                    # if there is a datatype
                    if len(elements) == 6:
                        if elements[5] in datatypes:
                            fingerprint['datatype'] = datatypes[elements[5]]
                        
                    
                    # set parameters for the pywikibot api call to add a new property entity
                    action_type = 'wbeditentity'
                    message = 'adding a new '+entity_type
                    params = {
                        'action': action_type,
                        'new': entity_type,
                        'data': json.dumps(fingerprint),
                        'summary': message,
                        'token': site.tokens['edit']
                    }
                    
                    # submit the request
                    req = site._simple_request(**params)
                    results = req.submit()
                    
                    # get the entity id
                    entity_id = results['entity']['id']
                    print("Created "+entity_type+" entity "+entity_id+" for "+entity_label)
                    
                    # get the pywikibot object
                    if entity_type == "item":
                        entity_obj = pywikibot.ItemPage(repo,entity_id)
                    else:
                        entity_obj = pywikibot.PropertyPage(repo,entity_id)
                    
                    # add the entity id and data type to a dictionary, with the label as the dictionary key
                    if not entity_label in entity_dictionary[entity_type]:
                        obj = {}
                        obj['id'] = entity_id
                        if 'datatype' in fingerprint:
                            obj['datatype'] = fingerprint['datatype']
                        entity_dictionary[entity_type][entity_label] = obj
                    
                else:
                
                    # the elements list represents a statement to be added to the last entity created
                    # including the property label in position 0 and the object value in position 1
                    label = elements[0]
                    value = elements[1]
                    reference_source = ""
                    if len(elements) >= 3:
                        reference_source = elements[2]
                    reference_value = ""
                    if len(elements) >= 4:
                        reference_value = elements[3]
                    add_statement(label,value,reference_source,reference_value)