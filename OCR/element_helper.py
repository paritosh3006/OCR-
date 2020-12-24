# Check if an element is under the compared one and intersected based on its horizontal center position
def is_element_below(element, comparison_element):
    return element['l'] <= comparison_element['center_w'] and element['r'] >= comparison_element['center_w'] and element['t'] > comparison_element['t']


# Check if an element is to the right of the compared one and intersected with each other based on its vertical position
def is_to_the_right_of(element, comparison_element):
    return (element['b'] >= comparison_element['t'] and element['t'] <= comparison_element['b']) and element['l'] > comparison_element['r']

def get_direct_elements_below(candidates, element):
    # Assuming elements are considered as direct neighbour if it's within 20 units
    return list(filter(lambda e: e['t'] <= element['b'] + 20, candidates))
