#Information about paragraphs and also convert some value to integer to make it easier to calculate later
def feature_enrichment_paragraphs(pars):
    paragraphs = []
    for p in pars:
        chunks = []
        for s in p.findAll('span'):
            chunks.append(s.text)
        text = ''.join(chunks)
        if p.get('baseline'):
            paragraphs.append({
                'text': text,
                # Convert it to integer
                'baseline': int(p['baseline']),
                'l': int(p['l']),
                # Get the center position horizontally
                'center_w': (int(p['r']) + int(p['l'])) / 2,
                'center_h': (int(p['b']) + int(p['t'])) / 2,
                'r': int(p['r']),
                'b': int(p['b']),
                't': int(p['t'])
            })

    return paragraphs


# Assuming statement is mailed, hence receiver information should be on the top-left corner
def get_left_top_quarter_paragraphs(page):
    paragraphs = []
    boundary = {
        'center_w': int(page['width']) / 2,  # Boundary to get the left part
        # Boundary to get the top-third part
        'center_h': int(page['height']) / 3
    }

    for p in page.findAll('p'):
        chunks = []
        for s in p.findAll('span'):
            chunks.append(s.text)
        text = ''.join(chunks)
        # Only consider if it's inside the boundary
        if p.get('baseline') and int(p['r']) <= boundary['center_w'] and int(p['b']) <= boundary['center_h']:
            paragraphs.append({
                'text': text,
                'baseline': int(p['baseline']),
                'l': int(p['l']),
                'center_w': (int(p['r']) + int(p['l'])) / 2,
                'center_h': (int(p['b']) + int(p['t'])) / 2,
                'r': int(p['r']),
                'b': int(p['b']),
                't': int(p['t'])
            })

    return paragraphs
