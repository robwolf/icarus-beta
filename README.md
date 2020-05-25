
# Icarus Simulation Data Processing

## About

This repository is a collection of python scripts designed to prepare the MAG ABM dataset to be simulated in MATSim and analyze the results of said simulation with exposure data.

- [Installation](#installation)
- [Project Structure](#project-structure)
  - [Files](#files)
  - [Tables](#tables)
- [Running](#running)
  - [Dependencies](#dependencies)
  - [Processes](#processes)
- [Notes](#notes)

## Installation

This project is a python package and will require several other packages to function. I highly recommend using Anaconda to manage you python environments, and my instructions for installation will assume are doing so. First create an python 3.7 conda environment for the project and activate it:

```bash
conda create --name icarus python=3.7
conda activate icarus
```

Then you will need to install this project manually as a python package. Clone this repository using git and then install it using pip:

```bash
git clone https://github.com/ChesterIcarus/DataProcessing.git /path/to/save/repository
pip install /path/to/save/repository
```

If you intend to use the developmental build, you will want to download and checkout the `dev` branch of the repository before installing with pip. This branch will have the new updates, but not everything here is guarenteed to be stable.

```bash
git fetch
git checkout -t origin/dev
```

Lastly you will need to install all the dependent python packages. The pip dependencies are listed in `requirements.txt` and the conda dependencies need to be specified manually:

```bash
pip install -r /path/to/save/repository/requirements.txt
conda install -c conda-forge libspatialindex=1.9.3
```

You will also need to download [osmosis](https://github.com/openstreetmap/osmosis/releases/tag/0.48.0) and [pt2matsim](https://bintray.com/polettif/matsim/pt2matsim/) from their respective sources as well as the source data (daymet, MAG ABM, etc.) and the custom built 12-SNAPSHOT JAR of MATSim from the Dropbox.

## Project Structure

This package has a collection of scripts which can prepare simulation input data and analyze the output data. A given simulation run has a folder dedicated to it where the scripts to prepare and analyze the simulation data are executed from. All data relevant to the simulation will be saved in this directory according to structure of files and tables described below. This will make the project a bit more modular, but it will still need to access external source data and programs, which have to be specified in the project configuration file (more on that later).

A visual summary of the database structure can be found here on [dbdiagrams.io](https://dbdiagram.io/d/5e9e7ded39d18f5553fdef7e), but this link may not be regularly undated or maintained.

Here is a run down of the internal structure of a simulation run folder.

### Files

#### config.json

This is the project configuration file which describes how this simulation run is going to be prepared, executed and analyzed. All scripts will reference this config file to locate external source data and executeables as well as settings that tweak how it is run. A default configuration file has been provided in the root directory of this repository; all possible fields are already present in the default config, and with exception to file paths, no values should need to change to run a simulation under default settings.

THere is no section going over each setting in the project config file. instead, see each executeable script in the [process descriptions](#processes) for more details regarding relevant attributes of the config to the script.

#### database.db

This is the project database file which contains all the project data stored in a sqlite database. Previously we had used an SQL database for hosting our data, but technical issues with getting users access to the database lead to this more modular solution. Everything that the project uses, including intermediary data, is saved in this database, which can lead to it being quite large (typically between five and seven gigabytes). Of course, particular data of interest can be export as CSV or its own database at on request. Descriptions of all tables in this database are given below in the [tables](#tables) section.

#### config/

This folder includes additional configuration files used in some process (such as the network generation). This is partly a consequence of the fact that not all steps of data preparation are done entirely in house, so some external software needs to be run with special configuration files. Eventually these files will be generated temporarily form the information in the project configuration file, but only when time permits.

#### input/

This folder includes all the files needed to run a MATSim simulation. After the files have been generated, this file can be zipped an sent else where to handle the simulation. The only other thing needed to run the simulation is an installation of Java and the MATSim JAR.

#### output/

This folder includes all the files that the MATSim simulation spits out. The only important files to the data processing in the this project are the events, plans, vehicles, network, and logfile files. The iterations folder can be deleted in its entirity (and doing so save you enormous amounts of time and storage).

#### result/

This folder includes all visuals and summaries drawn from the project data. The actual contents of this folder may vary.

#### tmp/

This folder is where processes may save temporary files. Generally files are deleted after the process completes, so this folder will usually remain empty, but do not put any files in this directory since processes may overwrite them with no warning.

### Tables

#### trips

This table cooresponds exactly, without alteration, to the trip data delivered in the ABM trips csv file. See the ABM documentation for more details regarding fields in this table.

#### households

This table cooresponds exactly, without alteration, to the household data delivered in the ABM households csv file. See the ABM documentation for more details regarding fields in this table.

#### persons

This table cooresponds exactly, without alteration, to the person data delivered in the ABM trips csv file. See the ABM documentation for more details regarding fields in this table.

#### agents

This table links the input data of the simulation to the ABM data. All agents that are deemed valid under the conditions set by the population generation will be populated here. The new unique `agent_id` field can be used to connect agents to their activities and legs while the original `household_id` and `household_idx` fields can be used to link these agents back to the original persons in the ABM data.

| field         | schema             | description                                                                   |
|---------------|--------------------|-------------------------------------------------------------------------------|
| agent_id      | mediumint unsigned | uniquely identifying field                                                    |
| household_id  | mediumint unisnged | household identifier, linked to `hhid` in ABM tables                          |
| household_idx | smallint unsigned  | uniquely identifying field within a household, linked to `pnum` in ABM tables |
| plan_size     | tinyint unsigned   | total number of activities and legs                                           |
| uses_vehicle  | tinyint unsigned   | 1 if agent has a personal vehicle leg, 0 otherwise                            |
| uses_walk     | tinyint unsinged   | 1 if agent has a walking leg, 0 otherwise                                     |
| uses_bike     | tinyint unsinged   | 1 if agent has a biking leg, 0 otherwise                                      |
| uses_transit  | tinyint unsigned   | 1 if agent has a transit leg, 0 otherwise                                     |
| uses_party    | tinyint unsigned   | 1 if agent has a leg part of a party, 0 otherwise                             |

#### activities

Originally activities were described in the ABM trips table along with legs. After being parsed, assigned groups, filtered, cleaned and prepared, activities are extracted from trips and given a table of their own. Each activity has its own unique `activity_id`, but more useful are the `agent_id` and `agent_idx` fields, which link the activities to their respective agents in `agents`. The `group` field is a unique id that links together activities that needed to be assigned APNs together due to party restrictions; a group of zero means the activity was assigned an APN independent of all other activities.

Every agent will have a `plan_size` of `2n+1`, which will mean the agent has `n+1` activities in the `activities` table and `n` legs in the `legs` table. For a leg with `leg_idx` of `n`, the activity preceding the leg has an `activity_idx` of `n` and that proceding the leg has one of `n+1`.

| field       | schema             | description                                                      |
|-------------|--------------------|------------------------------------------------------------------|
| activtiy_id | mediumint unsigned | uniquely identifying field                                       |
| agent_id    | mediumint unisnged | agent identifier, linked to `agent_id` on `agents`               |
| agent_idx   | smallint unsigned  | uniquely identifying field within an agent, sequenced temporally |
| type        | varchar            | type of activity                                                 |
| apn         | varchar            | parcel identifier, linked to `apn` on `parcels`                  |
| group       | mediumint unsigned | APN spawning group identifier; 0 for no group                    |
| start       | mediumint unsigned | start time of activity in seconds from 00:00:00                  |
| end         | mediumint unsigned | end time of activity in seconds from 00:00:00                    |
| duration    | mediumint unsigned | duration of activity in seconds                                  |

#### legs

Originally legs were described in the ABM trips table along with activities. After being parsed, assigned parties, filtered, cleaned and prepared, legs are extracted from trips and given a table of their own. Each leg has its own unique `leg_id`, but more useful are the `leg_id` and `leg_idx` fields, which link the legs to their respective `agents`. The `party` field is a unique id that links together legs that are travelling together; a party of zero means a leg is travelled alone. See the activities cetion for more details regarding sequencing activities and legs.

| field     | schema             | description                                                      |
|-----------|--------------------|------------------------------------------------------------------|
| leg_id    | mediumint unsigned | uniquely identifying field                                       |
| agent_id  | mediumint unisnged | agent identifier, linked to `agent_id` on `agents`               |
| agent_idx | smallint unsigned  | uniquely identifying field within an agent, sequenced temporally |
| mode      | varchar            | leg mode type                                                    |
| party     | mediumint unsigned | APN spawning party identifier; 0 for no group                    |
| start     | mediumint unsigned | start time of leg in seconds from 00:00:00                       |
| end       | mediumint unsigned | end time of leg in seconds from 00:00:00                         |
| duration  | mediumint unsigned | duration of leg in seconds                                       |

#### regions

| field  | schema            | description                                     |
|--------|-------------------|-------------------------------------------------|
| maz    | smallint unsinged | micro analysis zone; uniquely identifying field |
| taz    | smallint unsigned | travel analysis zone; more broad than MAZ       |
| area   | float             | area in square miles of the region              |
| center | varchar           | WKT encoded point of the centroid of the region |
| region | text              | WKT encoded polygon of the region               |

#### centroids

| field          | schema             | description                                                        |
|----------------|--------------------|--------------------------------------------------------------------|
| centroid_id    | mediumint unsigned | uniquely identifying field                                         |
| temperature_id | mediumint unsigned | temperature profile for the centroid                               |
| center         | varchar            | WKT encoded point of the centroid                                  |
| region         | text               | WKT encoded polygon of the region to which the centroid is closest |

#### temperatures

| field           | schema             | description                                                          |
|-----------------|--------------------|----------------------------------------------------------------------|
| temperature_id  | mediumint unsigned | uniquely identifying field for a profile, not the table              |
| temperature_idx | tinyint unsigned   | the sequence index of the temperature of the temperature profile     |
| time            | mediumint unsigned | time of day of the temperature; cooresponds with the temperature_idx |
| temperature     | float              | temperature in degrees celcius                                       |

#### links

The `links` table expresses most the information that can be understood from the links in the MATSim network file (excluding relational data). Note that the `source_node` and `terminal_node` fields refer to the `node_id` field on the `nodes` table. The `link_id`s are mostly integers with exception to the artifical links created by the transit mapper in the network generation.

| field         | schema  | description                                          |
|---------------|---------|------------------------------------------------------|
| link_id       | varchar | uniquely identifying field                           |
| source_node   | varchar | the source node of the link                          |
| terminal_node | varchar | the terminal node of the link                        |
| length        | float   | length of the link in meters                         |
| freespeed     | float   | max speed of link in meters per second               |
| capacity      | float   | max occupancy of link                                |
| permlanes     | float   | number of lanes in link                              |
| oneway        | tinyint | 1 if the link contains only traffic in one direction |
| modes         | varchar | comma delimited list of allowed modes on link        |
| line          | varchar | WTK encoded linestring of the link geometry          |

#### nodes

The `nodes` table expresses most the information that can be understood from the nodes in the MATSim network file (excluding relational data). Note that the `maz` and `centroid_id` fields refer to the `maz` field on the `regions` table and the `centroid_id` field on the `centroids` table respectively. Like the `links` table, `node_id`s are mostly integers with exception to the artifical nodes created by the transit mapper in the network generation.

| field       | schema             | description                      |
|-------------|--------------------|----------------------------------|
| node_id     | varchar            | uniquely identifying field       |
| maz         | smallint unsigned  | the region that the node lies in |
| centroid_id | mediumint unsigned | the centroid closest to the node |
| point       | varchar            | WKT encoded point of the node    |

#### output_agents

| field     | schema             | description                                                            |
|-----------|--------------------|------------------------------------------------------------------------|
| agent_id  | mediumint unsigned | uniquely identifying field                                             |
| plan_size | tinyint unsigned   | total number of activities and legs                                    |
| exposure  | float              | total exposure the agent experienced in the simulation (4:00 to 31:00) |

#### output_activities

| field       | schema             | description                                                                      |
|-------------|--------------------|----------------------------------------------------------------------------------|
| activtiy_id | mediumint unsigned | uniquely identifying field                                                       |
| agent_id    | mediumint unisnged | agent identifier, linked to `agent_id` on `agents`                               |
| agent_idx   | smallint unsigned  | uniquely identifying field within an agent, sequenced temporally                 |
| type        | varchar            | type of activity                                                                 |
| link        | varchar            | link at which the activity occurred in simulation; linked to `link_id` on `links |
| start       | mediumint unsigned | start time of activity in seconds from 00:00:00                                  |
| end         | mediumint unsigned | end time of activity in seconds from 00:00:00                                    |
| duration    | mediumint unsigned | duration of activity in seconds                                                  |
| exposure    | float              | exposure experienced in the activity; null if exposure has not been analyzed     |

#### output_legs

| field     | schema             | description                                                        |
|-----------|--------------------|--------------------------------------------------------------------|
| leg_id    | mediumint unsigned | uniquely identifying field                                         |
| agent_id  | mediumint unisnged | agent identifier, linked to `agent_id` on `agents`                 |
| agent_idx | smallint unsigned  | uniquely identifying field within an agent, sequenced temporally   |
| mode      | varchar            | leg mode type                                                      |
| start     | mediumint unsigned | start time of leg in seconds from 00:00:00                         |
| end       | mediumint unsigned | end time of leg in seconds from 00:00:00                           |
| duration  | mediumint unsigned | duration of leg in seconds                                         |
| exposure  | float              | exposure experienced on leg; null if exposure analysis not run yet |

#### output_events

| field    | schema             | description                                                          |
|----------|--------------------|----------------------------------------------------------------------|
| event_id | mediumint unsigned | uniquely identifying field                                           |
| leg_id   | mediumint unisnged | leg identifier, linked to `leg_id` on `legs`                         |
| leg_idx  | smallint unsigned  | uniquely identifying field within a leg, sequenced temporally        |
| link_id  | varchar            | link that the event occurred on, linked to `link_id` on `links`      |
| start    | mediumint unsigned | start time of event in seconds from 00:00:00                         |
| end      | mediumint unsigned | end time of event in seconds from 00:00:00                           |
| duration | mediumint unsigned | duration of leg in seconds                                           |
| exposure | float              | exposure experienced on event; null if exposure analysis not run yet |

## Running

Once the repository has been installed using pip, various processes can be run using the following command structure:

```bash
    python -m icarus.[action].[item] [--folder /path/to/folder] [--log /path/to/logfile]
```

The `--folder` argument is used to specify the location of the folder that the run data is in; without it it is assumed that the working directory is the location of the data. If the folder in question is missing important data, the process will most likely fail. The `--log` argument will save the log printed to the terminal to the filepath specified. The log will still be printed, but it will also be copied to the specified file.

Most commands do not take additional arguements to control the nature of the process's execution. The project configuration file (see above in files) should have all the settings that can be set for each process.

### Dependencies

The rounded boxes represent processes, which have input (arrows pointing towards) and output (arrows pointing away) data. The squared boxes represent data, which can be an input to (arrows pointing away) and ouput of (arrows pointing towards) processes. Green and purple boxes represent python and java process respectively while red and blue boxes represent xml files and sql tables respectively.

![dependency diagram](https://github.com/ChesterIcarus/DataProcessing/blob/dev/docs/dependencies.png)

### Processes

#### parse daymet

The daymet data comes in pairs netCDF files, one containing the minimum temperatures for each day and the other containing the maximum values. While netCDF files are quite good at densely storing high dimensional data, they are not particularly efficient to iterate over or manipulate, so as usual, we parse the data into SQL tables. In this case, the we form two tables, `centroids` and `temperatures`, where the centroids are the locations of the measured temperatures and the temperatures are the temperature profiles at the centroids; see the table information for more details. Temperature profiles are generated by interpolating between the minimum and maximum temperatures for a single day under the assumption that the minimum temperature occurs around dawn (5:00) and the max temperature in early afternoon (15:00). The day to parse and the resolution of the interpolation can be chosen using the `day` and `step` options in the configuration file. Note that the daymet data is not particularly percise (only to the nearest half a degree celcius to my observation) and the regions are not particularly small, so many centroids have the same temperature profiles, which saves storage. The configuration file also has the options `tmax_files` and `tmin_files`, which should point to the netCDF files you wish to parse; these lists need to coorespond to each other respectively to be parsed correctly. Do not use any daymet tile other than the smallest tiles as large tiles become exponentially slower to iterate over and will contain much unneeded data. In my case, I was able to generously cover all of the greater Maricopa region with four small daymet tiles.

All geometries are transformed from the source CRS (epsg:4326) to this project's CRS (epsg:2223); the `epsg` setting in the project config file is ignored. You may have also noticed that a region is generated for each centroid despite the fact the netCDF data only specifies a single point for the temperatures. These regions are calculated using voronoi tesselations, filtering out polygons that exist outside the centroid limits. These regions encompass all the area to which each respective centroid is closest to; all points in this area will be considered the temperature of the centroid.

#### parse regions

Regions is an alias for the microanalysis zones (MAZs). MAZ and TAZ data comes packaged together in a shape/database file pair, which is parsed into an SQL table called `regions`; see table information for more details. The Maricopa MAZ an TAZ data is projected in epsg:2223, and the parser currently does not have any support for reprojection. This is one amoung many reasons that a different projection -- despite having an option in the project config -- for this project is not recommended.

#### parse abm

The MAG ABM data is delivered in a CSV format in three files: households, trips and persons. These files are read and loaded into the tables `households`, `trips` and `persons` respectively with almost no alteration. See the MAG ABM documnetation for more details regarding the ABM data.

#### generate network

The network that MATSim will simulate the population of Maricopa on is based on OpenStreeMap road data and ValleyMetro transit data. Make sure that you have both the OSM PBF for Arizona as well as the transit files from ValleyMetro downloaded and linked to in the project configuration file. However, a lot of processing has to occur before these can become valid input for the simulation. The `generate network` process will spawn `osmosis` and `pt2matsim` process to:

1. Generate configuration files for the network generation from the project config file.
2. Decompress PBF file into OSM file and trim the network to a specified region.
3. Generate a MATSim transit schedule from the ValleyMetro transit data.
4. Convert the OSM network into a MATSim XML mulitmodial network; configure the allowed modes on the XML network.
5. Map the transit schedule onto the XML network, tweaking the network with artificial links if needed.
6. Compress output file and delete itermediary/temporary files.

Make sure that the `osmosis` and `pt2matsim` fields in the project config accurately reflect the location of the binaries on your machine. The `schedule_dir` should point to the location of the VallyMetro data, and the `osm_file` should point to the location of the source PBF file from OpenStreetMap. The map is trimmed using the specified region in `region`, which is a list of WGS84 lat/lon coordinates with the first and last point coinsiding. The map will then be transformed to the epsg coordinate system specified in `epsg` (also specify "meters" or "feet" in `units` for the target coordinate system); the defualt is epsg:2223, which is centered over and optimized for Arizona. The `subnetworks` dictionary is the set of routable modes in the network mapped to the modes that each mode can be routed with. The `highways` and `railways` dictionaries map all the chosen link types to the sets of valid modes for each type. With exception to the file paths, most of these settings probably do not need to be altered.

The end result are the network, transit schedule and transit vehicles files in the input folder as well as three files in the config file. The latter are merely for reference and will not be used again by any other script.

As a word of warning, make sure that the resources in the `resources` option in the configuration file represent the maximmum resources you want processes to take at any given time. If these numbers are too large, some process may be allocated more memory than your system can afford, which can lead to crashes. While this is true anywhere, these processes are particularly resource intensive.

#### parse roads

After a network has been generated, it is useful to have the road information in an accessible format as we analyze agent movement and exposure across it. From the `input/network.xml.gz` file, the tables `links` and `nodes` are extracted; see table information for more details. While nodes and links are related in a rather obvious manner, nodes are also related to the regions and centroids spatially, which are calculated at this point. The parsed daymet and region data is loaded in before parsing the nodes, and the closest centroid and encompassing region is found as the nodes are parsed. Despite using an strtree spatial index, this process is quite computationally burdensome and can take upwards of a hour to do.

As a sidenote, I had this process running much faster using the spatial indexes built into MySQL, but some reason none of the tools available to python for spatial indexing seem to match the performance of MySQL, or I'm just not implementing them efficiently.

#### parse parcels

The county has information available regarding all the parcels in Maricopa county. These locations can be used in the simulation as locations that agents can travel between. Parcels can be either residential, commercial or other (which is really actually unknown), and a defualt fake parcel is generated for each region as failsafe for some operations. These are saved in the `parcels` table. Like the network, this data is stored in a pair of database/shape files, and the parcels parsed with the region data inorder to assign each parcel a region. Consequently, parcel parsing is also extremely slow for the same reasons, taking about two hours on my machine. Also like the road parsing, the Maricopa parcel data is delivered already projected in epsg:2223, and this tool does not implement any reprojection.

#### generate population

Before a simulation can be run, the ABM data needs to transformed into a population that can be written as MATSim input files. Population generate does several things:

1. Forms parties and groups from shared trips information.
2. Filters out trips and agents by conditions that user desires (particular modes or activity types).
3. Filters out trips and agents if they don't make sense to us (bad timing, unknown regions, no driver, etc.).
4. Filters out trips and agents if we deem the trip unrealistic to be made in simulation.
5. Filters out trips and agents recursively by party and group affiliation according the previous three conditions.
6. Assigns parcels to activities based on group affiliation.
7. Gives all valid activities, legs and agents unique identifcation numbers.

The desired modes and activity types can be specified using the `modes` and `activity_types` options in the configuration file. Experimentation has shown that there are very few trips that don't simply make sense; this was mostly needed for back when the ABM data had much less accurate timing. A trip is deemed unrealistic if the minimum speed of the trip -- shortest direct distance betweeen regions divided by the trip duration -- grossly exceeds the maximum speed for a mode of transport. These types of issues should also be a neglible amount of the data.

Each trip is broken into activities and legs, where activities are events happening beween legs or events of travel. Every leg is given a party and each group is given a group. If two trips are shared, meaning the ABM specifies that the agents are to travel together, the cooresponding legs are assigned to the same party, and the corresponding activities before and after the legs are assigned to the same groups. This allows parcels to be assigned to groups, which will automatically ensure that agents who are suppose to be travelling together are assigned the same locations.

As alluded to earlier, in order for an agent to be valid, all his modes and activitiy types must be a subset of those specified by the user, all regions of his activites must be a subset of the known regions, all his legs must have a reasonable minimum speed, and all parties of a vehiclular mode must have a driver. This logic is best summarized as such,

```python
def valid_party(party: Party) -> bool:
    return party.driver is not None or party.mode != RouteMode.CAR

def valid_leg(leg: Leg) -> bool:
    distance = network.minimum_distance(leg.party.origin_group.maz, leg.party.dest_group.maz)
    duration = leg.end - leg.start
    valid = False
    if duration > 0:
        valid = distance / duration < leg.mode.route_mode().max_speed()
    elif distance == 0:
        valid = True
    return valid

def valid_agent(agent: Agent) -> bool:
    return (agent.modes.issubset(modes)
        and agent.activity_types.issubset(activity_types)
        and agent.mazs.issubset(network.mazs)
        and all(valid_party(party) for party in agent.parties)
        and all(valid_leg(leg) for leg in agent.legs))
```

When an agent is invalid, all agents that are recursively dependent on the agnet need to be removed also. Dependednts are the agents who are part of parties in which the agent is the driver for. Theoretically, an agent being removed could set off a massive chain of dependent removals, but for the most part dependents tend to be young family members. The effect of recursively removing agents is only significant when modes are constricted considerably.

Households are assigned a single parcel, prefferable a residential parcel. Only once all parcels have been exhausted will multiple households be assigned the same parcel. All groups specified as home will use the agent's household parcel. All other groups are assigned a parcel randomly, prefferably a commercial parcel. When a region contains no residential parcels, households are assigned commercial parcels randomly. When a region contains no commercial regions, groups are assigned residential parcels randomly. Other and default parcels are used a last resort in the case of both conditions.

#### generate plans

After a population has been generated, a plans file needs to be generated, which will become an important par to of the input to the MATSim simulation. Because the population generation organized trips into `activities` and `legs`, which is how MATSim organizes plans, this process is quite simple. All that needs to be done is to pull the data from the tables, refactor some naming, and add any changes to virtualized/teleported modes. Plans generation also has options for choosing a sample of population; these options can be found in the `sample` section of the configuration file. The `sample_size` option will select at most that many agents if specified while the `sample_percent` will select at least that proportion of the agents of the population. If both are specified, the minimum value will be used. The other options refer to the columns on the `agents` table. If "true" is specified, then only agents with this attribute will be selected, while if "false" is specified only agents without this attribute are selected. Otherwise ("null" or unspecified), agents will be selected regardless of this attribute. All attribute selections are conjunctive. If you need a more specific type of population selection, you will need to modify the source code.

The chosen plans are formatted to the MATSim [plans file specifications (v4)](http://www.matsim.org/files/dtd/plans_v4.dtd) and then saved to `input/plans.xml.gz`.

#### generate config

This is not implemented yet. For now you will need to copy a provided MATSim configuration file and modify it accordingly when the JSON configuration file used by all the other modules.

#### simulation

Assuming that all the dendencies for the simulation have been met, the simulation can be run by,

```bash
java -Xms32G -Xmx64G \
    -cp /path/to/matsim/jar \
    org.matsim.run.Controler /path/to/matsim/config
```

Note the they demanded resources in the first line can vary based on the size of the simulation being run, but should never be specified higher than what the machine/instance running can provide (this can lead to crashes).

The simulation runs well if you have the following file structure,

```files
run_xx_xx_xx/
    input/
        config.xml
        network.xml.gz
        plan.xml.gz
        transitSchedule.xml.gz
        transitVehicles.xml.gz
        vehicles.xml.gz
    output/
```

where the output directory will be where the simulation outputs the simulation results (assuming that the simulation is started from this working directory). You will notice that this reflects the project structure well, so the simulation can be run from the project directory with ease. If the simulation is run elsewhere, just zip the input folder and bring it along with the MATSim JAR. If you change the file structure, you may need to modify the paths in the XML config file so the simulation can find the input data.

Note that unless you are debuging the simulation with it, `output/ITERS/` can be deleted. This folder can be very large, especially if the simulatin was run for many iterations, so deleting it can save a lot of space and transfer time.

#### parse events

Once the simulation data has been obtained, it now has to be parsed and imported back into the database. The `output_plans` file contains all the legs and activities of the agents in the simulation much like the input plans file, but none of the timing of the plans file is accurate and it does not include link level timing. This is why the `output_events` file, which is a massive document of all the events that occured in the entirity of the simulation needs to be iterated and parsed. Parsing events will use both these files and information from the database in the following process:

1. Load the network data in from the database.
2. Load the routing data in from the output_plans file.
3. Load in the identifiers for activities and legs from the database.
4. Iterate over the events and parse activities, legs and events from the data.
5. Push the results back to the database.

The fourth step is expensive as the events file is enormous and a lot of data is being extracted from it. Consequently, the events parsing will frequently pause and export any compleeted legs, activities and events to the database to save memory in the parsing process. It may take a while to parse the simulation, but the log should keep you updated on its process. There are also some complicated things occuring in the handling of virtualized, vehicular and transit legs (if enabled), as well as some mode refactoring. The results are saved in `output_agents`, `output_legs`, `output_activities` and `output_events`; see the table descriptions for more details. You will notice that these tables mirror the corresponding input tables witgh exception to the events; there are no input events, the name was simple chosen for consistency.

#### analyze exposure

The exposure analysis tool uses the daymet temperature data and the results of the simulation to calculate agent exposure at an event level, when possible. If event level data is not available for a particular route, the temperature at the link of the starting activity is used. Some travel is air conditioned, so indoor temperatures are used for exposure. The exposure analysis tool will load the network data from database and then iteratively calculate the exposure for each agent in batches of 100k agents. Since the events and exposure parsing tools have already done most of the heavy lifting in parsing, the exposure tool is actually quite quick.

Results are saved back to the original output tables. Since updates in SQL are slow, it is actually much faster to create new temporary tables, drop the old ones and rename the new ones. The only side affect of this is that sqlite may change the schema slightly to reflect the simplified sqlite typing; this will have no fucntional affect on the database, and it can be readily changed if it is an issue.

## Notes

### Running in Restrictive Environments

If you need to run some of the python processes in a shared, restricted environment (such as the Agave servers), there is a good chance that you are not allowed to install software, which includes python packages. Since this project is run as a package itself, this can be problematic. The [stickytape](https://github.com/mwilliamson/stickytape) utility can be useful here to generate standalone scripts of modules that can be run as a single file instead of a set of interacting packages.

Also, note that the current project is running as python 3.7, which is a relatively new version of python that may not be available in other environments. The project can be made compatible with python 3.6 by removing all usages of `__futures__` imports and all typing of classes to themselves (which will only occur in files with mentioned import). I have chosen to use this feature despite its compatibility issues with older python versions since I think typing provides clarity to code.

Let me know if you need any help with the items described above or if you need help trying to get the scripts to work under other restrictions.

### Temporary Tables

Some modules create temporary tables in the process of manipulating data. These tables will have names prefixed with `temp_`. It would be best to avoid naming your own tables in the database with names of this format as these tables will be created and dropped without propting the user. Also, while processes usually cleanup their temporary tables, there is a chance that some remain if a process is cancelled or fails. Since all temporary tables are only relevant within a single process, these tables can deleted with no consequence.

### Minimizing Storage

A fullscale simulation processed from start to finish can be upwards of 7GB, not including the source data. If you have deleted large tables, you can benefit greatly by running the `vacuum` command on the database file, which will copy the database back into itself, removing unused space. Note that when it comes to compression, only the database can be significantly compressed (by a factor of a third); the remaining files are either already stored in a compressed format or too small to be considered significant in terms of storage.
