import itertools
import os
import gzip
import xml.etree.ElementTree as ET
import requests

save_as_gz = True  # Set to True to save an additional .gz version

#output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'epg.xml')
output_file = 'epg.xml'
output_file_gz = '../' + output_file + '.gz'

epgUrls = [
        'https://epgshare01.online/epgshare01/epg_ripper_US2.xml.gz',
        'https://epgshare01.online/epgshare01/epg_ripper_US_LOCALS2.xml.gz',
        'https://epgshare01.online/epgshare01/epg_ripper_CA1.xml.gz',
        'https://epgshare01.online/epgshare01/epg_ripper_UK1.xml.gz',
        'https://epgshare01.online/epgshare01/epg_ripper_DE1.xml.gz',
        'https://michaz1988.github.io/guide.xml.gz',
        'https://i.mjh.nz/PlutoTV/us.xml.gz',
        'https://i.mjh.nz/PlutoTV/ca.xml.gz',
        'https://i.mjh.nz/PlutoTV/de.xml.gz'
]

usaGroup_file = os.path.join(os.path.dirname(__file__), 'Channels/USA2Channels.txt')
with open(usaGroup_file, 'r', encoding='utf-8') as usaGroupfile:
    usaGroup = list(line.strip() for line in usaGroupfile)

ukGroup_file = os.path.join(os.path.dirname(__file__), 'Channels/UKChannels.txt')
with open(ukGroup_file, 'r', encoding='utf-8') as ukGroupfile:
    ukGroup = list(line.strip() for line in ukGroupfile)

canadaGroup_file = os.path.join(os.path.dirname(__file__), 'Channels/CanadaChannels.txt')
with open(canadaGroup_file, 'r', encoding='utf-8') as canadaGroupfile:
    canadaGroup = list(line.strip() for line in canadaGroupfile)

germanGroup_file = os.path.join(os.path.dirname(__file__), 'Channels/GermanChannels.txt')
with open(germanGroup_file, 'r', encoding='utf-8') as germanGroupfile:
    germanGroup = list(line.strip() for line in germanGroupfile)

michazGroup_file = os.path.join(os.path.dirname(__file__), 'Channels/MichazChannelsGitHub.txt')
with open(michazGroup_file, 'r', encoding='utf-8') as michazGroupfile:
    michazGroup = list(line.strip() for line in michazGroupfile)

plutoTvGermanGroup_file = os.path.join(os.path.dirname(__file__), 'Channels/PlutoTVGerman.txt')
with open(plutoTvGermanGroup_file, 'r', encoding='utf-8') as plutoTvGermanGroupfile:
    plutoTvGermanGroup = list(line.strip() for line in plutoTvGermanGroupfile)

plutoTvUSAGroup_file = os.path.join(os.path.dirname(__file__), 'Channels/PlutoTVUSA.txt')
with open(plutoTvUSAGroup_file, 'r', encoding='utf-8') as plutoTvUSAGroupfile:
    plutoTvUSAGroup = list(line.strip() for line in plutoTvUSAGroupfile)

def fetch_and_extract_xml(url):
    print(f"Downloading {url}.")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return None

    if url.endswith('.gz'):
        try:
            print(f"Downloaded successfully")
            decompressed_data = gzip.decompress(response.content)
            return ET.fromstring(decompressed_data)
        except Exception as e:
            print(f"Failed to decompress and parse XML from {url}: {e}")
            return None
    else:
        try:
            print(f"Downloaded successfully")
            return ET.fromstring(response.content)
        except Exception as e:
            print(f"Failed to parse XML from {url}: {e}")
            return None

def filter_and_build_epg(urls):
    valid_tvg_channels = set()

    for usa in usaGroup:
        occurenceIndex = len(tuple(itertools.takewhile(lambda x: usa not in x, usaGroup)))
        valid_tvg_channels.add(usaGroup[occurenceIndex].split()[-1])
    for uk in ukGroup:
        occurenceIndex = len(tuple(itertools.takewhile(lambda x: uk not in x, ukGroup)))
        valid_tvg_channels.add(ukGroup[occurenceIndex].split()[-1])
    for canada in canadaGroup:
        occurenceIndex = len(tuple(itertools.takewhile(lambda x: canada not in x, canadaGroup)))
        valid_tvg_channels.add(canadaGroup[occurenceIndex].split()[-1])
    for german in germanGroup:
        occurenceIndex = len(tuple(itertools.takewhile(lambda x: german not in x, germanGroup)))
        valid_tvg_channels.add(germanGroup[occurenceIndex].split()[-1])
    for michaz in michazGroup:
        occurenceIndex = len(tuple(itertools.takewhile(lambda x: michaz not in x, michazGroup)))
        valid_tvg_channels.add(michazGroup[occurenceIndex])
    for plutoTvGerman in plutoTvGermanGroup:
        occurenceIndex = len(tuple(itertools.takewhile(lambda x: plutoTvGerman not in x, plutoTvGermanGroup)))
        valid_tvg_channels.add(plutoTvGermanGroup[occurenceIndex])
    for plutoTvUSA in plutoTvUSAGroup:
        occurenceIndex = len(tuple(itertools.takewhile(lambda x: plutoTvUSA not in x, plutoTvUSAGroup)))
        valid_tvg_channels.add(plutoTvUSAGroup[occurenceIndex])

    root = ET.Element('tv')

    for url in urls:
        epg_data = fetch_and_extract_xml(url)
        if epg_data is None:
            continue

        for channel in epg_data.findall('channel'):
            tvg_id = channel.get('id')
            if tvg_id in valid_tvg_channels:
                root.append(channel)

        for programme in epg_data.findall('programme'):
            tvg_id = programme.get('channel')
            if tvg_id in valid_tvg_channels:
                title = programme.find('title').text
                root.append(programme)

    tree = ET.ElementTree(root)
    # tree.write(output_file, encoding='utf-8', xml_declaration=True)
    # print(f"New EPG saved to {output_file}")

    if save_as_gz:
        with gzip.open(output_file_gz, 'wb') as f:
            tree.write(f, encoding='utf-8', xml_declaration=True)
        print(f"New EPG saved to {output_file_gz}")


print("Downloading and creating EPG.")
filter_and_build_epg(epgUrls)
