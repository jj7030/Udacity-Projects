# -*- coding: utf-8 -*-
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

import schema

#Path of our OpenStreetMap file

OSM_PATH = "sample1.osm"

#5 Different files will be generated which are #nodes.csv,nodes_tags.csv,ways.csv,ways_nodes.csv and ways_tags.csv

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

#Using Regular expressions to find words which are problematic i.e have symbols 
#street_type_re is the regular expression to find words like Road.

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

#Here we have the expected words i.e which are abbreviated

expected=["Rd","Av.","rd.","rd","Av"]
mapping = { "Rd": "Road",
            "Av.": "Avenue",
            "rd.": "Road",
            "rd": "Road",
            "Av": "Avenue",
            }
SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

#The following function takes care of converting the data into desired form of lists and #dictionaries.We find each element's tag and see if they are node or way.If it is a node #then we further iter to it's tags and assign the attributes to our #dictionary(id,lat,lon,uid,user,version,changeset,timestamp).Similarly we iter through the #tags of way and do the similar thing.We even check for the regular expressions mentioned #in the beginning of the code.If there are problematic keys then we will ignore it.If #there are words with colon then we will split it and assign the begining part to key and
#the latter part to type 

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  

    if element.tag == 'node':
        for x in element.iter('node'):
            node_attribs['id']=x.attrib['id']
            node_attribs['lat']=x.attrib['lat']
            node_attribs['lon']=x.attrib['lon']
            node_attribs['uid']=x.attrib['uid']
            node_attribs['user']=x.attrib['user']
            node_attribs['version']=x.attrib['version']
            node_attribs['changeset']=x.attrib['changeset']
            node_attribs['timestamp']=x.attrib['timestamp']
           

            for tg in x.iter('tag'):
                ntag={}
                ntag['id']=x.attrib['id']
                tagkey=tg.attrib.get('k')
                p=PROBLEMCHARS.search(tagkey)
                if p:
                     break
                if not p:
                    m=LOWER_COLON.search(tagkey)
                    if m:
                        match = re.search('([\w.-]+):([\w.-]+):([\w.-]+)', tagkey)
                        match2= re.search('([\w.-]+):([\w.-]+)', tagkey)

                        if match:
                            asd2=match.group(3)
                            asd=match.group(2)
                            ntag['key']=asd+':'+asd2
                            ntag['type']=match.group(1)
                        elif not match:
                            if match2:
                                ntag['key']=match2.group(2)
                                ntag['type']=match2.group(1)
                    elif not m:
                        ntag['key']=tagkey
                        ntag['type']='regular'
                
                value=tg.attrib.get('v')
                last_m = street_type_re.search(value)
                if last_m:
                    last_word= last_m.group()
                    if last_word in expected:
                        name1=re.sub(r'\b\S+\.?$', mapping[last_word], value, flags=re.IGNORECASE)
                        ntag['value']= name1
                    else:
                        ntag['value']= value
                    tags.append(ntag)
            return {'node': node_attribs, 'node_tags': tags}
        

    elif element.tag == 'way':
        for y in element.iter('way'):
            way_attribs['id']=y.attrib.get('id')
            way_attribs['user']=y.attrib.get('user')
            way_attribs['uid']=y.attrib.get('uid')
            way_attribs['version']=y.attrib.get('version')
            way_attribs['timestamp']=y.attrib.get('timestamp')
            way_attribs['changeset']=y.attrib.get('changeset')
            for wtag in y.iter('tag'):
                wtagd={}
                wtagd['id']=y.attrib['id']
                tagkey=wtag.attrib.get('k')
                p=PROBLEMCHARS.search(tagkey)
                if not p:
                    m=LOWER_COLON.search(tagkey)
                    if m:
                        match = re.search('([\w.-]+):([\w.-]+):([\w.-]+)', tagkey)
                        match2= re.search('([\w.-]+):([\w.-]+)', tagkey)

                        if match:
                            asd2=match.group(3)
                            asd=match.group(2)
                            wtagd['key']=asd+':'+asd2
                            wtagd['type']=match.group(1)
                        elif not match:
                            #If one colon exits then add the first word to type and the next to key.
                            if match2:
                                wtagd['key']=match2.group(2)
                                wtagd['type']=match2.group(1)
                    #If the key string has no colons.
                    elif not m:
                        wtagd['key']=tagkey
                        wtagd['type']='regular'

                value=wtag.attrib.get('v')
                last_m = street_type_re.search(value)
                if last_m:
                    last_word= last_m.group()
                    if last_word in expected:
                        name1=re.sub(r'\b\S+\.?$', mapping[last_word], value, flags=re.IGNORECASE)
                        wtagd['value']= name1
                    else:
                        wtagd['value']= value                
                tags.append(wtagd)

            pos=0
            for ndtag in y.iter('nd'):
                ndtagd={}
                ndtagd['id']=y.attrib.get('id')
                ndtagd['node_id']=ndtag.attrib.get('ref')
                ndtagd['position']=pos
                pos=pos+1
                way_nodes.append(ndtagd)
            return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}





# The following helpers functions have been adopted from the case study of lesson 13 from the Data Wrangling course.
# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# In[5]:


# The following functions have been adopted from the case study of lesson 13 from the Data Wrangling course.
# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,          codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)


