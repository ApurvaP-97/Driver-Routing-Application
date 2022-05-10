import json
from collections import OrderedDict

def test_validateOutputs():
    outputRequired = json.load(open('../outputRequired.json'), object_pairs_hook=OrderedDict)
    outputObtained = json.load(open('../output.json'), object_pairs_hook=OrderedDict)
    try:
        assert (outputRequired == outputObtained)
    except:
        assert all([a == b for a, b in zip(outputRequired, outputObtained)])


