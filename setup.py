#!/usr/bin/env python3

from xmlrpc.client import ServerProxy
import json
import yaml
from random import choice

MANAGER_URL = 'http://c576.arch.suse.de/rpc/api'
MANAGER_LOGIN = 'admin'
MANAGER_PASSWORD = 'admin'
MAX_CITIES = 1
MAX_COUNTRIES = 1
GROUPS_FILE = 'groups_scenario_retail.yml'
DUMMY_EMAIL = 'joe@suse.com'

client = ServerProxy(MANAGER_URL, verbose=0)
key = client.auth.login(MANAGER_LOGIN, MANAGER_PASSWORD)

males = open('males.csv', 'r').readlines()
females = open('females.csv', 'r').readlines()
scenario = yaml.load(open(GROUPS_FILE, 'r'))

def generateName():
    ''' '''
    prefix = choice(['Mr.', 'Ms.'])
    if prefix == 'Mr.':
        first = choice(males)
        last = choice(males)
    else:
        first = choice(females)
        last = choice(females)
    return (prefix, first, last, DUMMY_EMAIL)

# Set up an organization for every country and add groups to the orgs
countries = json.load(open('countries.json', 'r'))
cities = json.load(open('cities.json', 'r'))
no_of_countries = 1
for country in countries:
    if no_of_countries > MAX_COUNTRIES:
        break
    login = MANAGER_LOGIN + '@' + country['code']
    prefix, first, last, email = generateName()
    client.org.create(
        key,
        country['name'],
        login,
        MANAGER_PASSWORD, # FIXME
        prefix,
        first,
        last,
        email,
        False
        )
    org_key = client.auth.login(login, MANAGER_PASSWORD)

    # Set up groups for cities of the world
    no_of_groups = 1
    for city in cities:
        if no_of_groups > MAX_CITIES:
            break
        if country['code'] == city['country']:
            try:
                client.systemgroup.create(
                    org_key,
                    city['name'] + ' (LOCATION)',
                    'City of ' +
                    city['name'] + ' in ' + city['country'] + '(' +
                    'Location: ' +
                    'latitude ' + city['lat'] + ', ' +
                    'longitude ' + city['lng'] + ')'
                    )
                print(city['name'], city['country'])
                no_of_groups+=1
            except xmlrpclib.Fault:
                print('ERROR: ', city['name'], ': Seems to be a duplicate')

    # Set up staging groups
    for stage in scenario['Stages']:
        client.systemgroup.create(
            org_key,
            stage + ' (STAGE)',
            stage + ' Systems'
            )
    # Set up HW type groups
    for hw in scenario['Server_HW']:
        client.systemgroup.create(
            org_key,
            hw + ' (SERVER HARDWARE TYPE)',
            hw + ' Server Systems'
            )
    for hw in scenario['Client_HW']:
        client.systemgroup.create(
            org_key,
            hw + ' (CLIENT HARDWARE TYPE)',
            hw + ' Client (Desktop, POS) Systems'
            )
    # Set up Role groups
    for role in scenario['Roles']:
        client.systemgroup.create(
            org_key,
            role + ' (ROLE)',
            role + ' System'
            )
    # Set up OS groups
    for os in scenario['OS']:
        client.systemgroup.create(
            org_key,
            os + ' (OS)',
            os
            )

    # Create activation keys, so systems can join the groups right away
    # Start with (POS) client hardware:
    for hw in scenario['Client_HW']:
        for role in ['POS Terminal', 'Branch Server']:
            groups = client.systemgroup.listAllGroups(org_key)
            for group in groups:
                if 'LOCATION' in group['name']:
                    g = group['name'][:-11]
                    short_g = g[:12]
                    try:
                        activationkey = client.activationkey.create(
                            org_key,
                            short_g + '_' + role + '_' + hw,
                            'Key to activate systems with role ' + role + ' from ' + hw + ' at location ' + g,
                            'sles12-sp3-pool-x86_64',
                            [],
                            False
                            )
                        for gg in groups:
                            if gg['name'] == hw + ' (CLIENT HARDWARE TYPE)':
                                hw_group = gg['id']
                            if gg['name'] == role + ' (ROLE)':
                                role_group = gg['id']
                            if gg['name'] == g + ' (LOCATION)':
                                location_group = gg['id']
                        client.activationkey.addServerGroups(
                            org_key,
                            activationkey,
                            [hw_group, role_group, location_group]
                            )
                        client.activationkey.addChildChannels(
                            org_key,
                            activationkey,
                            ['sle-manager-tools12-pool-x86_64-sp3',
                            'sle-manager-tools12-updates-x86_64-sp3',
                            'sles12-sp3-updates-x86_64'
                            ]
                            )
                    except xmlrpclib.Fault:
                        print("ERROR ERROR ERROR (usually duplicate cities)")

    client.auth.logout(org_key)
    no_of_countries+=1

client.auth.logout(key)
