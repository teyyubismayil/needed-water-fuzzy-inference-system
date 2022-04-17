import re

air_temperature_variables = ['cold', 'warm', 'hot']
soil_moisture_variables = ['dry', 'medium', 'wet']
needed_water_variables = ['little', 'medium', 'much']

fuzzy_rules = [
    'IF air_temperature IS cold OR soil_moisture IS wet THEN needed_water IS little',
    'IF air_temperature IS hot OR soil_moisture IS dry THEN needed_water IS much',
    'IF air_temperature IS warm AND soil_moisture IS medium THEN needed_water IS medium'
]

def fuzzify_air_temperature(air_temperature_cv):
    cold_fv = 1 - min(max((air_temperature_cv - 0) / 15, 0), 1)
    warm_fv = 1 - min(abs((air_temperature_cv - 15) / 15), 1)
    hot_fv = 1 - min(max((30 - air_temperature_cv) / 15, 0), 1)
    return [cold_fv, warm_fv, hot_fv]

def fuzzify_soil_moisture(soil_moisture_cv):
    dry_fv = 1 - min(max((soil_moisture_cv - 25) / 25, 0), 1)
    medium_fv = 1 - min(abs((soil_moisture_cv - 50) / 25), 1)
    wet_fv = 1 - min(max((75 - soil_moisture_cv) / 25, 0), 1)
    return [dry_fv, medium_fv, wet_fv]

def get_value_from_if_rule(air_temperature_fv, soil_moisture_fv, if_rule):
    if_parts = if_rule.split(' IS ')
    if if_parts[0] == 'air_temperature':
        return air_temperature_fv[air_temperature_variables.index(if_parts[1])]
    elif if_parts[0] == 'soil_moisture':
        return soil_moisture_fv[soil_moisture_variables.index(if_parts[1])]
    else:
        raise ValueError('Unsupported type of if rule.')

def add_value_to_inference(needed_water_fv, needed_water_variable, value):
    ind = needed_water_variables.index(needed_water_variable)
    if needed_water_fv[ind] == None:
        needed_water_fv[ind] = value
    else:
        needed_water_fv[ind] = min(needed_water_fv[ind], value)

def infer_needed_water(air_temperature_fv, soil_moisture_fv):
    needed_water_fv = [None] * len(needed_water_variables)
    for rule in fuzzy_rules:
        rule_splitted = rule.split(' THEN ')
        rule_if = rule_splitted[0][3:]
        rule_then = rule_splitted[1]
        rule_variable = rule_then.split(' IS ')[1]
        if_parts = re.split(' AND | OR ', rule_if)
        if len(if_parts) == 1:
            add_value_to_inference(
                needed_water_fv, 
                rule_variable, 
                get_value_from_if_rule(air_temperature_fv, soil_moisture_fv, if_parts[0])
            )
        elif len(if_parts) == 2:
            val1 = get_value_from_if_rule(air_temperature_fv, soil_moisture_fv, if_parts[0])
            val2 = get_value_from_if_rule(air_temperature_fv, soil_moisture_fv, if_parts[1])
            if ' AND ' in rule_if:
                add_value_to_inference(
                    needed_water_fv, 
                    rule_variable, 
                    min(val1, val2)
                )
            elif ' OR ' in rule_if:
                add_value_to_inference(
                    needed_water_fv, 
                    rule_variable, 
                    max(val1, val2)
                )
        else:
            raise ValueError('Unsupported type of if rule.')
    return needed_water_fv

# points are in form of [[x1, x2, ...], [y1, y2, ...]]
# returns (x, y)
def centroid(points):
    return (sum(points[0])/len(points[0]),sum(points[1])/len(points[1]))

# uses weighted average method
def defuzzify_needed_water(needed_water_fv):
    centroids_x = [0, 0, 0]
    # little
    if needed_water_fv[0] != 0:
        little_ipx = 25 + (1 - needed_water_fv[0]) * 25
        little_points = [[0, 0, little_ipx, 50],[0, needed_water_fv[0], needed_water_fv[0], 0]]
        #print('little_points: ', little_points)
        little_centroid = centroid(little_points)
        centroids_x[0] = little_centroid[0]
    
    # medium
    if needed_water_fv[1] == 1:
        medium_points = [[25, 50, 75],[0, 1, 0]]
        #print('medium_points: ', medium_points)
        medium_centroid = centroid(medium_points)
        centroids_x[1] = medium_centroid[0]
    elif needed_water_fv[1] != 0:
        medium_ipx1 = 50 - (1 - needed_water_fv[1]) * 25
        medium_ipx2 = 50 + (1 - needed_water_fv[1]) * 25
        medium_points = [[25, medium_ipx1, medium_ipx2, 75],[0, needed_water_fv[1], needed_water_fv[1], 0]]
        #print('medium_points: ', medium_points)
        medium_centroid = centroid(medium_points)
        centroids_x[1] = medium_centroid[0]

    # much
    if needed_water_fv[2] != 0:
        much_ipx = 75 - (1 - needed_water_fv[2]) * 25
        much_points = [[50, much_ipx, 100, 100],[0, needed_water_fv[2], needed_water_fv[2], 0]]
        #print('much_points: ', much_points)
        much_centroid = centroid(much_points)
        centroids_x[2] = much_centroid[0]
    
    #print('centroids_x: ', centroids_x)
    return sum(centroids_x) / sum(needed_water_fv)

# Input
air_temperature_crisp_value = int(input('Input air temperature: '))
soil_moisture_crisp_value = int(input('Input soil moisture: '))
if soil_moisture_crisp_value < 0 or soil_moisture_crisp_value > 100:
    raise ValueError('Invalid soil moisture value.')

# Fuzzification
air_temperature_fuzzy_value = fuzzify_air_temperature(air_temperature_crisp_value)
soil_moisture_fuzzy_value = fuzzify_soil_moisture(soil_moisture_crisp_value)

print('air_temperature_fuzzy_value: ', air_temperature_fuzzy_value)
print('soil_moisture_fuzzy_value: ', soil_moisture_fuzzy_value)

# Inference
needed_water_fuzzy_value = infer_needed_water(air_temperature_fuzzy_value, soil_moisture_fuzzy_value)
print('needed_water_fuzzy_value: ', needed_water_fuzzy_value)

# Defuzzification
needed_water_crisp_value = defuzzify_needed_water(needed_water_fuzzy_value)
print('needed_water_crisp_value: ', needed_water_crisp_value)
